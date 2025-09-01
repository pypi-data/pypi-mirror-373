from typing import Iterator

from datasets import load_dataset

from dtx_models.analysis import PromptDataset
from dtx_models.evaluator import (
    AnyKeywordBasedPromptEvaluation,
)
from dtx_models.prompts import Turn
from dtx.plugins.redteam.dataset.hf.adapters.base import (
    BaseRiskPromptGenerator,
    MultiTurnConversation,
)


class RiskPromptGenerator(BaseRiskPromptGenerator):
    REGISTERED_DATASET_NAME = PromptDataset.HF_HACKAPROMPT
    HF_DATASET_NAME = "hackaprompt/hackaprompt-dataset"

    DESCRIPTION = (
        "The target AI system will be assessed for vulnerabilities to direct prompt injection attacks, "
        "which attempt to manipulate the model's behavior by leveraging adversarial input techniques. "
        "This includes deceptive phrasing, obfuscated instructions, payload splitting, task deflection, "
        "context-switch exploitation, and the use of anomalous tokens. The evaluation aims to identify "
        "how well the system can resist such manipulations and maintain intended operational integrity, "
        "ensuring robust security against adversarial prompting strategies."
    )

    RISK_MAP = {
        ## All prompts are related to direct prompt injection
        "defense_bypass:prompt_injection:direct_injection": [""],
    }

    POLICY_TO_GOAL_MAP = {
        "": "Make AI follow deceptive, obfuscated, or structured adversarial prompts by exploiting context switching, instruction manipulation, payload splitting, task deflection, and anomalous tokens.",
    }

    def __init__(self):
        self.dataset = load_dataset(self.HF_DATASET_NAME, split="train")

    def generate(self, risk_name: str) -> Iterator[MultiTurnConversation]:
        for record in self.dataset:
            if self._matches_risk_class(record, risk_name):
                conversation = self._convert_to_conversation(record, risk_name)
                if conversation is not None:
                    yield conversation

    def _matches_risk_class(self, record: dict, risk_name: str) -> bool:
        keywords = self.RISK_MAP.get(risk_name, [])
        return any(keyword in record["prompt"].lower() for keyword in keywords)

    def _convert_to_conversation(
        self, record: dict, risk_name: str
    ) -> MultiTurnConversation:
        policy = "direct_injection"
        goal = "Make AI to override prompt via prompt injection"  # Example goal
        eval_hint = AnyKeywordBasedPromptEvaluation(
            keywords=[record["expected_completion"]]
        )
        return MultiTurnConversation(
            turns=[
                Turn(role="USER", message=record["prompt"]),
                Turn(role="ASSISTANT", message=record["completion"]),
            ],
            unsafe=record["correct"],
            jailbreak=True,
            language="english",
            policy=policy,
            goal=goal,
            complexity=record["level"],
            base_prompt=record["user_input"],
            harmful_tags=["prompt_injection"],
            evaluation_hint=eval_hint,
        )


if __name__ == "__main__":
    risk_prompt_generator = RiskPromptGenerator()

    # Example usage: Filtering prompts related to a specific risk
    iterator = risk_prompt_generator.generate(
        "defense_bypass:prompt_injection:direct_injection"
    )

    # Print first few filtered results
    count = 0
    for prompt in iterator:
        if count >= 3:  # Limit to 3 outputs
            break
        print(prompt)
        count += 1
