from typing import Optional, Dict, Any, Union
from dataclasses import dataclass
import requests
import os
import logging

logger = logging.getLogger(__name__)

try:
    from openai.types.chat import ChatCompletion, ChatCompletionChunk
    from openai.types.completion_usage import CompletionUsage
except ImportError:
    # OpenAI types not available, we'll create minimal compatible
    # CompletionUsage since it is used downstream for tracking all clients
    class CompletionUsage:
        def __init__(
            self, prompt_tokens: int, completion_tokens: int, total_tokens: int
        ):
            self.prompt_tokens = prompt_tokens
            self.completion_tokens = completion_tokens
            self.total_tokens = total_tokens

    ChatCompletion = Any
    ChatCompletionChunk = Any

try:
    from anthropic.types import Message as AnthropicMessage
    from anthropic.types.raw_message_delta_event import RawMessageDeltaEvent
except ImportError:
    AnthropicMessage = Any
    RawMessageDeltaEvent = Any

try:
    from cohere.v2.types import V2ChatResponse as CohereV2ChatResponse
    from cohere.v2.types.v2chat_stream_response import (
        V2ChatStreamResponse as CohereV2ChatStreamResponse,
        MessageEndV2ChatStreamResponse,
    )
except ImportError:
    CohereV2ChatResponse = Any
    CohereV2ChatStreamResponse = Any
    MessageEndV2ChatStreamResponse = Any


@dataclass
class UsageCost:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    model: str
    provider: str


class ParmotError(Exception):
    """Base exception for Parmot SDK errors"""

    pass


class ParmotUsageLimitError(ParmotError):
    """Raised when the Parmot user (customer) hits their subscription limit"""

    def __init__(self, message: str):
        super().__init__(message)


class ParmotEndUserUsageLimitError(ParmotError):
    """Raised when an end user hits their usage limits"""

    def __init__(
        self, message: str, current_usage: float, limit: float, limit_type: str
    ):
        super().__init__(message)
        self.current_usage = current_usage
        self.limit = limit
        self.limit_type = limit_type


class ParmotEndUserRateLimitError(ParmotError):
    """Raised when an end user hits their rate limits"""

    def __init__(
        self, message: str, current_rate: int, limit: int, window: str, retry_after: int
    ):
        super().__init__(message)
        self.current_rate = current_rate
        self.limit = limit
        self.window = window
        self.retry_after = retry_after


class ParmotEndUserBannedError(ParmotError):
    """Raised when an end user is banned"""

    def __init__(self, message: str):
        super().__init__(message)


class ParmotAPIError(ParmotError):
    """Raised when the API returns an error"""

    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.status_code = status_code


class ParmotNotFoundError(ParmotError):
    """Raised when a resource is not found"""

    def __init__(self, message: str):
        super().__init__(message)


class ParmotValidationError(ParmotError):
    """Raised when request validation fails"""

    def __init__(self, message: str):
        super().__init__(message)


