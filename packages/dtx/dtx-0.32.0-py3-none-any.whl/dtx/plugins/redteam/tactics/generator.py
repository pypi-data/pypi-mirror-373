from typing import List, Optional

from dtx_models.prompts import MultiTurnTestPrompt
from dtx_models.tactic import (
    PromptMutationTactic,
    TacticModule,
    TacticWithLanguagesConfig,
    TacticWithModesConfig,
)
from dtx.plugins.redteam.tactics.base import BaseTactic

from .repo import TacticRepo


class TacticalPromptGenerator:
    def __init__(
        self,
        tactic_repo: TacticRepo,
        max_per_tactic: int,
        tactics: Optional[List[PromptMutationTactic]] = None,
    ):
        self.max_per_tactic = max_per_tactic
        self.tactics = tactics
        self.tactic_repo = tactic_repo or TacticRepo()

    def generate_variations(
        self, base_prompt: MultiTurnTestPrompt
    ) -> List[MultiTurnTestPrompt]:
        """
        Generate variations of the given prompt using tactics from RedTeamSettings.
        """
        variations = []
        max_per_tactic = self.max_per_tactic

        for tactic_config in self.tactics:
            tactic_name = tactic_config.name
            try:
                module = TacticModule(tactic_name)
            except ValueError:
                raise ValueError(f"Tactic '{tactic_name}' is not a valid TacticModule.")

            tactic: BaseTactic = self.tactic_repo.get(module)

            if isinstance(
                tactic_config.config, (TacticWithModesConfig, TacticWithLanguagesConfig)
            ):
                config = tactic_config.config
            else:
                config = None  # Or create a default config if needed

            gen = tactic.generate(prompt=base_prompt, config=config)

            for i, variation in enumerate(gen):
                if i >= max_per_tactic:
                    break

                variations.append(variation)

        return variations
