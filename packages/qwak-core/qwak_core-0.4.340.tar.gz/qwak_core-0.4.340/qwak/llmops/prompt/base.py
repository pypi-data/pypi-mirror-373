import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional, Union

from cachetools import TTLCache, cached
from qwak.exceptions import QwakException
from qwak.llmops.generation.base import ModelResponse
from qwak.llmops.generation.chat.openai.types.chat.chat_completion import ChatCompletion
from qwak.llmops.generation.streaming import ChatCompletionStream, Stream
from qwak.llmops.model.descriptor import ChatModelDescriptor, ModelDescriptor
from qwak.llmops.prompt.chat.template import ChatPromptTemplate
from qwak.llmops.prompt.chat.value import ChatPromptValue
from qwak.llmops.prompt.value import PromptValue
from qwak.llmops.provider.chat import ChatCompletionProvider


@dataclass
class BasePrompt(ABC):
    @abstractmethod
    def render(self, variables: Dict[str, any]) -> PromptValue:
        pass

    @abstractmethod
    def invoke(
        self,
        variables: Optional[Dict[str, any]] = None,
        model_override: Optional[ModelDescriptor] = None,
        stream: bool = False,
    ) -> Union[ModelResponse, Stream]:
        pass


@dataclass
class ChatPrompt(BasePrompt):
    template: ChatPromptTemplate
    model: Optional[ChatModelDescriptor]

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if not isinstance(self.template, ChatPromptTemplate) or (
            self.model and not isinstance(self.model, ChatModelDescriptor)
        ):
            raise ValueError("ChatPrompt initiated with non-chat type fields!")

    def render(self, variables: Dict[str, any]) -> ChatPromptValue:
        return self.template.render(variables=variables)

    def invoke(
        self,
        variables: Optional[Dict[str, any]] = None,
        model_override: Optional[ModelDescriptor] = None,
        stream: bool = False,
    ) -> Union[ChatCompletion, ChatCompletionStream]:
        if not variables:
            variables = dict()
        if not self.model and not model_override:
            raise QwakException(
                "Can't invoke a prompt without a `ModelDescriptor`."
                " Please provide one using the model_override "
                "or create a ChatPrompt with a model."
            )

        return ChatCompletionProvider.invoke(
            chat_prompt_value=self.render(variables=variables),
            chat_model_descriptor=model_override if model_override else self.model,
            stream=stream,
        )


@dataclass
class RegisteredPrompt(BasePrompt):
    name: str
    prompt_description: str
    version_description: str
    version: int
    _target_default_version: bool
    prompt: BasePrompt
    _cache: Callable[[str], "RegisteredPrompt"] = field(init=False, default=None)
    _prompt_manager: "PromptManager" = None  # noqa

    def _get_prompt_manager(self) -> "PromptManager":  # noqa
        from qwak.llmops.prompt.manager import PromptManager

        if not self._prompt_manager:
            self._prompt_manager = PromptManager()
        return self._prompt_manager

    def _get_prompt_default_version_internal(self, name: str) -> "RegisteredPrompt":
        return self._get_prompt_manager().get_prompt(name=name, version=None)

    def _get_prompt_default_version(self, *, name: str) -> "RegisteredPrompt":
        if not self._cache:
            cache = cached(
                cache=TTLCache(
                    maxsize=1, ttl=float(os.environ.get("_PROMPT_CACHE_SECONDS", "60"))
                ),
                key=lambda *args, **kwargs: kwargs["name"],
            )
            self._cache = cache(self._get_prompt_default_version_internal)
        return self._cache(name=name)  # noqa

    def _handle_default_version_swap(self):
        if self._target_default_version:
            new_default_version_prompt: RegisteredPrompt = (
                self._get_prompt_default_version(name=self.name)
            )
            self.prompt_description = new_default_version_prompt.prompt_description
            if self.version != new_default_version_prompt.version:
                self.version_description = (
                    new_default_version_prompt.version_description
                )
                self.version = new_default_version_prompt.version
                self.prompt = new_default_version_prompt.prompt

    def render(self, variables: Dict[str, any]) -> PromptValue:
        self._handle_default_version_swap()
        return self.prompt.render(variables=variables)

    def invoke(
        self,
        variables: Optional[Dict[str, any]] = None,
        model_override: Optional[ModelDescriptor] = None,
        stream: bool = False,
    ) -> Union[ModelResponse, Stream]:
        if not variables:
            variables = dict()
        self._handle_default_version_swap()
        return self.prompt.invoke(
            variables=variables, model_override=model_override, stream=stream
        )