class ModelPricing:
    PRICING = {
        # Google Models
        "gemini-2.5-pro": {
            "input": 0.00125 / 1000,
            "output": 0.01 / 1000,
        },
        "gemini-2.5-flash": {
            "input": 0.0003 / 1000,
            "output": 0.0025 / 1000,
        },
        "gemini-2.0-flash": {
            "input": 0.0001 / 1000,
            "output": 0.0004 / 1000,
        },
        # Databricks models
        "databricks-llama-4-maverick": {
            "input": 0.0005 / 1000,
            "output": 0.0015 / 1000,
        },
        # OpenAI models
        "gpt-4o-mini": {
            "input": 0.00015 / 1000,
            "output": 0.0006 / 1000,
        },
        "gpt-4o": {
            "input": 0.005 / 1000,
            "output": 0.015 / 1000,
        },
        "gpt-4": {
            "input": 0.03 / 1000,
            "output": 0.06 / 1000,
        },
        "gpt-3.5-turbo": {
            "input": 0.001 / 1000,
            "output": 0.002 / 1000,
        },
        # Anthropic models
        "claude-sonnet-4": {
            "input": 3.0 / 1000000,
            "output": 15.0 / 1000000,
        },
        "claude-3-5-sonnet-20241022": {
            "input": 3.0 / 1000000,
            "output": 15.0 / 1000000,
        },
        "claude-3-5-sonnet-20240620": {
            "input": 3.0 / 1000000,
            "output": 15.0 / 1000000,
        },
        "claude-3-5-sonnet-latest": {
            "input": 3.0 / 1000000,
            "output": 15.0 / 1000000,
        },
        "claude-3-5-haiku-20241022": {
            "input": 0.25 / 1000000,
            "output": 1.25 / 1000000,
        },
        "claude-3-5-haiku-latest": {
            "input": 0.25 / 1000000,
            "output": 1.25 / 1000000,
        },
        "claude-3-opus-20240229": {
            "input": 15.0 / 1000000,
            "output": 75.0 / 1000000,
        },
        "claude-3-opus-latest": {
            "input": 15.0 / 1000000,
            "output": 75.0 / 1000000,
        },
        "claude-3-sonnet-20240229": {
            "input": 3.0 / 1000000,
            "output": 15.0 / 1000000,
        },
        "claude-3-haiku-20240307": {
            "input": 0.25 / 1000000,
            "output": 1.25 / 1000000,
        },
        "claude-2.1": {
            "input": 8.0 / 1000000,
            "output": 24.0 / 1000000,
        },
        "claude-2.0": {
            "input": 8.0 / 1000000,
            "output": 24.0 / 1000000,
        },
        "claude-instant-1.2": {
            "input": 0.8 / 1000000,
            "output": 2.4 / 1000000,
        },
        # Cohere models
        "command-r-plus-08-2024": {
            "input": 3.0 / 1000000,
            "output": 15.0 / 1000000,
        },
        "command-r-08-2024": {
            "input": 0.15 / 1000000,
            "output": 0.6 / 1000000,
        },
        "command-r-plus": {
            "input": 3.0 / 1000000,
            "output": 15.0 / 1000000,
        },
        "command-r": {
            "input": 0.5 / 1000000,
            "output": 1.5 / 1000000,
        },
        "command": {
            "input": 1.0 / 1000000,
            "output": 2.0 / 1000000,
        },
        "command-nightly": {
            "input": 1.0 / 1000000,
            "output": 2.0 / 1000000,
        },
        "command-light": {
            "input": 0.3 / 1000000,
            "output": 0.6 / 1000000,
        },
        "command-light-nightly": {
            "input": 0.3 / 1000000,
            "output": 0.6 / 1000000,
        },
    }

    @classmethod
    def get_pricing(cls, model: str) -> Dict[str, float]:
        if model not in cls.PRICING:
            logger.warning(
                f"Model '{model}' pricing not found, using claude-3-5-haiku pricing as fallback"
            )
            return cls.PRICING["claude-3-5-haiku-20241022"]
        return cls.PRICING[model]


def create_openai_compatible_usage(
    prompt_tokens: int, completion_tokens: int, total_tokens: Optional[int] = None
) -> CompletionUsage:
    """Create an OpenAI-compatible usage object from token counts."""
    if total_tokens is None:
        total_tokens = prompt_tokens + completion_tokens

    return CompletionUsage(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
    )


def calculate_cost(
    usage: Union[CompletionUsage, Dict[str, int]], model: str, provider: str = "openai"
) -> UsageCost:
    """Calculate cost from usage object (OpenAI-compatible format)."""
    pricing = ModelPricing.get_pricing(model)

    # Handle both CompletionUsage objects and dict formats
    if isinstance(usage, dict):
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)
    else:
        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        total_tokens = usage.total_tokens

    input_cost = prompt_tokens * pricing["input"]
    output_cost = completion_tokens * pricing["output"]
    total_cost = input_cost + output_cost

    return UsageCost(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        input_cost=input_cost,
        output_cost=output_cost,
        total_cost=total_cost,
        model=model,
        provider=provider,
    )


def extract_anthropic_usage(response: AnthropicMessage) -> Optional[CompletionUsage]:
    """Extract usage information from Anthropic response and convert to OpenAI format."""
    if response.usage is None:
        return None

    return create_openai_compatible_usage(
        prompt_tokens=response.usage.input_tokens,
        completion_tokens=response.usage.output_tokens,
    )


