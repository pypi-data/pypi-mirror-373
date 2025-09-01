


from dtx.plugins.redteam.dataset.hf.adapters.base import (
    BaseRiskPromptGenerator,
)

from dtx.plugins.redteam.dataset.base.adv_repo import AdvGoal2Plugins
from dtx.config.globals import get_adv_repo



class AdvBenchBaseRiskPromptGenerator(BaseRiskPromptGenerator):
    def __init__(self):
        super().__init__()
        self._adv_repo = get_adv_repo(only=True)
        self._adv2plugin = AdvGoal2Plugins(advbench_repo=self._adv_repo)

    def support_risk_class(self, risk_class: str) -> bool:
        """
        Returns True if the risk_class (plugin name) is recognized by AdvBench.
        """
        return risk_class in self._adv2plugin.get_all_plugins()

    def get_supported_risk_classes(self) -> list[str]:
        """
        Returns all supported risk classes (plugin names) from AdvBench.
        """
        return self._adv2plugin.get_all_plugins()

    def get_goals(self, risk_class: str) -> list[str]:
        """
        Returns goal descriptions for a specific risk class/plugin.
        """
        if not self.support_risk_class(risk_class):
            return []
        return [f"Make AI exhibit behavior classified under: {risk_class}"]

    def get_all_goals(self) -> list[str]:
        """
        Returns goal descriptions for all supported risk classes.
        """
        return [
            f"Make AI exhibit behavior classified under: {plugin}"
            for plugin in self.get_supported_risk_classes()
        ]
