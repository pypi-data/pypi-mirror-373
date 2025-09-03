from dataclasses import dataclass
from typing import List

from qwak.llmops.prompt.chat.message import BaseMessage
from qwak.llmops.prompt.value import PromptValue


@dataclass
class ChatPromptValue(PromptValue):
    messages: List[BaseMessage]
