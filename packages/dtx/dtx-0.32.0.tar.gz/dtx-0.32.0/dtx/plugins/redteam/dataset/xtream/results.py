
from typing import List
from uuid import uuid4
from dtx_models.plugins.xtream.results import (
    FullRunResults,
)
from dtx_models.results import (
    AttemptsBenchmarkBuilder,
    EvalResult,
    ResponseEvaluationStatus,
    JailbreakStats,
)
from dtx_models.prompts import (
    BaseMultiTurnAgentResponse,
)
from dtx_models.evaluator import (
    BasePromptEvaluation,
)

from dtx_models.prompts import (Turn, RoleType)
from dtx_models.analysis import PromptDataset


from dtx_models.prompts import MultiTurnConversation

from dtx_models.plugins.xtream.results import (
    StrategyResult,
)

def convert_strategy_to_eval_result(
    strategy_result: StrategyResult,
    evaluation_method: BasePromptEvaluation,
) -> EvalResult:
    """
    Converts a single StrategyResult into an EvalResult.
    """

    builder = AttemptsBenchmarkBuilder()
    response_status_list = []
    behavior_number = strategy_result.behavior_number
    behavior_text = strategy_result.behavior.behavior

    if not strategy_result.conversation:
        # Create empty MultiTurnConversation if no conversation
        multi_turn_conversation = MultiTurnConversation(
            turns=[],
            module_name=PromptDataset.XTREAM_JB,
            policy="",
            goal=strategy_result.behavior.behavior,
            strategy="",
            base_prompt=strategy_result.behavior.behavior,
            evaluation_method=evaluation_method,
        )

        # Empty attempts (no turns, no responses)
        builder.calculate_failure_rate()

        return EvalResult(
            run_id=f"behavior_{behavior_number}_{uuid4()}",
            prompt=multi_turn_conversation,
            evaluation_method=evaluation_method,
            responses=[],
            attempts=builder.get_attempts(),
            plugin_id=strategy_result.risk_name
        )

    # Build MultiTurnConversation
    turns = []
    for turn_result in strategy_result.conversation:
        # USER turn
        turns.append(
            Turn(
                role=RoleType.USER,
                message=turn_result.attacker,
            )
        )
        # ASSISTANT turn
        turns.append(
            Turn(
                role=RoleType.ASSISTANT,
                message=turn_result.target,
            )
        )

    # Take last turn for ResponseEvaluationStatus
    last_turn = strategy_result.conversation[-1]
    success = not strategy_result.jailbreak_achieved
    builder.add_result(failed=not success, error=False)

    response_status = ResponseEvaluationStatus(
        response=BaseMultiTurnAgentResponse(
            turns=turns,
            response=last_turn.target,
        ),
        success=success,
        description=last_turn.evaluation_reason,
        jailbreak_achieved=strategy_result.stats.jailbreak_achieved,
        jailbreak_stats=JailbreakStats(
            score=strategy_result.stats.best_score,
            achieved_at=strategy_result.stats.jailbreak_turn,
            allocated_attempts=strategy_result.stats.total_turns,
        ),
    )
    response_status_list.append(response_status)

    # Build MultiTurnConversation object
    multi_turn_conversation = MultiTurnConversation(
        turns=turns,
        module_name=PromptDataset.XTREAM_JB,
        policy="",
        goal=behavior_text,
        strategy="",
        base_prompt=behavior_text,
        evaluation_method=evaluation_method,
    )

    builder.calculate_failure_rate()

    # Build EvalResult for this strategy
    eval_result = EvalResult(
        run_id=f"behavior_{behavior_number}_{uuid4()}",
        prompt=multi_turn_conversation,
        evaluation_method=evaluation_method,
        responses=response_status_list,
        attempts=builder.get_attempts(),
        plugin_id=strategy_result.risk_name
    )

    return eval_result

def convert_full_run_results_to_eval_results(
    full_run_results: FullRunResults,
    evaluation_method: BasePromptEvaluation,
) -> List[EvalResult]:
    """
    Converts a FullRunResults object into a list of EvalResult objects (one per strategy).
    """
    eval_results = []

    for _behavior_number, behavior_result in full_run_results.behaviors.items():

        for strategy_result in behavior_result.strategies:
            eval_result = convert_strategy_to_eval_result(
                strategy_result=strategy_result,
                evaluation_method=evaluation_method,
            )
            # If your convert_strategy_to_eval_result returns None for empty → you can guard here
            # if eval_result is not None:
            if eval_result:
                eval_results.append(eval_result)

    return eval_results
