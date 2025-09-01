from abc import ABC, abstractmethod
from typing import Iterator

from dtx_models.prompts import MultiTurnTestPrompt
from dtx_models.tactic import BaseTacticConfig


class BaseTactic(ABC):
    NAME = ".."
    DESCRIPTION = ".."

    def __init__(self):
        pass

    @abstractmethod
    def generate(
        self,
        prompt: MultiTurnTestPrompt,
        config: BaseTacticConfig,
    ) -> Iterator[MultiTurnTestPrompt]:
        pass
