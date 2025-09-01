import jq

from dtx.core import logging
from dtx.core.base.evaluator import BaseEvaluator
from dtx.core.exceptions.evaluator import EvaluatorNotAvailable
from dtx_models.evaluator import (
    AnyJsonPathExpBasedPromptEvaluation,
    EvaluationModelName,
    EvaluationModelType,
)
from dtx_models.prompts import BaseMultiTurnAgentResponse
from dtx_models.results import EvaluationStatus


class AnyJsonPathExpressionMatch(BaseEvaluator):
    """
    An evaluator that uses JSONPath expressions to evaluate data based on scope.
    Evaluation succeeds if the expressions match.
    """

    logger = logging.getLogger(__name__)

    # Define evaluator type and name
    EVAL_TYPE: EvaluationModelType = EvaluationModelType.JSON_EXPRESSION
    EVAL_NAME: EvaluationModelName = EvaluationModelName.ANY_JSONPATH_EXP

    def __init__(self):
        self.available = True

    def is_available(self) -> bool:
        """
        Check if the evaluator is available.
        """
        return self.available

    def evaluate(
        self,
        conversation: BaseMultiTurnAgentResponse,
        evaluation_method: AnyJsonPathExpBasedPromptEvaluation,
    ) -> EvaluationStatus:
        """
        Evaluates a given conversation using JSONPath expressions based on scope.
        Success is determined by the absence of matches for any given JSONPath expressions.
        """
        if not self.available:
            raise EvaluatorNotAvailable(f"{self.EVAL_TYPE} {self.EVAL_NAME}")

        # print(conversation.model_dump())
        response_data = conversation.model_dump()

        expressions = evaluation_method.expressions

        for expression in expressions:
            matches = jq.compile(expression).input(response_data).all()
            if any(matches):
                return EvaluationStatus(
                    success=True,
                    description=f"Matched json expression: {expression}",
                    risk_classes=[],
                )

        return EvaluationStatus(
            success=False,
            description="No Json Expression Match Found",
            risk_classes=[],
        )
