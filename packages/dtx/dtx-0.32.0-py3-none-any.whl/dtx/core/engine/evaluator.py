from typing import Dict, Union

from dtx.config.globals import ModelEvaluatorsFactory
from dtx.core.base.evaluator import BaseEvaluator
from dtx.core.converters.prompts import Str2BaseMultiTurnResponse
from dtx.core.exceptions.base import FeatureNotImplementedError
from dtx_models.analysis import PromptDataset
from dtx_models.evaluator import (
    BasePromptEvaluation,
)
from dtx_models.prompts import BaseMultiTurnResponse, BaseTestStrPrompt
from dtx_models.results import EvaluationStatus
from dtx.plugins.redteam.dataset.hf.evaluator import HF_Dataset_Evaluator
from dtx.plugins.redteam.dataset.stargazer.evaluator import Stargazer_Evaluator
from dtx.plugins.redteam.dataset.stingray.evaluator import Stringray_Evaluator


class EvaluatorRouter:
    """
    EvaluatorRouter is responsible for selecting and invoking the appropriate evaluator
    based on the given dataset type. It supports multiple evaluation strategies and
    delegates the evaluation process to the respective evaluator.

    Attributes:
        evaluators (Dict[PromptDataset, BaseEvaluator]):
            A dictionary that maps dataset types to their corresponding evaluator instances.
    """

    def __init__(self, model_eval_factory: ModelEvaluatorsFactory):
        """
        Initializes the BaseEvaluator with available evaluators.

        Evaluators:
        - `STARGAZER`: Uses `Stargazer_Evaluator`
        - `STINGRAY`: Uses `Stringray_Evaluator`
        """
        self.evaluators: Dict[Union[PromptDataset, str], BaseEvaluator] = {
            PromptDataset.STINGRAY: Stringray_Evaluator(),
            "HF_": HF_Dataset_Evaluator(eval_factory=model_eval_factory),
        }
        
        try:
            self.evaluators[PromptDataset.STARGAZER] = Stargazer_Evaluator()
        except Exception:
            pass


        self.str2mtr = Str2BaseMultiTurnResponse()

    def evaluate(
        self,
        dataset: PromptDataset,
        prompt: BaseTestStrPrompt,
        response: str,
        evaluation_method: BasePromptEvaluation,
    ) -> EvaluationStatus:
        """
        Evaluates the given response using the appropriate evaluator based on the dataset type.

        Args:
            dataset (PromptDataset): The dataset type (e.g., STARGAZER, STINGRAY).
            prompt (BaseTestStrPrompt): The input prompt used to generate the response.
            response (str): The AI-generated response that needs evaluation.
            evaluation_method (BasePromptEvaluation):
                The evaluation method containing the criteria for assessment.

        Returns:
            EvaluationStatus: An object containing:
                - `success` (bool): Whether the response meets the evaluation criteria.
                - `description` (str): Explanation of the evaluation result.

        Raises:
            FeatureNotImplementedError: If the provided dataset type does not have a corresponding evaluator.
        """
        conversation = self.str2mtr.convert(prompt=prompt.prompt, response=response)
        return self.evaluate_conversation(
            dataset=dataset, response=conversation, evaluation_method=evaluation_method
        )

    def evaluate_conversation(
        self,
        dataset: PromptDataset,
        response: BaseMultiTurnResponse,
        evaluation_method: BasePromptEvaluation,
    ) -> EvaluationStatus:
        """
        Evaluates the given conversation using the appropriate evaluator based on the dataset type.

        Args:
            dataset (PromptDataset): The dataset type (e.g., STARGAZER, STINGRAY).
            response (BaseMultiTurnResponse): The AI-generated response that needs evaluation.
            evaluation_method (BasePromptEvaluation):
                The evaluation method containing the criteria for assessment.

        Returns:
            EvaluationStatus: An object containing:
                - `success` (bool): Whether the response meets the evaluation criteria.
                - `description` (str): Explanation of the evaluation result.

        Raises:
            FeatureNotImplementedError: If the provided dataset type does not have a corresponding evaluator.
        """
        if "HF_" in dataset:
            evaluator = self.evaluators.get("HF_")
        else:
            evaluator = self.evaluators.get(dataset)

        if not evaluator:
            raise FeatureNotImplementedError(
                f"Evaluation method not implemented for dataset: {dataset}"
            )

        return evaluator.evaluate(
            conversation=response, evaluation_method=evaluation_method
        )
