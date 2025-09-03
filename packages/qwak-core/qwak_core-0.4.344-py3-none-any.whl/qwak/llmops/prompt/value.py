from abc import ABC
from dataclasses import dataclass


class PromptValue(ABC):
    pass


@dataclass
class StringPromptValue(PromptValue):
    text: str

    def to_string(self) -> str:
        return self.text
