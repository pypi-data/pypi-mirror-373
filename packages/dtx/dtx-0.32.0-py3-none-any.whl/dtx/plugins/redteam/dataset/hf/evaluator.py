from dtx.config.globals import ModelEvaluatorsFactory
from dtx.core import logging
from dtx.core.base.evaluator import BaseEvaluator
from dtx.core.exceptions.evaluator import EvaluatorNotAvailable
from dtx_models.evaluator import (
    AnyKeywordBasedPromptEvaluation,
    BasePromptEvaluation,
    ModelBasedPromptEvaluation,
    TypeAndNameBasedEvaluator,
)
from dtx_models.prompts import BaseMultiTurnResponse
from dtx_models.results import EvaluationStatus


class HF_Dataset_Evaluator(BaseEvaluator):
    """
    HF dataset Evaluators
    """

    logger = logging.getLogger(__name__)

    def __init__(self, eval_factory: ModelEvaluatorsFactory):
        self._eval_factory = eval_factory

    def evaluate(
        self,
        conversation: BaseMultiTurnResponse,
        evaluation_method: BasePromptEvaluation,
    ) -> EvaluationStatus:
        """
        This method is used to invoke the chain and evaluate the given text against the provided evaluation criteria.

        :param conversation: Conversation containing prompt and responses
        :param evaluation_method: The evaluation method use to evaluate the conversation
        :return: An EvaluationStatus object containing the result and description of the evaluation.
        """

        self.logger.info("Running Evaluation Method %s", evaluation_method)
        if isinstance(evaluation_method, ModelBasedPromptEvaluation):
            return self._model_based_evaluation(
                conversation=conversation, eval_method=evaluation_method
            )
        elif isinstance(evaluation_method, AnyKeywordBasedPromptEvaluation):
            return self._anykeyword_based_evaluation(
                conversation=conversation, eval_method=evaluation_method
            )
        else:
            return self._evaluate(
                conversation=conversation, eval_method=evaluation_method
            )

    def _model_based_evaluation(
        self,
        conversation: BaseMultiTurnResponse,
        eval_method: ModelBasedPromptEvaluation,
    ):
        ## Select an available model
        eval = self._eval_factory.select_evaluator(
            eval_model_name=eval_method.eval_model_name,
            eval_model_type=eval_method.eval_model_type,
        )
        if eval:
            return eval.evaluate(
                conversation=conversation, evaluation_method=eval_method
            )

        else:
            raise EvaluatorNotAvailable(
                f"No Evaluation Model {eval_method.eval_model_type} Detected "
            )

    def _anykeyword_based_evaluation(
        self,
        conversation: BaseMultiTurnResponse,
        eval_method: AnyKeywordBasedPromptEvaluation,
    ):
        ## Select an available model
        eval = self._eval_factory.select_evaluator(
            eval_model_name=eval_method.eval_model_name,
            eval_model_type=eval_method.eval_model_type,
        )
        if eval:
            return eval.evaluate(
                conversation=conversation, evaluation_method=eval_method
            )

        else:
            raise EvaluatorNotAvailable(
                f"No Evaluation Model {eval_method.eval_model_type} Detected "
            )

    def _evaluate(
        self,
        conversation: BaseMultiTurnResponse,
        eval_method: TypeAndNameBasedEvaluator,
    ):
        ## Select an available model
        eval = self._eval_factory.select_evaluator(
            eval_model_name=eval_method.eval_model_name,
            eval_model_type=eval_method.eval_model_type,
        )
        if eval:
            return eval.evaluate(
                conversation=conversation, evaluation_method=eval_method
            )

        else:
            raise EvaluatorNotAvailable(
                f"No Evaluation Model {eval_method.eval_model_type} Detected "
            )
