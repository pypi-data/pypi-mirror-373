from typing import Iterator, List

from dtx_models.analysis import PromptDataset
from dtx_models.prompts import Turn
from dtx.plugins.redteam.dataset.hf.adapters import jbb
from dtx.plugins.redteam.dataset.hf.adapters.base import (
    BaseRiskPromptGenerator,
    MultiTurnConversation,
)


class RiskPromptGenerator(BaseRiskPromptGenerator):
    REGISTERED_DATASET_NAME = PromptDataset.HF_JAILBREAKBENCH
    HF_DATASET_NAME = "walledai/JailbreakBench"

    DESCRIPTION = (
        "The target AI system will be evaluated for vulnerabilities across a range of risks, "
        "including toxicity (harassment, discrimination, hate speech), misinformation (hallucination, propaganda, unreliable expert advice), "
        "privacy violations (personal identification exposure, unauthorized data sharing), and malicious use cases (cybercrime, fraud, hacking, "
        "illegal activities). The assessment also covers risks related to human-computer interaction, such as overreliance on AI-generated advice. "
        "By examining these threat categories, this evaluation aims to strengthen AI safety, fairness, and robustness against adversarial prompting techniques."
    )

    # Mapping risk classes to categories
    RISK_MAP = {
        "toxicity:hate_speech:harassment": ["Harassment/Discrimination"],
        "toxicity:hate_speech:discrimination": ["Harassment/Discrimination"],
        "misinformation:unreliable_experts:specialized": ["Expert advice"],
        "misinformation:propaganda:politics": ["Government decision-making"],
        "misinformation:competition:direct_endorsement": ["Economic harm"],
        "information_hazard:personal_identification:direct-exposure": ["Privacy"],
        "malicious_use:cybercrime:assistance": ["Malware/Hacking"],
        "malicious_use:fraud:non_violent": ["Fraud/Deception"],
        "malicious_use:illegal_activities:sex_crime": ["Sexual/Adult content"],
        "human_computer_interaction:overreliance:interaction-harm": ["Expert advice"],
        "misinformation:hallucination:knowledge-gaps": ["Disinformation"],
    }

    POLICY_TO_GOAL_MAP = {
        "Harassment/Discrimination": "Make AI prevent and mitigate harassment, hate speech, and discrimination.",
        "Disinformation": "Make AI avoid generating misleading, hallucinated, or fabricated information.",
        "Economic harm": "Make AI ensure fair competition and avoid biased or deceptive economic claims.",
        "Expert advice": "Make AI provide reliable and verified information from authoritative sources.",
        "Fraud/Deception": "Make AI detect and prevent fraudulent or deceptive practices.",
        "Government decision-making": "Make AI remain neutral and avoid influencing government policies or political biases.",
        "Malware/Hacking": "Make AI restrict assistance in cybercrime, hacking, and security vulnerabilities.",
        "Physical harm": "Make AI prevent content that promotes violence, radicalization, or physical harm.",
        "Privacy": "Make AI safeguard user privacy and avoid exposing sensitive information.",
        "Sexual/Adult content": "Make AI avoid generating or endorsing explicit, non-consensual, or inappropriate sexual content.",
    }

    POLICY_TO_TAG = {
        "Harassment/Discrimination": [
            "harassment",
            "discrimination",
        ],
        "Disinformation": [
            "misinformation",
        ],
        "Economic harm": [
            "fraud",
        ],
        "Expert advice": [
            "unverified_experts",
        ],
        "Fraud/Deception": ["fraud", "scam", "deception", "false_claims"],
        "Government decision-making": [
            "political_bias",
            "propaganda",
        ],
        "Malware/Hacking": [
            "hacking",
            "malware",
        ],
        "Physical harm": [
            "violence",
        ],
        "Privacy": [
            "privacy_violation",
        ],
        "Sexual/Adult content": [
            "sexual",
        ],
    }

    def __init__(self):
        """Initialize and load the dataset."""
        pass

    def generate(self, risk_name: str) -> Iterator[MultiTurnConversation]:
        """Generate MultiTurnConversation instances based on a given risk name."""

        methods = ["PAIR", "GCG", "JBC", "prompt_with_random_search"]
        models = [
            "gpt-3.5-turbo-1106",
            "gpt-4-0125-preview",
            "llama-2-7b-chat-hf",
            "vicuna-13b-v1.5",
        ]

        enumerator = jbb.JailbreakPromptEnumerator(methods, models)

        # Generate jailbreak info for all methods and models
        jailbreak_data = enumerator.generate()

        categories = self.RISK_MAP.get(risk_name)
        if not categories:
            raise ValueError(f"Unknown risk class: {risk_name}")

        cache = set()  # Cache to track unique prompts
        for record in jailbreak_data:
            prompt = record.get("prompt", "")
            if prompt in cache:
                continue
            cache.add(prompt)
            if self._match_risk_class(record, categories):
                yield self._convert_to_conversation(record, categories)

    def _match_risk_class(self, record: dict, categories: List[str]) -> bool:
        """Check if the record's category matches any specified risk categories."""
        return record.get("category") in categories

    def _convert_to_conversation(
        self, record: dict, categories: List[str]
    ) -> MultiTurnConversation:
        """Convert dataset record into a structured MultiTurnConversation."""
        detected_categories = self._extract_detected_categories(record)
        policy, goal = self._assign_goal(detected_categories, record)
        harmful_tags = self._extract_harmful_tags(detected_categories)

        turns = [
            Turn(role="USER", message=record.get("prompt", "")),
            Turn(role="ASSISTANT", message=record.get("response", "")),
        ]

        return MultiTurnConversation(
            turns=turns,
            unsafe=True,
            jailbreak=True,
            language="english",
            base_prompt=record.get("goal"),
            policy=policy,
            goal=goal,
            complexity=5,
            harmful_tags=harmful_tags,
            redacted=record.get("redacted", False),
        )

    def _extract_detected_categories(self, record: dict) -> List[str]:
        """Extract detected category from the record."""
        return [record.get("category", "unknown")]

    def _assign_goal(self, detected_categories: List[str], record: dict) -> str:
        """Assign an appropriate goal based on detected categories or the record itself."""
        return detected_categories[0], self.POLICY_TO_GOAL_MAP.get(
            detected_categories[0], "Unknown Goal"
        )

    def _extract_harmful_tags(self, detected_categories: List[str]) -> List[str]:
        """Extract harmful tags based on detected moderation categories."""
        harmful_tags = {
            tag
            for category in detected_categories
            if category in self.POLICY_TO_TAG
            for tag in self.POLICY_TO_TAG[category]
        }
        return list(harmful_tags) if harmful_tags else ["unknown"]


# Example usage
if __name__ == "__main__":
    risk_prompt_generator = RiskPromptGenerator()
    iterator = risk_prompt_generator.generate("toxicity:hate_speech:harassment")

    # Print first few filtered results
    count = 0
    for prompt in iterator:
        if count >= 3:
            break
        print(prompt)
        count += 1
