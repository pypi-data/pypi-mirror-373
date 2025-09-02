import requests
import os
import logging
import stripe
from typing import Optional, Dict, Any, List, Tuple
from .usage import (
    ParmotUsageLimitError,
    ParmotEndUserUsageLimitError,
    ParmotEndUserRateLimitError,
    ParmotAPIError,
    ParmotNotFoundError,
    ParmotValidationError,
)
from .schemas import (
    EndUserUsageSummary,
    EndUserPlanInfo,
    CreateEndUserPlanRequest,
    UpdateEndUserPlanRequest,
    CreateEndUserPlanResponse,
)

logger = logging.getLogger(__name__)


class ParmotClient:
    def __init__(
        self, api_key: Optional[str] = None, api_base_url: Optional[str] = None
    ):
        determined_api_key = api_key or os.getenv("PARMOT_API_KEY")
        if not determined_api_key:
            raise ValueError(
                "PARMOT_API_KEY must be provided either as parameter or environment variable"
            )
        self.api_key: str = determined_api_key

        self.api_base_url = api_base_url or os.getenv(
            "PARMOT_API_BASE_URL", "https://parmotbackend-production.up.railway.app"
        )

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 10,
    ) -> requests.Response:
        url = f"{self.api_base_url}{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=json_data,
                params=params,
                timeout=timeout,
            )
            return response
        except requests.RequestException as e:
            logger.error(f"Error making {method} request to {endpoint}: {str(e)}")
            raise ParmotAPIError(f"Network error: {str(e)}", 0)

    def _handle_response_errors(self, response: requests.Response) -> None:
        """Handle common HTTP error responses and raise appropriate exceptions"""
        if response.status_code < 400:
            return

        try:
            error_data = response.json()
            error_message = error_data.get(
                "error", f"HTTP {response.status_code} error"
            )
        except:
            error_message = f"HTTP {response.status_code} error"
            error_data = None

        if response.status_code == 400:
            raise ParmotValidationError(error_message)
        elif response.status_code == 404:
            raise ParmotNotFoundError(error_message)
        elif response.status_code == 429:
            # Rate limit error
            if error_data and "retry_after" in error_data:
                raise ParmotEndUserRateLimitError(
                    error_data["error"],
                    error_data.get("current_rate", 0),
                    error_data.get("limit", 0),
                    error_data.get("window", "unknown"),
                    error_data.get("retry_after", 60),
                )
            else:
                raise ParmotEndUserRateLimitError(error_message, 0, 0, "unknown", 60)
        elif response.status_code == 402:
            # Check if this is an end user limit error (has additional fields)
            if error_data and "current_usage" in error_data and "limit" in error_data:
                raise ParmotEndUserUsageLimitError(
                    error_data["error"],
                    error_data["current_usage"],
                    error_data["limit"],
                    error_data.get("limit_type", "unknown"),
                )
            else:
                # This is a Parmot user limit error
                raise ParmotUsageLimitError(error_message)
        else:
            raise ParmotAPIError(error_message, response.status_code)

    def check_end_user_usage_limits(self, end_user_id: str) -> bool:
        """Check if end user is currently over their limits"""
        payload = {"end_user_id": end_user_id}

        response = self.request(
            "POST", "/api/end-user-usage/check-limits", json_data=payload
        )

        if response.status_code == 200:
            return True

        self._handle_response_errors(response)
        return False

    def get_end_user_usage_summary(
        self, end_user_id: Optional[str] = None
    ) -> EndUserUsageSummary:
        params = {}
        if end_user_id:
            params["end_user_id"] = end_user_id

        response = self.request("GET", "/api/end-user-usage/summary", params=params)
        self._handle_response_errors(response)
        data = response.json()

        return EndUserUsageSummary(
            end_user_id=data.get("end_user_id"),
            total_requests=data["total_requests"],
            total_cost=data["total_cost"],
            total_tokens=data["total_tokens"],
            total_prompt_tokens=data["total_prompt_tokens"],
            total_completion_tokens=data["total_completion_tokens"],
            current_month_requests=data["current_month_requests"],
            current_month_cost=data["current_month_cost"],
            current_month_tokens=data["current_month_tokens"],
        )

    def create_end_user_plan(
        self,
        name: str,
        monthly_token_limit: Optional[int] = None,
        monthly_cost_limit: Optional[float] = None,
        rate_limit_per_minute: Optional[int] = None,
        rate_limit_per_hour: Optional[int] = None,
        rate_limit_per_day: Optional[int] = None,
        description: Optional[str] = None,
    ) -> CreateEndUserPlanResponse:
        request_data = CreateEndUserPlanRequest(
            name=name,
            monthly_token_limit=monthly_token_limit,
            monthly_cost_limit=monthly_cost_limit,
            rate_limit_per_minute=rate_limit_per_minute,
            rate_limit_per_hour=rate_limit_per_hour,
            rate_limit_per_day=rate_limit_per_day,
            description=description,
        )

        payload = {
            "name": request_data.name,
            "monthly_token_limit": request_data.monthly_token_limit,
            "monthly_cost_limit": request_data.monthly_cost_limit,
            "rate_limit_per_minute": request_data.rate_limit_per_minute,
            "rate_limit_per_hour": request_data.rate_limit_per_hour,
            "rate_limit_per_day": request_data.rate_limit_per_day,
            "description": request_data.description,
        }

        response = self.request("POST", "/api/end-user-plans", json_data=payload)
        self._handle_response_errors(response)
        data = response.json()
        return CreateEndUserPlanResponse(plan_id=data["plan_id"])

    def get_end_user_plan(self, name: str) -> Optional[EndUserPlanInfo]:
        response = self.request("GET", f"/api/end-user-plans/{name}")

        if response.status_code == 404:
            return None

        self._handle_response_errors(response)
        data = response.json()

        return EndUserPlanInfo(
            id=data["id"],
            name=data["name"],
            monthly_token_limit=data.get("monthly_token_limit"),
            monthly_cost_limit=data.get("monthly_cost_limit"),
            rate_limit_per_minute=data.get("rate_limit_per_minute"),
            rate_limit_per_hour=data.get("rate_limit_per_hour"),
            rate_limit_per_day=data.get("rate_limit_per_day"),
            description=data.get("description"),
            is_active=data["is_active"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )

    def get_all_end_user_plans(self) -> List[EndUserPlanInfo]:
        response = self.request("GET", "/api/end-user-plans")
        self._handle_response_errors(response)
        data = response.json()

        plans_data = data.get("plans", [])
        return [
            EndUserPlanInfo(
                id=plan["id"],
                name=plan["name"],
                monthly_token_limit=plan.get("monthly_token_limit"),
                monthly_cost_limit=plan.get("monthly_cost_limit"),
                rate_limit_per_minute=plan.get("rate_limit_per_minute"),
                rate_limit_per_hour=plan.get("rate_limit_per_hour"),
                rate_limit_per_day=plan.get("rate_limit_per_day"),
                description=plan.get("description"),
                is_active=plan["is_active"],
                created_at=plan["created_at"],
                updated_at=plan["updated_at"],
            )
            for plan in plans_data
        ]

    def update_end_user_plan(
        self,
        name: str,
        monthly_token_limit: Optional[int] = None,
        monthly_cost_limit: Optional[float] = None,
        rate_limit_per_minute: Optional[int] = None,
        rate_limit_per_hour: Optional[int] = None,
        rate_limit_per_day: Optional[int] = None,
        description: Optional[str] = None,
    ) -> bool:
        request_data = UpdateEndUserPlanRequest(
            monthly_token_limit=monthly_token_limit,
            monthly_cost_limit=monthly_cost_limit,
            rate_limit_per_minute=rate_limit_per_minute,
            rate_limit_per_hour=rate_limit_per_hour,
            rate_limit_per_day=rate_limit_per_day,
            description=description,
        )

        payload = {
            "monthly_token_limit": request_data.monthly_token_limit,
            "monthly_cost_limit": request_data.monthly_cost_limit,
            "rate_limit_per_minute": request_data.rate_limit_per_minute,
            "rate_limit_per_hour": request_data.rate_limit_per_hour,
            "rate_limit_per_day": request_data.rate_limit_per_day,
            "description": request_data.description,
        }

        response = self.request("PUT", f"/api/end-user-plans/{name}", json_data=payload)

        if response.status_code == 404:
            return False

        self._handle_response_errors(response)
        return True

    def delete_end_user_plan(self, name: str) -> bool:
        response = self.request("DELETE", f"/api/end-user-plans/{name}")

        if response.status_code == 404:
            return False

        self._handle_response_errors(response)
        return True

    def assign_end_user_to_plan(self, end_user_id: str, plan_name: str) -> bool:
        payload = {"end_user_id": end_user_id}

        response = self.request(
            "POST", f"/api/end-user-plans/{plan_name}/assign", json_data=payload
        )

        if response.status_code == 404:
            return False

        self._handle_response_errors(response)
        return True

    def remove_end_user_from_plan(self, end_user_id: str) -> bool:
        payload = {"end_user_id": end_user_id}

        response = self.request("POST", "/api/end-user-plans/remove", json_data=payload)

        if response.status_code == 404:
            return False

        self._handle_response_errors(response)
        return True

    def get_end_user_plan_assignment(
        self, end_user_id: str
    ) -> Optional[EndUserPlanInfo]:
        response = self.request("GET", f"/api/end-users/{end_user_id}/plan")

        if response.status_code == 404:
            return None

        self._handle_response_errors(response)
        data = response.json()

        return EndUserPlanInfo(
            id=data["id"],
            name=data["name"],
            monthly_token_limit=data.get("monthly_token_limit"),
            monthly_cost_limit=data.get("monthly_cost_limit"),
            rate_limit_per_minute=data.get("rate_limit_per_minute"),
            rate_limit_per_hour=data.get("rate_limit_per_hour"),
            rate_limit_per_day=data.get("rate_limit_per_day"),
            description=data.get("description"),
            is_active=data["is_active"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )

    def create_stripe_checkout_session(
        self,
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
            checkout_params["subscription_data"][
                "trial_period_days"
            ] = trial_period_days

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
        self,
        stripe_event: Dict[str, Any],
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
        parmot_fallback_plan_name: Optional[str] = metadata.get(
            "parmot_fallback_plan_name"
        )
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
        success: bool = self.assign_end_user_to_plan(end_user_id, target_plan)
        if success:
            logger.info(
                f"Assigned user {end_user_id} to plan {target_plan} after {action}"
            )
            return f"User assigned to {target_plan} plan", 200
        else:
            logger.error(
                f"Failed to assign user {end_user_id} to plan {target_plan} after {action}"
            )
            return f"Failed to assign user to {target_plan} plan", 500
