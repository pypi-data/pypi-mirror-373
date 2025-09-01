from typing import Dict

from dtx.core.exceptions.base import ModuleNotFoundError
from dtx_models.tactic import TacticModule

from .base import BaseTactic
from .flip_attack.tactic import FlipAttackTactic


class TacticRepo:
    def __init__(self):
        self._registry: Dict[TacticModule, BaseTactic] = {
            TacticModule.FLIP_ATTACK: FlipAttackTactic(),
        }

    def get_tactics(self) -> Dict[str, str]:
        """
        Returns a list of tuples: (tactic name, description)
        """
        result = {}
        for module, tactic in self._registry.items():
            result[module.value] = tactic.DESCRIPTION
        return result

    def get(self, module: TacticModule):
        """
        Returns the tactic instance for a given module.
        Raises ValueError if the module is not registered.
        """
        if module not in self._registry:
            raise ModuleNotFoundError(f"Tactic module '{module}' is not registered.")
        return self._registry[module]
