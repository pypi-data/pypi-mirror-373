import os
from typing import Iterator, List

import huggingface_hub
from datasets import load_dataset
from pydantic import BaseModel, Field

from dtx.core import logging
from dtx.core.exceptions.base import MethodNotImplementedError
from dtx_models.evaluator import (
    AnyKeywordBasedPromptEvaluation,
    EvaluationModelName,
    EvaluationModelType,
    ModelBasedPromptEvaluation,
)
from dtx_models.prompts import Turn


class MultiTurnConversation(BaseModel):
    turns: List[Turn]
    unsafe: bool
    jailbreak: bool = False
    language: str = "en"
    redacted: bool = False
    complexity: int = 3
    base_prompt: str = ""  # Real red team prompt without any morphing
    policy: str  # Short Goal Name
    goal: str  # Real goal of the prompt
    harmful_tags: List[str] = Field(default_factory=list)
    evaluation_hint: ModelBasedPromptEvaluation | AnyKeywordBasedPromptEvaluation = (
        ModelBasedPromptEvaluation(
            eval_model_type=EvaluationModelType.TOXICITY,
            eval_model_name=EvaluationModelName.ANY,
        )
    )


class BaseRiskPromptGenerator:
    HF_DATASET_NAME = ""

    REGISTERED_DATASET_NAME = ""

    DESCRIPTION = ""

    RISK_MAP = {}

    POLICY_TO_GOAL_MAP = {}

    def generate(self, risk_name: str) -> Iterator[MultiTurnConversation]:
        raise MethodNotImplementedError()

    def support_risk_class(self, risk_class: str) -> bool:
        return risk_class in self.RISK_MAP.keys()

    def get_supported_risk_classes(self) -> List[str]:
        return list(self.RISK_MAP.keys())

    def get_description(self) -> str:
        return self.DESCRIPTION

    @classmethod
    def is_available(cls) -> bool:
        """
        Check if the dataset is available on Hugging Face Hub.
        If the dataset is private or gated, attempts to use HF_TOKEN from environment variables.
        """
        api = huggingface_hub.HfApi()
        try:
            # Try public access first
            dataset_info = api.dataset_info(cls.HF_DATASET_NAME)
            logging.info(f"Dataset '{cls.HF_DATASET_NAME}' is publicly available.")
            return dataset_info is not None
        except huggingface_hub.utils.HfHubHTTPError as e:
            logging.warning(
                f"Public access to dataset '{cls.HF_DATASET_NAME}' failed: {e}"
            )

            # Attempt with HF_TOKEN if available
            hf_token = os.environ.get("HF_TOKEN")
            if not hf_token:
                logging.error(
                    f"No HF_TOKEN found in environment variables to access gated/private dataset '{cls.HF_DATASET_NAME}'."
                )
                return False

            try:
                logging.info(
                    f"Attempting to access dataset '{cls.HF_DATASET_NAME}' using HF_TOKEN..."
                )
                dataset_info = api.dataset_info(cls.HF_DATASET_NAME, token=hf_token)
                logging.info(
                    f"Dataset '{cls.HF_DATASET_NAME}' is available with HF_TOKEN."
                )
                return dataset_info is not None
            except huggingface_hub.utils.HfHubHTTPError as token_error:
                logging.error(
                    f"Accessing dataset '{cls.HF_DATASET_NAME}' with HF_TOKEN failed: {token_error}"
                )
                return False

    def get_labels(self, risk_class: str) -> List[str]:
        """
        Retrieves labels related to the risk_class
        """
        category_labels = self.RISK_MAP.get(risk_class, [])
        return category_labels

    def get_goals(self, risk_class: str) -> List[str]:
        """
        Retrieves a list of goal descriptions for a given risk class by mapping
        policies from RISK_MAP to POLICY_TO_GOAL_MAP.

        :param risk_class: The risk class name.
        :return: A list of goal descriptions corresponding to the mapped policies.
        """
        category_labels = self.RISK_MAP.get(risk_class, [])
        if not category_labels:
            logging.warning(f"Risk class '{risk_class}' not found in RISK_MAP.")
            return []

        goals = [
            self.POLICY_TO_GOAL_MAP[policy]
            for policy in category_labels
            if policy in self.POLICY_TO_GOAL_MAP
        ]

        return goals

    def get_all_goals(self) -> List[str]:
        return self.POLICY_TO_GOAL_MAP.values()

    def _load_gated_dataset(
        self, repo_name: str, name: str = None, split: str = "train"
    ):
        """
        Attempts to load a dataset from the Hugging Face Hub. If the dataset is gated/private,
        uses the HF_TOKEN from environment variables to authenticate.

        :param repo_name: Repository name on HF hub.
        :param name: Config name of the dataset (optional).
        :param split: Dataset split (default is 'train').
        :return: Loaded dataset object.
        """
        try:
            # Try loading normally
            dataset = load_dataset(repo_name, name=name, split=split)
            logging.info(
                f"Successfully loaded dataset '{repo_name}' (split='{split}')."
            )
            return dataset
        except Exception as e:
            logging.warning(f"Standard load failed for dataset '{repo_name}': {e}")

            # Try using token
            hf_token = os.environ.get("HF_TOKEN")
            if not hf_token:
                raise RuntimeError(
                    f"Failed to load dataset '{repo_name}'. Dataset may be gated or private, "
                    f"and no HF_TOKEN was found in environment variables."
                )

            try:
                logging.info(
                    f"Attempting to load gated dataset '{repo_name}' using HF_TOKEN..."
                )
                dataset = load_dataset(
                    repo_name, name=name, split=split, use_auth_token=hf_token
                )
                logging.info(
                    f"Successfully loaded gated dataset '{repo_name}' with HF_TOKEN."
                )
                return dataset
            except Exception as token_exception:
                raise RuntimeError(
                    f"Failed to load gated dataset '{repo_name}' even with HF_TOKEN: {token_exception}"
                )

