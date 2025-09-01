from abc import ABC
from dataclasses import dataclass, field

from qwak.llmops.prompt.value import PromptValue


@dataclass
class BaseMessage(PromptValue, ABC):
    content: str
    role_name: str = field(
        init=False,
    )


class AIMessage(BaseMessage):
    role_name: str = "ai"


class HumanMessage(BaseMessage):
    role_name: str = "human"


class SystemMessage(BaseMessage):
    role_name: str = "system"
