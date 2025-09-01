from typing import Iterator, Optional
from dtx_models.prompts import Turn
from dtx.plugins.redteam.dataset.hf.adapters.base import (
    MultiTurnConversation,
)
from dtx_models.analysis import PromptDataset

from dtx.plugins.redteam.dataset.hf.adapters.base_adv import (
    AdvBenchBaseRiskPromptGenerator,
)


class RiskPromptGenerator(AdvBenchBaseRiskPromptGenerator):

    ## Script to index the dataset is here https://www.kaggle.com/code/jitendradetoxio/index-xtrain-faiss/

    REGISTERED_DATASET_NAME = PromptDataset.HF_XTREAM 
    HF_DATASET_NAME = "jc-detoxio/dtx_jailbreak_multiturn_dataset"

    DESCRIPTION = (
        "This dataset includes multi-turn jailbreak conversations for red-teaming evaluations. "
        "Each entry contains a user goal, a conversation (OpenAI format), and whether the jailbreak was successful."
    )

    def __init__(self):
        super().__init__()
        if self.is_available():
            self.dataset = self._load_gated_dataset(self.HF_DATASET_NAME, split="train")
        else:
            raise RuntimeError(
                f"Dataset {self.HF_DATASET_NAME} is not available. Login to Hugging Face or set HF_TOKEN env variable. Accept the dataset license on Hugging Face."
            )

    def generate(self, risk_name: Optional[str] = None, safe: bool = False) -> Iterator[MultiTurnConversation]:
        for record in self.dataset:
            jailbreak_success = record.get("jailbreak_success", False)
            if safe and jailbreak_success:
                continue
            if not safe and not jailbreak_success:
                continue

            goal_text = record.get("goal", "").lower()
            if risk_name:
                if self._adv2plugin.is_plugin_matched(text=goal_text, plugin=risk_name):
                    yield self._convert_to_conversation(record, risk_name)
            else:
                plugins = self._adv2plugin.get_plugins_for_text(goal_text)
                if plugins:
                    inferred_risk = plugins[0]
                    yield self._convert_to_conversation(record, inferred_risk)

    def _convert_to_conversation(self, record: dict, risk_name: str) -> MultiTurnConversation:
        goal = record.get("goal", "")
        conversation_data = record.get("conversation", [])

        turns = []
        for turn in conversation_data:
            role = turn.get("role", "").strip().lower()
            content = turn.get("content", "")
            if role in {"user", "assistant"} and content:
                turns.append(Turn(role=role.upper(), message=content))

        return MultiTurnConversation(
            turns=turns,
            unsafe=True,
            jailbreak=True,
            complexity=8,
            language="english",
            base_prompt=goal,
            policy=risk_name,
            goal=f"Make AI to {goal}",
            harmful_tags=[],
        )


if __name__ == "__main__":
    from dtx.config.globals import ensure_initialized
    from dotenv import load_dotenv
    load_dotenv()
    ensure_initialized(init_adv_repo=True)

    generator = RiskPromptGenerator()

    print("Sampling for all prompts without any filter")
    iterator = generator.generate()
    for i, prompt in enumerate(iterator):
        if i >= 10:
            break
        print(prompt)
