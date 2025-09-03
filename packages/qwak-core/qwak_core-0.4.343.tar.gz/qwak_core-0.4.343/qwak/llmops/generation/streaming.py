from abc import ABC
from typing import Generic, TypeVar

from qwak.llmops.generation.chat.openai.types.chat.chat_completion_chunk import (
    ChatCompletionChunk,
)

try:
    from collections import Iterable

    iterableABC = Iterable
except ImportError:
    from collections.abc import Iterable

    iterableABC = Iterable


_T = TypeVar("_T")


class Stream(Generic[_T], ABC, iterableABC):
    pass


class ChatCompletionStream(Stream[ChatCompletionChunk], ABC):
    pass
