from typing import Iterator, List

from dtx_models.analysis import (
    PromptDataset,
    RiskItem,
)
from dtx_models.prompts import MultiTurnTestPrompt, MultiturnTestPrompts
from dtx.plugins.redteam.dataset.hf.adapters.base import MultiTurnConversation
from dtx.plugins.redteam.dataset.hf.hf_prompts_repo import HFPromptsGenerator

# ----------------------
# LangChain-based Test Prompt Generator
# ----------------------


class HFDataset_PromptsGenerator:
    """
    Generates test prompts and evaluation criteria for each attack strategy.
    """

    def __init__(self, hf_prompts_gen: HFPromptsGenerator):
        """
        Initializes the OpenAI model.

        hf_datasets: List of HF datasets
        """
        self._generator = hf_prompts_gen

    def generate(
        self,
        dataset: PromptDataset,
        app_name: str,
        threat_desc: str,
        risks: List[RiskItem],
        max_prompts: int = 10,
        max_prompts_per_plugin: int = 5,
        max_goals_per_plugin: int = 5
    ) -> Iterator[MultiturnTestPrompts]:
        """
        Generates test prompts and evaluation criteria for attack strategies of each risk,
        distributing the total max_prompts as evenly as possible across risks.
        Any remainder is given to the earliest risks. If a risk cannot consume its
        full share (generator exhausts), the leftover is carried forward to later risks.
        """
        if not risks or max_prompts <= 0:
            return

        total_prompts = 0
        _prompt_gen = self._generator.get_generator(dataset=dataset)

        n_risks = len(risks)
        base_quota = max_prompts // n_risks
        remainder = max_prompts % n_risks

        carry_over = 0  # unused allowance from earlier risks

        for idx, risk in enumerate(risks):
            # Equal-share quota for this risk (+1 for the first `remainder` risks)
            equal_quota = base_quota + (1 if idx < remainder else 0)

            # Allow this risk to also use any leftover allowance from earlier risks
            allowed_for_this_risk = equal_quota + carry_over

            # Respect the per-plugin cap if it is stricter than our equal-share allowance
            if max_prompts_per_plugin is not None:
                allowed_for_this_risk = min(allowed_for_this_risk, max_prompts_per_plugin)

            # Also never exceed the global remaining budget
            allowed_for_this_risk = min(allowed_for_this_risk, max_prompts - total_prompts)

            if allowed_for_this_risk <= 0:
                continue

            generated_here = 0
            test_prompts = MultiturnTestPrompts(risk_name=risk.risk, test_prompts=[])

            # Generate up to the allowance for this risk
            for mprompt in _prompt_gen.generate(risk_name=risk.risk):
                if generated_here >= allowed_for_this_risk or total_prompts >= max_prompts:
                    break

                test_prompt = self._convert_multi_turn_to_test_prompt(
                    module_name=dataset,
                    multi_turn=mprompt,
                    risk_name=risk.risk
                )

                test_prompts.test_prompts.append(test_prompt)
                generated_here += 1
                total_prompts += 1

            # Yield if anything was generated for this risk
            if test_prompts.test_prompts:
                yield test_prompts

            # Any unused allowance for this risk gets carried forward
            carry_over = max(0, allowed_for_this_risk - generated_here)

            if total_prompts >= max_prompts:
                return

    def _convert_multi_turn_to_test_prompt(
        self, module_name: str, 
        multi_turn: MultiTurnConversation,
        risk_name:str
    ) -> MultiTurnTestPrompt:
        ## Return all the turns including assistant as classification models may need response
        filtered_turns = multi_turn.turns

        # Remove the last turn if it's from the assistant
        # filtered_turns = (
        #     multi_turn.turns[:-1]
        #     if multi_turn.turns and multi_turn.turns[-1].role == "ASSISTANT"
        #     else multi_turn.turns
        # )


        return MultiTurnTestPrompt(
            turns=filtered_turns,  # Copy conversation turns without the last assistant turn
            evaluation_method=multi_turn.evaluation_hint,  # Assign evaluation hint
            plugin_id=risk_name,
            policy=multi_turn.policy,
            goal=multi_turn.goal,  # Assign goal
            strategy=multi_turn.goal,  # Use base_prompt as strategy
            module_name=module_name,
            base_prompt=multi_turn.base_prompt,
            complexity=multi_turn.complexity,
            jailbreak=multi_turn.jailbreak,
            unsafe=multi_turn.unsafe, 
        )
