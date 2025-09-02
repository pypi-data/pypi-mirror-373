from typing import Optional, List, Dict, Any, Iterator, Union
import logging
from ..client import ParmotClient
from ..usage import (
    track_cohere_message,
    track_cohere_stream_event,
    ParmotUsageLimitError,
    ParmotEndUserUsageLimitError,
    UsageCost,
)

logger = logging.getLogger(__name__)

try:
    from cohere import ClientV2
    from cohere.v2.types import V2ChatResponse, V2ChatStreamResponse
except ImportError:
    raise ImportError(
        "The cohere package is required. Install it with: pip install cohere"
    )


class TrackedCohere:
    def __init__(
        self,
        api_key: Optional[str] = None,
        parmot_api_key: Optional[str] = None,
        api_base_url: Optional[str] = None,
        **kwargs,
    ):
        self.client = ClientV2(api_key=api_key, **kwargs)
        self.http_client = ParmotClient(parmot_api_key, api_base_url)
        self.provider = "cohere"

    def chat(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        user_id: str,
        **kwargs,
    ) -> V2ChatResponse:
        chat_kwargs = {"model": model, "messages": messages, **kwargs}
        response = self.client.chat(**chat_kwargs)

        usage_cost = track_cohere_message(
            response,
            model,
            user_id,
            self.http_client.api_key,
            self.http_client.api_base_url,
            self.provider,
        )
        return response

    def chat_stream(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        user_id: str,
        **kwargs,
    ) -> Iterator[V2ChatStreamResponse]:
        chat_kwargs = {"model": model, "messages": messages, **kwargs}
        stream = self.client.chat_stream(**chat_kwargs)

        def stream_wrapper() -> Iterator[V2ChatStreamResponse]:
            final_usage_cost: Optional[UsageCost] = None

            for event in stream:
                yield event

                # Handle message-end events which contain usage information
                if hasattr(event, "type") and event.type == "message-end":
                    # Track the final event which should contain usage
                    usage_cost = track_cohere_stream_event(
                        event,
                        model,
                        user_id,
                        self.http_client.api_key,
                        self.http_client.api_base_url,
                        self.provider,
                    )
                    if usage_cost is not None:
                        final_usage_cost = usage_cost

        return stream_wrapper()

    def __getattr__(self, name: str) -> Any:
        return getattr(self.client, name)
