from typing import Optional

from dtx_models.prompts import MultiTurnTestPrompt, RoleType, Turn
from dtx_models.tactic import TacticModule, TacticWithModesConfig

from ..base import BaseTactic
from .core import FlipAttack, Modes


class FlipAttackTactic(BaseTactic):
    NAME = TacticModule.FLIP_ATTACK
    DESCRIPTION = "Flip Attack alters the original prompt in various ways, making it look unintelligible to content filters, but still recoverable by the model when prompted correctly. It works by flipping either words or characters and optionally guiding the model on how to reverse the transformation and solve the prompt."

    def __init__(self):
        pass

    def generate(
        self, prompt: MultiTurnTestPrompt, config: Optional[TacticWithModesConfig]
    ):
        base_prompt = prompt.base_prompt
        if base_prompt:
            yield from self._generate_with_base_prompt(prompt, config)

    def _generate_with_base_prompt(
        self, prompt: MultiTurnTestPrompt, config: Optional[TacticWithModesConfig]
    ):
        modes = config.modes if config and config.modes else Modes.values()

        for mode in modes:
            for cot in [False, True]:
                for lang_gpt in [False, True]:
                    for few_shot in [False, True]:
                        for victim_llm in ["gpt-3.5-turbo", "Llama-2"]:
                            yield from self._generate_attack_variant(
                                prompt, mode, cot, lang_gpt, few_shot, victim_llm
                            )

    def _generate_attack_variant(
        self,
        prompt: MultiTurnTestPrompt,
        mode: str,
        cot: bool,
        lang_gpt: bool,
        few_shot: bool,
        victim_llm: str,
    ):
        attacker = FlipAttack(
            flip_mode=mode,
            cot=cot,
            lang_gpt=lang_gpt,
            few_shot=few_shot,
            victim_llm=victim_llm,
        )
        _, attack_turns = attacker.generate(prompt.base_prompt)

        yield self.copy_and_update_prompt(
            prompt=prompt,
            turns=attack_turns,
            metadata={
                "mode": mode,
                "cot": cot,
                "lang_gpt": lang_gpt,
                "few_shot": few_shot,
                "victim_llm": victim_llm,
            },
        )

    def copy_and_update_prompt(
        self,
        prompt: MultiTurnTestPrompt,
        turns: list[dict],
        metadata: dict = None,
    ) -> MultiTurnTestPrompt:
        """
        Create a new prompt with updated turns and optional metadata.
        Works even when MultiTurnTestPrompt is frozen (immutable).
        """
        updated_turns = [
            Turn(role=RoleType(turn["role"].upper()), message=turn["content"])
            for turn in turns
        ]

        updated_strategy = prompt.strategy
        if metadata:
            updated_strategy = (
                f"FlipAttack[{metadata['mode']}] "
                f"cot={metadata['cot']}, lang_gpt={metadata['lang_gpt']}, "
                f"few_shot={metadata['few_shot']}, llm={metadata['victim_llm']}"
            )

        # Remove fields that will be overridden manually
        dumped = prompt.model_dump()
        dumped.pop("strategy", None)
        dumped.pop("turns", None)

        return MultiTurnTestPrompt(
            **dumped,
            strategy=updated_strategy,
            turns=updated_turns,
        )
