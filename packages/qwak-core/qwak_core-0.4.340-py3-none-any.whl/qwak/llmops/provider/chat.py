from functools import lru_cache
from typing import Union

from qwak.llmops.generation.chat.openai.types.chat.chat_completion import ChatCompletion
from qwak.llmops.generation.streaming import ChatCompletionStream
from qwak.llmops.model.descriptor import ChatModelDescriptor, OpenAIChat
from qwak.llmops.prompt.chat.value import ChatPromptValue
from qwak.llmops.provider.openai.provider import OpenAIProvider


class ChatCompletionProvider:
    @staticmethod
    @lru_cache(maxsize=None)
    def _get_openai_provider():
        return OpenAIProvider()

    @staticmethod
    def invoke(
        chat_prompt_value: ChatPromptValue,
        chat_model_descriptor: ChatModelDescriptor,
        stream: bool = False,
    ) -> Union[ChatCompletion, ChatCompletionStream]:
        if isinstance(chat_model_descriptor, OpenAIChat):
            return ChatCompletionProvider._invoke_openai_chat(
                chat_prompt_value=chat_prompt_value,
                chat_model_descriptor=chat_model_descriptor,
                stream=stream,
            )
        else:
            raise ValueError("Can't invoke prompt and model combination!")

    @staticmethod
    def _invoke_openai_chat(
        chat_prompt_value: ChatPromptValue,
        chat_model_descriptor: OpenAIChat,
        stream: bool = False,
    ) -> Union[ChatCompletion, ChatCompletionStream]:
        return ChatCompletionProvider._get_openai_provider().create_chat_completion(
            chat_prompt_value=chat_prompt_value,
            chat_model_descriptor=chat_model_descriptor,
            stream=stream,
        )
