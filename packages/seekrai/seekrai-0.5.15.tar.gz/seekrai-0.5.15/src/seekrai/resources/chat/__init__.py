from functools import cached_property

from seekrai.resources.chat.completions import AsyncChatCompletions, ChatCompletions
from seekrai.types import (
    SeekrFlowClient,
)


class Chat:
    def __init__(self, client: SeekrFlowClient) -> None:
        self._client = client

    @cached_property
    def completions(self) -> ChatCompletions:
        return ChatCompletions(self._client)


class AsyncChat:
    def __init__(self, client: SeekrFlowClient) -> None:
        self._client = client

    @cached_property
    def completions(self) -> AsyncChatCompletions:
        return AsyncChatCompletions(self._client)
