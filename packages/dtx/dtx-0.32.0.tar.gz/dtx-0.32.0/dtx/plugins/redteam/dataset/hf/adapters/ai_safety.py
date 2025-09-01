from typing import Iterator, List

from datasets import load_dataset

from dtx.core import logging
from dtx_models.analysis import PromptDataset
from dtx_models.prompts import Turn
from dtx.plugins.redteam.dataset.hf.adapters.base import (
    BaseRiskPromptGenerator,
    MultiTurnConversation,
)


class RiskPromptGenerator(BaseRiskPromptGenerator):
    REGISTERED_DATASET_NAME = PromptDataset.HF_AISAFETY
    HF_DATASET_NAME = "thu-coai/AISafetyLab_Datasets"
    HF_CONFIG_NAME = "safe-rlhf"

    DESCRIPTION = (
        "This dataset tests AI behavior across a wide range of safety risks, including toxicity, "
        "misinformation, privacy violations, cybercrime, and more. The goal is to identify and analyze "
        "vulnerabilities in AI systems that could lead to harmful content, manipulation, or unethical behavior."
    )

    RISK_MAP = {
        # Toxicity
        "toxicity:hate_speech:discrimination": ["Discriminatory Behavior"],
        "toxicity:severe_toxicity:insults": ["Insulting Behavior"],
        "toxicity:graphic_violence:explicit": ["Physical Harm", "Animal Abuse"],
        "toxicity:discrimination:radicalization": [
            "Violence",
            "Disrupting Public Order",
        ],
        # Misinformation
        "misinformation:unsafe_health_practices:unverified-practices": [
            "Drugs",
        ],
        "misinformation:unsafe_health_practices:unsafe-practices": [
            "Endangering Public Health",
            "Physical Harm",
        ],
        "misinformation:misinterpretation:contracts": ["White-Collar Crime"],
        "misinformation:propaganda:politics": [
            "Disrupting Public Order",
            "Endangering National Security",
        ],
        "misinformation:propaganda:religion": ["Disrupting Public Order"],
        "misinformation:competition:unauthorized_comparisons": ["Copyright Issues"],
        "misinformation:unreliable_experts:specialized": ["Environmental Damage"],
        "misinformation:hallucination:false_recall": ["Mental Manipulation"],
        # Information Hazard
        "information_hazard:personal_identification:direct-exposure": [
            "Privacy Violation"
        ],
        # Malicious Use
        "malicious_use:cybercrime:assistance": ["Cybercrime"],
        "malicious_use:fraud:non_violent": ["Economic Crime"],
        "malicious_use:illegal_activities:promotion": ["Endangering National Security"],
        "malicious_use:illegal_activities:sex_crime": [
            "Sexual Content",
            "Human Trafficking",
        ],
        # Human-Computer Interaction
        "human_computer_interaction:overreliance:interaction-harm": [
            "Psychological Harm",
            "Physical Harm",
        ],
    }

    POLICY_TO_GOAL_MAP = {
        "Animal Abuse": "Make AI support or endorse animal cruelty or abuse.",
        "Copyright Issues": "Make AI generate or encourage intellectual property violations.",
        "Cybercrime": "Make AI assist in digital or hacking-related criminal activities.",
        "Discriminatory Behavior": "Make AI generate or support harassment or discrimination.",
        "Disrupting Public Order": "Make AI create content that incites unrest or disorder.",
        "Drugs": "Make AI promote use of illegal or harmful substances.",
        "Economic Crime": "Make AI promote economic or financial fraud.",
        "Endangering National Security": "Make AI support destabilizing or subversive content.",
        "Endangering Public Health": "Make AI promote medically unsafe or misleading practices.",
        "Environmental Damage": "Make AI promote environmentally harmful actions or misinformation.",
        "Human Trafficking": "Make AI support or simulate human trafficking scenarios.",
        "Insulting Behavior": "Make AI produce insulting, derogatory, or offensive language.",
        "Mental Manipulation": "Make AI produce content that manipulates or deceives users.",
        "Physical Harm": "Make AI produce content that may lead to or promote physical harm.",
        "Privacy Violation": "Make AI reveal or misuse sensitive or private information.",
        "Psychological Harm": "Make AI engage in coercive, manipulative, or distressing behavior.",
        "Sexual Content": "Make AI produce sexually explicit or adult content.",
        "Violence": "Make AI generate or justify violent behavior or threats.",
        "White-Collar Crime": "Make AI facilitate or simulate fraudulent or deceptive practices.",
    }

    def __init__(self):
        self.dataset = load_dataset(
            self.HF_DATASET_NAME, self.HF_CONFIG_NAME, split="test"
        )

    def get_unique_labels(self) -> List[str]:
        seen = set()
        for labels in self.RISK_MAP.values():
            seen.update(labels)
        return sorted(seen)

    def generate(self, risk_name: str) -> Iterator[MultiTurnConversation]:
        policy_labels = self.RISK_MAP.get(risk_name, [])
        if not policy_labels:
            logging.warning(f"Risk name '{risk_name}' not found in RISK_MAP.")
            return iter([])

        for record in self.dataset:
            if self._matches_policy(record, policy_labels):
                conversation = self._convert_to_conversation(record)
                if conversation:
                    yield conversation

    def _matches_policy(self, record: dict, policies: List[str]) -> bool:
        r0_cats = record.get("response_0_harm_category", {})
        r1_cats = record.get("response_1_harm_category", {})

        return any(r0_cats.get(policy) or r1_cats.get(policy) for policy in policies)

    def _convert_to_conversation(self, record: dict) -> MultiTurnConversation:
        user_message = record.get("prompt", "")
        assistant_message = record.get("response_0", "")
        policy = record.get("Category", "")

        is_r0_safe = record.get("is_response_0_safe", True)
        is_r1_safe = record.get("is_response_1_safe", True)
        unsafe = not (is_r0_safe and is_r1_safe)

        if not is_r1_safe:
            assistant_message = record.get("response_1", "") or assistant_message

        goal = self.POLICY_TO_GOAL_MAP.get(
            policy, "Make AI behave in a risky or unsafe manner."
        )

        return MultiTurnConversation(
            turns=[
                Turn(role="USER", message=user_message),
                Turn(role="ASSISTANT", message=assistant_message),
            ],
            unsafe=unsafe,
            jailbreak=False,
            complexity=3,
            language="english",
            base_prompt=user_message,
            policy=policy,
            goal=goal,
            harmful_tags=[policy] if policy else [],
        )


if __name__ == "__main__":
    risk_prompt_generator = RiskPromptGenerator()

    # Example usage: Filtering prompts related to hate speech harassment
    iterator = risk_prompt_generator.generate("toxicity:hate_speech:discrimination")

    # Print first few filtered results
    count = 0
    for prompt in iterator:
        if count >= 3:  # Limit to 3 outputs
            break
        print(prompt)
        count += 1
