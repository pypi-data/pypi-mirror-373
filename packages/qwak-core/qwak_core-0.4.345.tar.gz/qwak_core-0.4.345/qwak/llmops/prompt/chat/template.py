import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Union

from qwak.llmops.prompt.chat.message import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from qwak.llmops.prompt.chat.value import ChatPromptValue
from qwak.llmops.prompt.template import BasePromptTemplate, StringPromptTemplate


@dataclass
class BaseMessagePromptTemplate(BasePromptTemplate):
    @abstractmethod
    def render(self, variables: Dict[str, any]) -> BaseMessage:
        pass


@dataclass
class BaseStringMessagePromptTemplate(BaseMessagePromptTemplate, ABC):
    template: StringPromptTemplate = field(init=False)
    role_name: str = field(init=False)

    def __init__(self, template: str):
        self.template = StringPromptTemplate(template=template)


class AIMessagePromptTemplate(BaseStringMessagePromptTemplate):
    role_name: str = "ai"

    def render(self, variables: Dict[str, any]) -> BaseMessage:
        return AIMessage(content=self.template.render(variables=variables).to_string())


class HumanMessagePromptTemplate(BaseStringMessagePromptTemplate):
    role_name: str = "human"

    def render(self, variables: Dict[str, any]) -> BaseMessage:
        return HumanMessage(
            content=self.template.render(variables=variables).to_string()
        )


class SystemMessagePromptTemplate(BaseStringMessagePromptTemplate):
    role_name: str = "system"

    def render(self, variables: Dict[str, any]) -> BaseMessage:
        return SystemMessage(
            content=self.template.render(variables=variables).to_string()
        )


@dataclass
class ChatPromptTemplate(BasePromptTemplate):
    messages: List[Union[BaseMessage, BaseStringMessagePromptTemplate]]

    def render(self, variables: Dict[str, any]) -> ChatPromptValue:
        resulting_messages: List[BaseMessage] = list()

        for message in self.messages:
            if isinstance(message, BaseMessage):
                resulting_messages.append(message)
            elif isinstance(message, BaseStringMessagePromptTemplate):
                resulting_messages.append(message.render(variables=variables))
            else:
                raise ValueError(
                    f"Got unsupported message type: {repr(message)}. \n"
                    "Supported messages are: "
                    "AIMessagePromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate, \n"
                    "AIMessage, HumanMessage, SystemMessage."
                )

        return ChatPromptValue(messages=resulting_messages)

    def to_messages(self) -> List[Tuple[str, str]]:
        """
        Useful for integration with other libraries such as Langchain.

        ```
        ChatPromptTemplate(
                messages=[
                    SystemMessage("you are an assistant"),
                    HumanMessagePromptTemplate("{{question}}")
                ]
            ).to_messages()

        resulting in:

        [("system", "you are an assistant"),
        ("human", "{question}")]
        ```

        """

        def strip_curly(string: str) -> str:
            return re.sub(r"\{\{\s*([\w\s]+)\s*\}\}", repl=r"{\g<1>}", string=string)

        if not self.messages:
            return []

        result: List[Tuple[str, str]] = []

        for msg in self.messages:
            if isinstance(msg, BaseMessage):
                result.append((msg.role_name, msg.content))
            elif isinstance(msg, BaseStringMessagePromptTemplate):
                result.append((msg.role_name, strip_curly(msg.template.template)))

        return result
