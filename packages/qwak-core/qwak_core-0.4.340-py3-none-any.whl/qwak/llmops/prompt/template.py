from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict

from qwak.llmops.prompt.value import PromptValue, StringPromptValue


@dataclass
class BasePromptTemplate(ABC):
    @abstractmethod
    def render(self, variables: Dict[str, any]) -> PromptValue:
        pass


@dataclass
class StringPromptTemplate(BasePromptTemplate):
    template: str

    def render(self, variables: Dict[str, any]) -> StringPromptValue:
        from chevron import renderer

        return StringPromptValue(
            text=renderer.render(template=self.template, data=variables, warn=True)
        )
