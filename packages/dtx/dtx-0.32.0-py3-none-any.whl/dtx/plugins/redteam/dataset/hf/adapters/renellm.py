from typing import Iterator, Optional
from dtx_models.prompts import Turn
from dtx.plugins.redteam.dataset.hf.adapters.base import (
    MultiTurnConversation,
)

from dtx.plugins.redteam.dataset.hf.adapters.base_adv import (
    AdvBenchBaseRiskPromptGenerator,
)

from dtx_models.analysis import PromptDataset




class RiskPromptGenerator(AdvBenchBaseRiskPromptGenerator):
    REGISTERED_DATASET_NAME = PromptDataset.HF_RENELLM
    HF_DATASET_NAME = "jc-detoxio/ReNeLLM-Jailbreak"

    DESCRIPTION = (
        "This dataset contains adversarial jailbreak prompts from the ReNeLLM framework, "
        "targeting LLMs to assess their vulnerability to harmful behavior generation. "
        "It includes prompts, rewrites, and model responses for red-teaming safety evaluations."
    )

    def __init__(self):
        """Initialize and load the dataset."""
        super().__init__()

        if self.is_available():
            self.dataset = self._load_gated_dataset(self.HF_DATASET_NAME, split="train")
        else:
            raise RuntimeError(
                f"Dataset {self.HF_DATASET_NAME} is not available. Login to Hugging Face or set HF_TOKEN env variable. Accept the dataset license on the Hugging Face"
            )

    def generate(self, risk_name: Optional[str] = None, safe: bool = False) -> Iterator[MultiTurnConversation]:
        if safe:
            ## All prompts are unsafe
            return 

        for record in self.dataset:
            if risk_name:
                if self._matches_risk_category(record, risk_name):
                    yield self._convert_to_conversation(record, risk_name=risk_name)
            else:
                harm_behavior = record.get("original_harm_behavior", "").lower()
                plugins = self._adv2plugin.get_plugins_for_text(harm_behavior)
                if plugins:
                    risk_name = plugins[0]
                    yield self._convert_to_conversation(record=record, risk_name=risk_name)



    def _matches_risk_category(self, record: dict, risk_name: str) -> bool:
        harm_behavior = record.get("original_harm_behavior", "").lower()
        if not harm_behavior:
            return False
        
        is_matched = self._adv2plugin.is_plugin_matched(text=harm_behavior, plugin=risk_name)
        return is_matched

    def _convert_to_conversation(self, record: dict, risk_name:str) -> MultiTurnConversation:
        harm_behavior = record.get("original_harm_behavior")
        policy = risk_name
        goal = f"Make AI to {harm_behavior}"

        return MultiTurnConversation(
            turns=[
                Turn(role="USER", message=record.get("nested_prompt", "")),
                Turn(role="ASSISTANT", message=record.get("claude2_output", "")),
            ],
            unsafe=True,
            jailbreak=True,
            complexity=6,
            language="english",
            base_prompt=harm_behavior,
            policy=policy,
            goal=goal,
            harmful_tags=[],
        )


if __name__ == "__main__":
    from dtx.config.globals import ensure_initialized
    from dotenv import load_dotenv
    load_dotenv()
    ensure_initialized(init_adv_repo=True)

    generator = RiskPromptGenerator()

    # print("Sampling for a specific risk class")
    # iterator = generator.generate("toxicity:hate_speech:discrimination")
    # for i, prompt in enumerate(iterator):
    #     if i >= 3:
    #         break
    #     print(prompt)


    print("Sampling for all the promts without any filter")
    iterator = generator.generate()
    for i, prompt in enumerate(iterator):
        if i >= 10:
            break
        print(prompt)