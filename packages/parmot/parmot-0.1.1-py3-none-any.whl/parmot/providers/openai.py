from openai import OpenAI as BaseOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from typing import Union, Iterator, Optional, List, Dict, Any
import logging
from ..client import ParmotClient
from ..usage import (
    track_completion,
    track_stream_chunk,
    ParmotUsageLimitError,
    ParmotEndUserUsageLimitError,
)

logger = logging.getLogger(__name__)


class TrackedCompletions:
    def __init__(self, completions, http_client: ParmotClient, provider: str):
        self._completions = completions
        self.http_client = http_client
        self.provider = provider

    def create(
        self, messages: List[Dict[str, Any]], model: str, user_id: str, **kwargs
    ) -> Union[ChatCompletion, Iterator[ChatCompletionChunk]]:

        create_kwargs = {"messages": messages, "model": model, **kwargs}

        stream = kwargs.get("stream", False)
        if stream:
            stream_options = kwargs.get("stream_options", {})
            stream_options["include_usage"] = True
            create_kwargs["stream_options"] = stream_options

        completion = self._completions.create(**create_kwargs)

        if isinstance(completion, ChatCompletion):
            usage_cost = track_completion(
                completion,
                model,
                user_id,
                self.http_client.api_key,
                self.http_client.api_base_url,
                self.provider,
            )
            return completion
        else:

            def stream_wrapper():
                final_usage_cost = None

                for chunk in completion:
                    yield chunk

                    if hasattr(chunk, "usage") and chunk.usage is not None:
                        usage_cost = track_stream_chunk(
                            chunk,
                            model,
                            user_id,
                            self.http_client.api_key,
                            self.http_client.api_base_url,
                            self.provider,
                        )
                        if usage_cost is not None:
                            final_usage_cost = usage_cost

            return stream_wrapper()


class TrackedChatCompletions:
    def __init__(self, chat_completions, http_client: ParmotClient, provider: str):
        self._chat_completions = chat_completions
        self.completions = TrackedCompletions(
            chat_completions.completions, http_client, provider
        )


class TrackedOpenAI(BaseOpenAI):
    def __init__(
        self,
        api_key: Optional[str] = None,
        parmot_api_key: Optional[str] = None,
        api_base_url: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(api_key=api_key, **kwargs)

        self.http_client = ParmotClient(parmot_api_key, api_base_url)
        self.provider = "openai"

        # Replace the chat attribute with our tracked version
        self.chat = TrackedChatCompletions(self.chat, self.http_client, self.provider)  # type: ignore
