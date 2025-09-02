import logging
from typing import Dict, Any, Tuple, Optional, List, Union

import stripe
from .client import ParmotClient

logger = logging.getLogger(__name__)


def create_stripe_checkout_session(
    price_id: str,
    end_user_id: str,
    parmot_plan_name: str,
    success_url: str,
    cancel_url: str,
    parmot_fallback_plan_name: Optional[str] = None,
    customer_id: Optional[str] = None,
    trial_period_days: Optional[int] = None,
    allow_promotion_codes: bool = False,
    billing_address_collection: str = "auto",
    payment_method_types: Optional[List[str]] = None,
    locale: str = "auto",
    metadata: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Create a Stripe Checkout Session with proper Parmot metadata for automatic plan management.

    This helper function creates a Stripe checkout session with all the required metadata
    for Parmot's automatic plan management via webhooks.
    """

    # Prepare metadata with Parmot-required fields
    session_metadata: Dict[str, str] = {
        "end_user_id": end_user_id,
        "parmot_plan_name": parmot_plan_name,
    }

    if parmot_fallback_plan_name:
        session_metadata["parmot_fallback_plan_name"] = parmot_fallback_plan_name

    # Merge with any additional metadata provided
    if metadata:
        session_metadata.update(metadata)

    # Prepare subscription metadata (same as session metadata for consistency)
    subscription_metadata: Dict[str, str] = session_metadata.copy()

    # Set default payment method types if not provided
    if payment_method_types is None:
        payment_method_types = ["card"]

    # Build checkout session parameters
    checkout_params: Dict[str, Any] = {
        "mode": "subscription",
        "payment_method_types": payment_method_types,
        "line_items": [
            {
                "price": price_id,
                "quantity": 1,
            }
        ],
        "success_url": success_url,
        "cancel_url": cancel_url,
        "metadata": session_metadata,
        "subscription_data": {
            "metadata": subscription_metadata,
        },
        "allow_promotion_codes": allow_promotion_codes,
        "billing_address_collection": billing_address_collection,
        "locale": locale,
    }

    # Add optional parameters
    if customer_id:
        checkout_params["customer"] = customer_id

    if trial_period_days:
        checkout_params["subscription_data"]["trial_period_days"] = trial_period_days

    checkout_session = stripe.checkout.Session.create(**checkout_params)
    logger.info(
        f"Created Stripe checkout session {checkout_session.id} for end user {end_user_id} "
        f"with plan {parmot_plan_name}"
    )
    return {
        "url": checkout_session.url,
        "id": checkout_session.id,
        "session": checkout_session,
    }


def handle_stripe_event(
    stripe_event: Dict[str, Any],
    parmot_client: ParmotClient,
    fallback_plan_name: str = "Free",
) -> Tuple[str, int]:
    """
    Handle Stripe webhook events and automatically manage Parmot end user plans.

    This function processes Stripe webhook events and automatically assigns end users
    to appropriate Parmot plans based on their payment status and subscription metadata.
    """

    event_type: str = stripe_event.get("type", "")

    # Handle only relevant events
    if event_type not in [
        "invoice.payment_succeeded",
        "invoice.payment_failed",
        "customer.subscription.deleted",
        "customer.subscription.updated",
    ]:
        logger.info(f"Unhandled Stripe event type: {event_type}")
        return "Event type not handled", 200

    # Extract data from event
    event_data: Dict[str, Any] = stripe_event.get("data", {}).get("object", {})
    # Get subscription data based on event type
    subscription_data: Dict[str, Any]
    if event_type.startswith("customer.subscription."):
        # For subscription events, the object is the subscription itself
        subscription_data = event_data
    else:
        # For invoice events, we need to get subscription from the invoice
        subscription_id: Optional[str] = event_data.get("subscription")
        if not subscription_id:
            logger.warning(f"No subscription ID found in {event_type} event")
            return "No subscription ID in event", 400
        # Retrieve full subscription to get metadata
        subscription_obj = stripe.Subscription.retrieve(subscription_id)
        # Convert to dict-like structure for consistent access
        subscription_data = {
            "id": subscription_obj.id,
            "status": subscription_obj.status,
            "metadata": (
                dict(subscription_obj.metadata) if subscription_obj.metadata else {}
            ),
        }
    # Extract metadata
    metadata: Dict[str, str] = subscription_data.get("metadata", {})
    end_user_id: Optional[str] = metadata.get("end_user_id")
    parmot_plan_name: Optional[str] = metadata.get("parmot_plan_name")
    parmot_fallback_plan_name: Optional[str] = metadata.get("parmot_fallback_plan_name")
    if not end_user_id:
        logger.warning(
            f"No end_user_id in subscription metadata for event {event_type}"
        )
        return "No end_user_id in subscription metadata", 400
    if not parmot_plan_name:
        logger.warning(
            f"No parmot_plan_name in subscription metadata for event {event_type}"
        )
        return "No parmot_plan_name in subscription metadata", 400
    # Determine which plan to assign based on event type
    target_plan: str
    action: str
    if event_type == "invoice.payment_succeeded":
        target_plan = parmot_plan_name
        action = "payment success"
    elif event_type == "invoice.payment_failed":
        target_plan = parmot_fallback_plan_name or fallback_plan_name
        action = "payment failure"
    elif event_type == "customer.subscription.deleted":
        target_plan = parmot_fallback_plan_name or fallback_plan_name
        action = "subscription deletion"
    elif event_type == "customer.subscription.updated":
        # Check subscription status to determine plan
        status: Optional[str] = subscription_data.get("status")
        if status in ["active", "trialing"]:
            target_plan = parmot_plan_name
        else:
            target_plan = parmot_fallback_plan_name or fallback_plan_name
        action = f"subscription update (status: {status})"
    else:
        # This shouldn't happen due to our earlier check, but just in case
        return "Unexpected event type", 400
    # Assign user to the determined plan
    success: bool = parmot_client.assign_end_user_to_plan(end_user_id, target_plan)
    if success:
        logger.info(f"Assigned user {end_user_id} to plan {target_plan} after {action}")
        return f"User assigned to {target_plan} plan", 200
    else:
        logger.error(
            f"Failed to assign user {end_user_id} to plan {target_plan} after {action}"
        )
        return f"Failed to assign user to {target_plan} plan", 500
