import random
from typing import Dict, List, Optional, Union

from qwak.clients.integration_management.integration_utils import IntegrationUtils
from qwak.clients.integration_management.openai.openai_system_secret import (
    OpenAIApiKeySystemSecret,
)
from qwak.exceptions import QwakException
from qwak.llmops.generation.chat.openai.types.chat.chat_completion import ChatCompletion
from qwak.llmops.generation.streaming import ChatCompletionStream
from qwak.llmops.model.descriptor import OpenAIChat
from qwak.llmops.prompt.chat.message import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from qwak.llmops.prompt.chat.value import ChatPromptValue
from qwak.llmops.provider.openai.client import OpenAIClient


class OpenAIProvider:
    client: OpenAIClient

    def __init__(self):
        self.client = OpenAIClient()

    def _get_random_openai_api_key(self) -> Optional[str]:
        openai_api_keys: List[OpenAIApiKeySystemSecret] = (
            IntegrationUtils().get_openai_api_keys()
        )
        if len(openai_api_keys) == 0:
            return None

        return random.choice(openai_api_keys).get_api_key()  # nosec

    def _chat_value_to_json(self, chat_prompt_value: ChatPromptValue) -> List[Dict]:
        return [self._map_message(m) for m in chat_prompt_value.messages]

    def _map_message(self, message: BaseMessage) -> Dict[str, str]:
        role: str
        content: str = message.content

        if isinstance(message, AIMessage):
            role = "assistant"
        elif isinstance(message, SystemMessage):
            role = "system"
        elif isinstance(message, HumanMessage):
            role = "user"
        else:
            raise QwakException(f"Can't handle message of type: {repr(message)}")

        return {"role": role, "content": content}

    def create_chat_completion(
        self,
        chat_prompt_value: ChatPromptValue,
        chat_model_descriptor: OpenAIChat,
        stream: bool = False,
    ) -> Union[ChatCompletion, ChatCompletionStream]:
        openai_api_key: Optional[str] = self._get_random_openai_api_key()
        if not openai_api_key:
            raise QwakException(
                "Could not find Open AI integration, Please create one."
            )

        d = chat_model_descriptor

        return self.client.invoke_chat_completion(
            stream=stream,
            api_key=openai_api_key,
            model=d.model_id,
            messages=self._chat_value_to_json(chat_prompt_value),
            frequency_penalty=d.frequency_penalty,
            logit_bias=d.logit_bias,
            logprobs=d.logprobs,
            max_tokens=d.max_tokens,
            n=d.n,
            presence_penalty=d.presence_penalty,
            response_format=d.response_format,
            seed=d.seed,
            stop=d.stop,
            temperature=d.temperature,
            top_logprobs=d.top_logprobs,
            top_p=d.top_p,
            user=d.user,
            tool_choice=d.tool_choice,
            tools=d.tools,
        )
