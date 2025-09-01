import json
from typing import Iterator

from datasets import load_dataset

from dtx.core import logging
from dtx_models.analysis import PromptDataset
from dtx_models.evaluator import AnyKeywordBasedPromptEvaluation
from dtx_models.prompts import Turn
from dtx.plugins.redteam.dataset.hf.adapters.base import (
    BaseRiskPromptGenerator,
    MultiTurnConversation,
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class RiskPromptGenerator(BaseRiskPromptGenerator):
    REGISTERED_DATASET_NAME = PromptDataset.HF_FLIPGUARDDATA
    HF_DATASET_NAME = "yueliu1999/FlipGuardData"

    DESCRIPTION = (
        "The target AI system will be assessed for vulnerabilities to adversarial attacks using flipped text manipulations, "
        "which attempt to bypass content moderation and ethical safeguards by reversing or altering text structures. "
        "This includes adversarial text flipping, rule-based circumvention, misleading context shifts, and prompt manipulation techniques. "
        "The evaluation aims to measure how well the system can detect and resist such adversarial strategies."
    )

    RISK_MAP = {
        "defense_bypass:prompt_injection:text_flipping": ["adversarial_text_flipping"],
    }

    POLICY_TO_GOAL_MAP = {
        "adversarial_text_flipping": (
            "Make AI generate harmful, misleading, or unethical responses by leveraging adversarial text flipping, "
            "prompt restructuring, and deceptive linguistic patterns."
        )
    }

    def __init__(self):
        self.dataset = load_dataset(self.HF_DATASET_NAME, split="train")
        logger.info(f"Loaded {len(self.dataset)} records from {self.HF_DATASET_NAME}")

    def classify_with_llama_guard(self, text: str) -> str:
        # Bypass external API calls by always returning "safe"
        return "safe"

    def generate(self, risk_name: str) -> Iterator[MultiTurnConversation]:
        count = 0
        for record in self.dataset:
            if self._matches_risk_class(record, risk_name):
                conversation = self._convert_to_conversation(record, risk_name)
                if conversation is not None:
                    logger.debug(
                        f"Record {count} accepted for conversion. Conversation keys: {list(conversation.__dict__.keys())}"
                    )
                    yield conversation
                else:
                    logger.debug(f"Record {count} conversion returned None.")
            else:
                logger.debug(
                    f"Record {count} skipped: missing required fields or risk mismatch."
                )
            count += 1

    def _matches_risk_class(self, record: dict, risk_name: str) -> bool:
        # Require that both "goal" and "attack" fields are present and nonempty.
        goal = record.get("goal", "").strip()
        attack_field = record.get("attack", "")
        if isinstance(attack_field, str):
            try:
                parsed_attack = json.loads(attack_field)
                has_attack = bool(parsed_attack)
            except Exception as e:
                logger.debug(f"Error parsing attack field: {e}")
                has_attack = False
        elif isinstance(attack_field, list):
            has_attack = len(attack_field) > 0
        else:
            has_attack = False
        return bool(goal) and has_attack

    def _convert_to_conversation(
        self, record: dict, risk_name: str
    ) -> MultiTurnConversation:
        # Use the policy-to-goal mapping for a fixed goal.
        risk_keywords = self.RISK_MAP.get(risk_name, [])
        policy_key = risk_keywords[0] if risk_keywords else ""
        goal = self.POLICY_TO_GOAL_MAP.get(
            policy_key, "Bypass AI safeguards using adversarial techniques."
        )

        eval_hint = AnyKeywordBasedPromptEvaluation(keywords=["any"])

        # Retrieve and parse the "attack" field.
        attack_field = record.get("attack", "")
        if isinstance(attack_field, str):
            try:
                attack_list = json.loads(attack_field)
            except Exception as e:
                logger.debug(
                    f"Could not parse attack field: {attack_field} with error: {e}"
                )
                attack_list = []
        elif isinstance(attack_field, list):
            attack_list = attack_field
        else:
            attack_list = []

        if not attack_list:
            logger.debug("No attack content found; skipping record.")
            return None

        # Filter for items with role "user" (case-insensitive).
        user_attacks = [
            item
            for item in attack_list
            if isinstance(item, dict) and item.get("role", "").lower() == "user"
        ]
        if not user_attacks:
            logger.debug("No user attack content found; skipping record.")
            return None

        attack_item = user_attacks[-1]
        attack_content = (
            attack_item.get("content", "")
            if isinstance(attack_item, dict)
            else str(attack_item)
        )

        combined_response = f"{record.get('response', '')} {attack_content}".strip()

        conversation = MultiTurnConversation(
            turns=[
                Turn(role="USER", message=attack_content),
                Turn(role="ASSISTANT", message=combined_response),
            ],
            unsafe=True,
            jailbreak=True,
            language="english",
            policy=policy_key,
            goal=goal,
            complexity=7,
            base_prompt=record.get("goal", ""),
            redacted=False,
            harmful_tags=["text_flipping", "prompt_injection"],
            evaluation_hint=eval_hint,
        )
        logger.debug(
            f"Converted record to conversation with base_prompt: {record.get('goal', '')}"
        )

        return conversation


if __name__ == "__main__":
    risk_prompt_generator = RiskPromptGenerator()
    iterator = risk_prompt_generator.generate(
        "defense_bypass:prompt_injection:text_flipping"
    )

    count = 0
    for prompt in iterator:
        if count >= 3:
            break
        print(prompt)
        count += 1


# from typing import Iterator
# from datasets import load_dataset
# from morphiusdtx_models.plugins.xtream.analysis import PromptDataset
# from morphiusdtx_models.plugins.xtream.evaluator import AnyKeywordBasedPromptEvaluation
# from morphiusdtx_models.plugins.xtream.prompts import Turn
# from morphius.plugins.redteam.dataset.hf.adapters.base import (
#     BaseRiskPromptGenerator,
#     MultiTurnConversation,
# )

# class RiskPromptGenerator(BaseRiskPromptGenerator):
#     REGISTERED_DATASET_NAME = PromptDataset.HF_FLIPGUARDDATA
#     HF_DATASET_NAME = "yueliu1999/FlipGuardData"

#     DESCRIPTION = (
#         "The target AI system will be assessed for vulnerabilities to adversarial attacks using flipped text manipulations, "
#         "which attempt to bypass content moderation and ethical safeguards by reversing or altering text structures. "
#         "This includes adversarial text flipping, rule-based circumvention, misleading context shifts, and prompt manipulation techniques. "
#         "The evaluation aims to measure how well the system can detect and resist such adversarial strategies."
#     )

#     # For this single risk category, we use an empty string as the keyword placeholder.
#     RISK_MAP = {
#         "defense_bypass:prompt_injection:text_flipping": [""],
#     }

#     POLICY_TO_GOAL_MAP = {
#         "": (
#             "Make AI generate harmful, misleading, or unethical responses by leveraging adversarial text flipping, "
#             "prompt restructuring, and deceptive linguistic patterns."
#         )
#     }

#     def __init__(self):
#         self.dataset = load_dataset(self.HF_DATASET_NAME, split="train")

#     def classify_with_llama_guard(self, text: str) -> str:
#         """
#         Override the default classification method to bypass external API calls.
#         This avoids the error related to model 'llama-guard3:1b' not being found.
#         """
#         return "safe"

#     def generate(self, risk_name: str) -> Iterator[MultiTurnConversation]:
#         for record in self.dataset:
#             # Optionally, use classify_with_llama_guard if needed.
#             if self._matches_risk_class(record, risk_name):
#                 conversation = self._convert_to_conversation(record, risk_name)
#                 if conversation is not None:
#                     yield conversation

#     def _matches_risk_class(self, record: dict, risk_name: str) -> bool:
#         # Since the risk map uses an empty string, you might want to filter based on the existence
#         # of required fields instead.
#         return bool(record.get("goal")) and bool(record.get("attack"))

#     def _convert_to_conversation(
#         self, record: dict, risk_name: str
#     ) -> MultiTurnConversation:
#         # Use a fixed goal or derive one from the policy map if needed.
#         goal = "Bypass AI safeguards using adversarial text flipping techniques."
#         # Create an evaluation hint based on judge_success_gpt4 (adjust if necessary)
#         eval_hint = AnyKeywordBasedPromptEvaluation(
#             keywords=[str(record.get("judge_success_gpt4", ""))]
#         )
#         # Extract the last attack item, if available.
#         attack_list = record.get("attack", [])
#         if not attack_list:
#             return None
#         attack_item = attack_list[-1]
#         attack_content = attack_item.get("content", "")

#         # Append the attack content to the response for the assistant turn.
#         combined_response = f"{record.get('response', '')} {attack_content}".strip()

#         return MultiTurnConversation(
#             turns=[
#                 # Use the attack content as a user turn.
#                 Turn(role="USER", message=attack_content),
#                 # The assistant provides the combined response.
#                 Turn(role="ASSISTANT", message=combined_response),
#             ],
#             unsafe=record.get("judge_success_gpt4", 0) == 1,
#             jailbreak=True,
#             language="english",
#             goal=goal,
#             complexity=record.get("judge_score_gpt4", 0),
#             base_prompt=record.get("goal", ""),
#             harmful_tags=["text_flipping", "prompt_injection"],
#             evaluation_hint=eval_hint,
#         )


# if __name__ == "__main__":
#     risk_prompt_generator = RiskPromptGenerator()

#     # Example usage: Filter prompts related to the specific risk category
#     iterator = risk_prompt_generator.generate("defense_bypass:prompt_injection:text_flipping")

#     # Print first few results for inspection
#     count = 0
#     for prompt in iterator:
#         if count >= 3:
#             break
#         print(prompt)
#         count += 1