def extract_anthropic_stream_usage(
    event: RawMessageDeltaEvent, accumulated_input_tokens: int = 0
) -> Optional[CompletionUsage]:
    """Extract usage information from Anthropic stream event and convert to OpenAI format."""
    if event.usage is None:
        return None

    return create_openai_compatible_usage(
        prompt_tokens=accumulated_input_tokens,
        completion_tokens=event.usage.output_tokens,
    )


def extract_cohere_usage(response: CohereV2ChatResponse) -> Optional[CompletionUsage]:
    """Extract usage information from Cohere response and convert to OpenAI format."""
    if response.usage is None or response.usage.billed_units is None:
        return None

    input_tokens = int(response.usage.billed_units.input_tokens or 0)
    output_tokens = int(response.usage.billed_units.output_tokens or 0)

    return create_openai_compatible_usage(
        prompt_tokens=input_tokens, completion_tokens=output_tokens
    )


def extract_cohere_stream_usage(
    event: CohereV2ChatStreamResponse,
) -> Optional[CompletionUsage]:
    """Extract usage information from Cohere stream event and convert to OpenAI format."""
    # Check if this is a message-end event which contains usage information in delta
    if isinstance(event, MessageEndV2ChatStreamResponse) and event.delta is not None:
        # Extract usage from the delta if available
        if hasattr(event.delta, "usage") and event.delta.usage is not None:
            usage = event.delta.usage

            # Handle both dict and object formats for usage
            if isinstance(usage, dict):
                billed_units = usage.get("billed_units")
                if billed_units:
                    input_tokens = int(billed_units.get("input_tokens", 0))
                    output_tokens = int(billed_units.get("output_tokens", 0))

                    return create_openai_compatible_usage(
                        prompt_tokens=input_tokens, completion_tokens=output_tokens
                    )
            else:
                # Handle object format
                if hasattr(usage, "billed_units") and usage.billed_units is not None:
                    input_tokens = int(usage.billed_units.input_tokens or 0)
                    output_tokens = int(usage.billed_units.output_tokens or 0)

                    return create_openai_compatible_usage(
                        prompt_tokens=input_tokens, completion_tokens=output_tokens
                    )

    return None


