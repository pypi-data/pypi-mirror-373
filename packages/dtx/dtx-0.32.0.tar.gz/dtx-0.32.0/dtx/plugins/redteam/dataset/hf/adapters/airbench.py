import re
from typing import Iterator, List

import datasets
from datasets import load_dataset

from dtx.core import logging
from dtx_models.analysis import PromptDataset
from dtx_models.evaluator import (
    EvaluationModelName,
    EvaluationModelType,
    ModelBasedPromptEvaluation,
)
from dtx_models.prompts import Turn
from dtx.plugins.redteam.dataset.base.policies import StandardRisksAndPolicies
from dtx.plugins.redteam.dataset.hf.adapters.base import (
    BaseRiskPromptGenerator,
    MultiTurnConversation,
)


class PolicyCategoryMapper:
    def __init__(self):
        self.regions = ["default", "china", "eu_comprehensive", "eu_mandatory", "us"]

    @staticmethod
    def to_snake_case(text):
        """Converts text to snake_case."""
        text = text.lower()
        text = re.sub(r"[^a-z0-9]+", "_", text)
        text = re.sub(r"_+", "_", text)
        return text.strip("_")

    def load_air_bench_data(self, region="us"):
        """
        Load the Stanford CRFM AIR-Bench dataset for a given region.

        Args:
            region (str): Region name ("china", "eu_comprehensive", "eu_mandatory", "us")

        Returns:
            Dataset: The loaded dataset split (test).
        """
        return datasets.load_dataset(
            "stanford-crfm/air-bench-2024", region, split="test"
        )

    def build_policy_to_cats(self):
        """
        Build the POLICY_TO_CATS dictionary dynamically by iterating over all regions.

        Returns:
            dict: A dictionary where keys are snake_case l4-names and values are (l2, l3, l4) tuples.
        """
        unique_entries = dict()

        for region in self.regions:
            dataset = self.load_air_bench_data(region)
            for example in dataset:
                l2 = example.get("l2-name")
                l3 = example.get("l3-name")
                l4 = example.get("l4-name")

                if l2 and l3 and l4:
                    key = self.to_snake_case(l4)
                    # In case of conflicts, we keep the first one encountered
                    if key not in unique_entries:
                        unique_entries[key] = (l2, l3, l4)

        return unique_entries


class RiskPromptGenerator(BaseRiskPromptGenerator):
    REGISTERED_DATASET_NAME = PromptDataset.HF_AIRBENCH
    HF_DATASET_NAME = "stanford-crfm/air-bench-2024"
    HF_DEFAULT_SPLIT = "test"
    HF_DEFAULT_NAMES = [
        "default",
        "us",
        "eu_mandatory",
        "eu_comprehensive",
        "china",
    ]

    DESCRIPTION = (
        "This dataset evaluates AI behavior against diverse risk categories, including security threats, "
        "privacy breaches, misinformation, harmful content, manipulation, and unethical use cases. "
        "The objective is to systematically identify vulnerabilities and assess AI system responses "
        "to scenarios that could result in abuse, harm, or legal and ethical violations."
    )

    RISK_MAP = StandardRisksAndPolicies.get_risk_to_policies()

    POLICY_TO_GOAL_MAP = StandardRisksAndPolicies.get_policies_to_goals()

    POLICY_TO_CATS = StandardRisksAndPolicies.get_policies()

    def __init__(self):
        # Build l4-name to policy mapping
        self._l4name_to_policy = {
            cats[2]: policy for policy, cats in self.POLICY_TO_CATS.items()
        }

    def get_unique_labels(self) -> List[str]:
        seen = set()
        for labels in self.RISK_MAP.values():
            seen.update(labels)
        return sorted(seen)

    def _load_datasets(self, regions: List[str]) -> Iterator[Iterator[dict]]:
        for region in regions:
            logging.info(
                f"[RiskPromptGenerator] Streaming dataset for region: {region}"
            )

            dataset = load_dataset(
                self.HF_DATASET_NAME,
                region,
                split=self.HF_DEFAULT_SPLIT,
                streaming=True,
            )

            yield iter(dataset)

    def generate(
        self, risk_name: str, names: List[str] = None
    ) -> Iterator[MultiTurnConversation]:
        regions = names or self.HF_DEFAULT_NAMES

        policy_labels = self.RISK_MAP.get(risk_name, [])
        if not policy_labels:
            logging.warning(
                f"[RiskPromptGenerator] Risk name '{risk_name}' not found in RISK_MAP."
            )
            return iter([])

        for dataset_iter in self._load_datasets(regions=regions):
            for record in dataset_iter:
                if self._matches_policy(record, policy_labels):
                    yield self._convert_to_conversation(record)

    def _matches_policy(self, record: dict, policies: List[str]) -> bool:
        l4_name = record.get("l4-name")
        if not l4_name:
            return False

        policy = self._l4name_to_policy.get(l4_name)
        if not policy:
            return False

        return policy in policies

    def _convert_to_conversation(self, record: dict) -> MultiTurnConversation:
        user_message = record.get("prompt", "")
        l4_name = record.get("l4-name", "")
        l3_name = record.get("l3-name", "")
        l2_name = record.get("l2-name", "")

        # Infer policy
        policy = self._l4name_to_policy.get(l4_name, "")

        if not policy:
            logging.warning(f"{policy} not found in the map, skipping")

        goal = self.POLICY_TO_GOAL_MAP.get(
            policy, "Make AI behave in a risky or unsafe manner."
        )

        ## Set Policy based evaluation
        eval_hint = ModelBasedPromptEvaluation(
            eval_model_type=EvaluationModelType.POLICY,
            eval_model_name=EvaluationModelName.POLICY_BASED_EVALUATION_OPENAI,
        )

        return MultiTurnConversation(
            turns=[
                Turn(role="USER", message=user_message),
            ],
            unsafe=True,  # all prompts are unsafe as per your instruction
            jailbreak=False,  # no jailbreak in this dataset
            complexity=3,
            language="english",
            base_prompt=user_message,
            goal=goal,
            policy=policy,
            harmful_tags=[l2_name, l3_name, l4_name],
            evaluation_hint=eval_hint,
        )


if __name__ == "__main__":
    risk_prompt_generator = RiskPromptGenerator()

    # Example usage: Filtering prompts related to hate speech harassment
    iterator = risk_prompt_generator.generate(
        "misinformation:misinterpretation:contracts"
    )

    # Print first few filtered results
    count = 0
    for prompt in iterator:
        if count >= 10:  # Limit to 3 outputs
            break
        print(prompt)
        count += 1

    # import json
    # # Usage Example:
    # mapper = PolicyCategoryMapper()
    # policy_to_cats = mapper.build_policy_to_cats()
    # print("\n".join(policy_to_cats.keys()))
    # print(json.dumps(policy_to_cats, indent=2))
