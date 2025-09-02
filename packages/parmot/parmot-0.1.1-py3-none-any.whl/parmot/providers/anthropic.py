from typing import Optional, List, Dict, Any, Iterator, Union, cast
import logging
from ..client import ParmotClient
from ..usage import (
    track_anthropic_message,
    track_anthropic_stream_event,
    ParmotUsageLimitError,
    ParmotEndUserUsageLimitError,
    UsageCost,
)

logger = logging.getLogger(__name__)

from anthropic import Anthropic as BaseAnthropic
from anthropic.types import Message
from anthropic.types.raw_message_stream_event import RawMessageStreamEvent
from anthropic.types.raw_message_delta_event import RawMessageDeltaEvent
from anthropic.types.message_param import MessageParam
from anthropic.types.model_param import ModelParam


class TrackedMessages:
    def __init__(self, messages: Any, http_client: ParmotClient, provider: str):
        self._messages = messages
        self.http_client = http_client
        self.provider = provider

    def create(
        self,
        max_tokens: int,
        messages: List[MessageParam],
        model: ModelParam,
        user_id: str,
        **kwargs: Any,
    ) -> Union[Message, Iterator[RawMessageStreamEvent]]:
        # Check if streaming is requested
        stream = kwargs.get("stream", False)

        if stream:
            # Build streaming parameters
            streaming_kwargs: Dict[str, Any] = {
                "max_tokens": max_tokens,
                "messages": messages,
                "model": model,
                "stream": True,
            }

            # Add other valid kwargs except stream
            for key, value in kwargs.items():
                if key != "stream":
                    streaming_kwargs[key] = value

            response = self._messages.create(**streaming_kwargs)

            def stream_wrapper() -> Iterator[RawMessageStreamEvent]:
                final_usage_cost: Optional[UsageCost] = None
                accumulated_input_tokens = 0

                stream_response = cast(Iterator[RawMessageStreamEvent], response)
                for event in stream_response:
                    yield event

                    # Handle message_start event to get input tokens
                    if event.type == "message_start":
                        if event.message.usage.input_tokens is not None:
                            accumulated_input_tokens = event.message.usage.input_tokens

                    # Handle message_delta event which contains final usage
                    elif event.type == "message_delta":
                        delta_event = cast(RawMessageDeltaEvent, event)
                        if delta_event.usage.output_tokens is not None:
                            usage_cost = track_anthropic_stream_event(
                                delta_event,
                                str(model),
                                user_id,
                                self.http_client.api_key,
                                self.http_client.api_base_url,
                                self.provider,
                                accumulated_input_tokens,
                            )
                            if usage_cost is not None:
                                final_usage_cost = usage_cost

            return stream_wrapper()
        else:
            # Build non-streaming parameters
            non_streaming_kwargs: Dict[str, Any] = {
                "max_tokens": max_tokens,
                "messages": messages,
                "model": model,
            }

            # Add other valid kwargs except stream
            for key, value in kwargs.items():
                if key != "stream":
                    non_streaming_kwargs[key] = value

            response = self._messages.create(**non_streaming_kwargs)
            message_response = cast(Message, response)
            usage_cost = track_anthropic_message(
                message_response,
                str(model),
                user_id,
                self.http_client.api_key,
                self.http_client.api_base_url,
                self.provider,
            )
            return message_response


class TrackedAnthropic:
    def __init__(
        self,
        api_key: Optional[str] = None,
        parmot_api_key: Optional[str] = None,
        api_base_url: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        default_headers: Optional[Dict[str, str]] = None,
        default_query: Optional[Dict[str, str]] = None,
        http_client: Optional[Any] = None,
        **kwargs: Any,
    ):
        # Filter kwargs to only include valid Anthropic client arguments
        anthropic_kwargs: Dict[str, Any] = {}
        if base_url is not None:
            anthropic_kwargs["base_url"] = base_url
        if timeout is not None:
            anthropic_kwargs["timeout"] = timeout
        if max_retries is not None:
            anthropic_kwargs["max_retries"] = max_retries
        if default_headers is not None:
            anthropic_kwargs["default_headers"] = default_headers
        if default_query is not None:
            anthropic_kwargs["default_query"] = default_query
        if http_client is not None:
            anthropic_kwargs["http_client"] = http_client

        self.client = BaseAnthropic(api_key=api_key, **anthropic_kwargs)
        self.http_client = ParmotClient(parmot_api_key, api_base_url)
        self.provider = "anthropic"

        # Replace the messages attribute with our tracked version
        self.messages = TrackedMessages(
            self.client.messages, self.http_client, self.provider
        )

    def __getattr__(self, name: str) -> Any:
        # Delegate all other attributes to the underlying client
        return getattr(self.client, name)