def send_usage_to_api(
    api_key: str,
    end_user_id: str,
    usage_cost: UsageCost,
    api_base_url: Optional[str] = None,
) -> bool:
    if api_base_url is None:
        api_base_url = os.getenv(
            "PARMOT_API_BASE_URL", "https://parmotbackend-production.up.railway.app"
        )

    url = f"{api_base_url}/api/end-user-usage/record"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    payload = {
        "end_user_id": end_user_id,
        "model": usage_cost.model,
        "provider": usage_cost.provider,
        "prompt_tokens": usage_cost.prompt_tokens,
        "completion_tokens": usage_cost.completion_tokens,
        "total_tokens": usage_cost.total_tokens,
        "input_cost": usage_cost.input_cost,
        "output_cost": usage_cost.output_cost,
        "total_cost": usage_cost.total_cost,
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if response.status_code == 429:
            try:
                error_data: Dict[str, Any] = response.json()
            except:
                error_data: Dict[str, Any] = {"error": "Rate limit exceeded"}

            raise ParmotEndUserRateLimitError(
                error_data.get("error", "Rate limit exceeded"),
                error_data.get("current_rate", 0),
                error_data.get("limit", 0),
                error_data.get("window", "unknown"),
                error_data.get("retry_after", 60),
            )
        elif response.status_code == 402:
            try:
                error_data: Dict[str, Any] = response.json()
            except:
                error_data: Dict[str, Any] = {"error": "Usage limit exceeded"}

            # Check if this is an end user limit error (has additional fields)
            if error_data and "current_usage" in error_data and "limit" in error_data:
                raise ParmotEndUserUsageLimitError(
                    error_data["error"],
                    error_data["current_usage"],
                    error_data["limit"],
                    error_data.get("limit_type", "unknown"),
                )
            else:
                # This is a Parmot user limit error (only has error field)
                raise ParmotUsageLimitError(
                    error_data.get("error", "Parmot user usage limit exceeded")
                )
        elif response.status_code != 201:
            try:
                error_data = response.json()
                error_message = error_data.get(
                    "error", f"HTTP {response.status_code} error"
                )
            except:
                error_message = f"HTTP {response.status_code} error"

            logger.error(
                f"Failed to record usage: {response.status_code} - {error_message}"
            )
            raise ParmotAPIError(error_message, response.status_code)

        logger.info(f"Successfully recorded usage for user {end_user_id}")
        return True

    except (
        ParmotUsageLimitError,
        ParmotEndUserUsageLimitError,
        ParmotEndUserRateLimitError,
        ParmotAPIError,
    ):
        raise
    except requests.RequestException as e:
        logger.error(f"Error sending usage to API: {str(e)}")
        raise ParmotAPIError(f"Network error: {str(e)}", 0)


def track_completion(
    response: Union[ChatCompletion, Any],
    model: str,
    end_user_id: str,
    api_key: str,
    api_base_url: Optional[str] = None,
    provider: str = "openai",
) -> Optional[UsageCost]:
    if response.usage is None:
        return None

    usage_cost = calculate_cost(response.usage, model, provider)

    try:
        success = send_usage_to_api(api_key, end_user_id, usage_cost, api_base_url)

        if success:
            logger.info(
                f"✅ Usage recorded: ${usage_cost.total_cost:.6f} ({usage_cost.prompt_tokens} input + {usage_cost.completion_tokens} output tokens) for user {end_user_id}"
            )

        return usage_cost
    except ParmotUsageLimitError as e:
        logger.error(f"❌ Parmot user subscription limit exceeded: {str(e)}")
        raise
    except ParmotEndUserUsageLimitError as e:
        logger.warning(
            f"⚠️ End user usage limit exceeded for user {end_user_id}: {str(e)}"
        )
        logger.info(
            f"✅ Usage was still recorded: ${usage_cost.total_cost:.6f} ({usage_cost.prompt_tokens} input + {usage_cost.completion_tokens} output tokens) for user {end_user_id}"
        )
        raise
    except ParmotEndUserRateLimitError as e:
        logger.warning(
            f"⚠️ End user rate limit exceeded for user {end_user_id}: {str(e)}"
        )
        raise


def track_stream_chunk(
    chunk: Union[ChatCompletionChunk, Any],
    model: str,
    end_user_id: str,
    api_key: str,
    api_base_url: Optional[str] = None,
    provider: str = "openai",
) -> Optional[UsageCost]:
    if chunk.usage is None:
        return None
    usage_cost = calculate_cost(chunk.usage, model, provider)
    send_usage_to_api(api_key, end_user_id, usage_cost, api_base_url)
    return usage_cost


def track_anthropic_message(
    response: AnthropicMessage,
    model: str,
    end_user_id: str,
    api_key: str,
    api_base_url: Optional[str] = None,
    provider: str = "anthropic",
) -> Optional[UsageCost]:
    usage = extract_anthropic_usage(response)
    if usage is None:
        return None

    usage_cost = calculate_cost(usage, model, provider)

    try:
        success = send_usage_to_api(api_key, end_user_id, usage_cost, api_base_url)

        if success:
            logger.info(
                f"✅ Usage recorded: ${usage_cost.total_cost:.6f} ({usage_cost.prompt_tokens} input + {usage_cost.completion_tokens} output tokens) for user {end_user_id}"
            )

        return usage_cost
    except ParmotUsageLimitError as e:
        logger.error(f"❌ Parmot user subscription limit exceeded: {str(e)}")
        raise
    except ParmotEndUserUsageLimitError as e:
        logger.warning(
            f"⚠️ End user usage limit exceeded for user {end_user_id}: {str(e)}"
        )
        logger.info(
            f"✅ Usage was still recorded: ${usage_cost.total_cost:.6f} ({usage_cost.prompt_tokens} input + {usage_cost.completion_tokens} output tokens) for user {end_user_id}"
        )
        raise
    except ParmotEndUserRateLimitError as e:
        logger.warning(
            f"⚠️ End user rate limit exceeded for user {end_user_id}: {str(e)}"
        )
        raise


def track_anthropic_stream_event(
    event: RawMessageDeltaEvent,
    model: str,
    end_user_id: str,
    api_key: str,
    api_base_url: Optional[str] = None,
    provider: str = "anthropic",
    accumulated_input_tokens: int = 0,
) -> Optional[UsageCost]:
    usage = extract_anthropic_stream_usage(event, accumulated_input_tokens)
    if usage is None:
        return None

    usage_cost = calculate_cost(usage, model, provider)

    try:
        success = send_usage_to_api(api_key, end_user_id, usage_cost, api_base_url)

        if success:
            logger.info(
                f"✅ Stream usage recorded: ${usage_cost.total_cost:.6f} ({usage_cost.prompt_tokens} input + {usage_cost.completion_tokens} output tokens) for user {end_user_id}"
            )

        return usage_cost
    except ParmotUsageLimitError as e:
        logger.error(f"❌ Parmot user subscription limit exceeded: {str(e)}")
        raise
    except ParmotEndUserUsageLimitError as e:
        logger.warning(
            f"⚠️ End user usage limit exceeded for user {end_user_id}: {str(e)}"
        )
        logger.info(
            f"✅ Stream usage was still recorded: ${usage_cost.total_cost:.6f} ({usage_cost.prompt_tokens} input + {usage_cost.completion_tokens} output tokens) for user {end_user_id}"
        )
        raise
    except ParmotEndUserRateLimitError as e:
        logger.warning(
            f"⚠️ End user rate limit exceeded for user {end_user_id}: {str(e)}"
        )
        raise


def track_cohere_message(
    response: CohereV2ChatResponse,
    model: str,
    end_user_id: str,
    api_key: str,
    api_base_url: Optional[str] = None,
    provider: str = "cohere",
) -> Optional[UsageCost]:
    usage = extract_cohere_usage(response)
    if usage is None:
        return None

    usage_cost = calculate_cost(usage, model, provider)

    try:
        success = send_usage_to_api(api_key, end_user_id, usage_cost, api_base_url)

        if success:
            logger.info(
                f"✅ Usage recorded: ${usage_cost.total_cost:.6f} ({usage_cost.prompt_tokens} input + {usage_cost.completion_tokens} output tokens) for user {end_user_id}"
            )

        return usage_cost
    except ParmotUsageLimitError as e:
        logger.error(f"❌ Parmot user subscription limit exceeded: {str(e)}")
        raise
    except ParmotEndUserUsageLimitError as e:
        logger.warning(
            f"⚠️ End user usage limit exceeded for user {end_user_id}: {str(e)}"
        )
        logger.info(
            f"✅ Usage was still recorded: ${usage_cost.total_cost:.6f} ({usage_cost.prompt_tokens} input + {usage_cost.completion_tokens} output tokens) for user {end_user_id}"
        )
        raise
    except ParmotEndUserRateLimitError as e:
        logger.warning(
            f"⚠️ End user rate limit exceeded for user {end_user_id}: {str(e)}"
        )
        raise


def track_cohere_stream_event(
    event: CohereV2ChatStreamResponse,
    model: str,
    end_user_id: str,
    api_key: str,
    api_base_url: Optional[str] = None,
    provider: str = "cohere",
) -> Optional[UsageCost]:
    usage = extract_cohere_stream_usage(event)
    if usage is None:
        return None

    usage_cost = calculate_cost(usage, model, provider)

    try:
        success = send_usage_to_api(api_key, end_user_id, usage_cost, api_base_url)

        if success:
            logger.info(
                f"✅ Stream usage recorded: ${usage_cost.total_cost:.6f} ({usage_cost.prompt_tokens} input + {usage_cost.completion_tokens} output tokens) for user {end_user_id}"
            )

        return usage_cost
    except ParmotUsageLimitError as e:
        logger.error(f"❌ Parmot user subscription limit exceeded: {str(e)}")
        raise
    except ParmotEndUserUsageLimitError as e:
        logger.warning(
            f"⚠️ End user usage limit exceeded for user {end_user_id}: {str(e)}"
        )
        logger.info(
            f"✅ Stream usage was still recorded: ${usage_cost.total_cost:.6f} ({usage_cost.prompt_tokens} input + {usage_cost.completion_tokens} output tokens) for user {end_user_id}"
        )
        raise
    except ParmotEndUserRateLimitError as e:
        logger.warning(
            f"⚠️ End user rate limit exceeded for user {end_user_id}: {str(e)}"
        )
        raise
