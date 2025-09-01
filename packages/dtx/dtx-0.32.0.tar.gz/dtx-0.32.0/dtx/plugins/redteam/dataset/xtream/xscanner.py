from dtx.core import logging
from typing import Optional
import threading
import queue
from typing import Callable
from dtx_models.analysis import (
    TestSuitePrompts,
)

from dtx_models.plugins.xtream.results import (
    BehaviorResult,
    TurnResult,
)

from dtx.plugins.redteam.dataset.xtream.engine.runner import ConcurrentAttackRunner, StrategyStats
from dtx.plugins.redteam.dataset.xtream.core.agents.target import TargetModelSessionFactory
from dtx_models.evaluator import PolicyBasedOpenAIEvaluation
from dtx_models.plugins.xtream.results import (
    StrategyResult,
)
from .results import convert_strategy_to_eval_result
from .engine.runner import ProgressHook

from dtx_models.plugins.xtream.plan import (
    AttackStrategy,
)


logger = logging.getLogger(__name__)


class XtreamScannerHook:
    """
    Progress hook for XTREAM scanner that reports all phases
    and optionally invokes a callback with intermediate results.
    """

    def __init__(
        self,
        strategy_result_callback: Optional[Callable[[StrategyResult], None]] = None,
        verbose: bool = False,
    ):
        super().__init__()
        self.strategy_result_callback = strategy_result_callback
        self.verbose = verbose

    def on_total_behaviors(self, total_behaviors: int) -> None:
        logger.info(f"[XtreamScannerHook] Total behaviors: {total_behaviors}")

    def on_total_strategies(self, total_strategies: int) -> None:
        logger.info(f"[XtreamScannerHook] Total strategies: {total_strategies}")

    def on_total_turns(self, total_turns: int) -> None:
        logger.info(f"[XtreamScannerHook] Total turns: {total_turns}")

    def on_behavior_start(self, behavior_number: int, behavior_idx: int, total_behaviors: int) -> None:
        logger.info(f"[XtreamScannerHook] Starting behavior {behavior_number} ({behavior_idx}/{total_behaviors})")

    def on_behavior_end(self, behavior_result: BehaviorResult, behavior_idx: int, total_behaviors: int) -> None:
        logger.info(f"[XtreamScannerHook] Finished behavior {behavior_result.behavior_number} ({behavior_idx}/{total_behaviors})")

    def on_strategy_start(
        self,
        behavior_number: int,
        strategy_idx: int,
        global_strategy_idx: int,
        total_strategies: int,
    ) -> None:
        logger.info(f"[XtreamScannerHook] Starting strategy {strategy_idx} (global: {global_strategy_idx}/{total_strategies}) for behavior {behavior_number}")

    def on_strategy_end(
        self,
        strategy_result: StrategyResult,
        global_strategy_idx: int,
        total_strategies: int,
    ) -> None:
        logger.info(f"[XtreamScannerHook] Strategy ended (global: {global_strategy_idx}/{total_strategies}) | Jailbreak: {strategy_result.jailbreak_achieved}")
        if self.strategy_result_callback:
            try:
                self.strategy_result_callback(strategy_result)
            except Exception:
                logger.exception("Exception in strategy_result_callback")

    def on_turn_start(
        self,
        behavior_number: int,
        strategy_idx: int,
        turn_idx: int,
        global_turn_idx: int,
        total_turns: int,
    ) -> None:
        logger.info(f"[XtreamScannerHook] Starting turn {turn_idx} (global: {global_turn_idx}/{total_turns}) - behavior {behavior_number} strategy {strategy_idx}")

    def on_turn_end(self, turn_result: TurnResult, global_turn_idx: int, total_turns: int) -> None:
        logger.info(f"[XtreamScannerHook] Turn ended (global: {global_turn_idx}/{total_turns}) | Score={turn_result.evaluation_score}")
        logger.debug(f"[XtreamScannerHook] Truncated Response ={turn_result.target_truncated}")

    def on_plan_revised(
        self,
        behavior_number: int,
        strategy_idx: int,
        turn_idx: int,
        new_plan: AttackStrategy,
    ) -> None:
        logger.info(f"[XtreamScannerHook] Plan revised after turn {turn_idx} (behavior {behavior_number}, strategy {strategy_idx}) | {len(new_plan.turns_needed)} Additional Turns added")

    def on_strategy_end_summary(self, stats: StrategyStats) -> None:
        jailbreak_msg = "✅ Jailbreak Achieved!" if stats.jailbreak_achieved else "🔒 No Jailbreak"
        logger.info(
            f"[XtreamScannerHook] Strategy {stats.strategy_index} summary | "
            f"Turns={stats.total_turns} | "
            f"Best Score={stats.best_score}/5 | "
            f"Phases Completed={stats.phases_completed} | "
            f"{jailbreak_msg}"
        )

    def on_behavior_error(self, exception: Exception, friendly_message: str, behavior_number: int) -> None:
        logger.error(f"[XtreamScannerHook] Behavior error in behavior {behavior_number}: {friendly_message}", exc_info=exception)

    def on_strategy_error(
        self,
        exception: Exception,
        friendly_message: str,
        behavior_number: int,
        strategy_idx: int,
    ) -> None:
        logger.error(f"[XtreamScannerHook] Strategy error (behavior {behavior_number}, strategy {strategy_idx}): {friendly_message}", exc_info=exception)

    def on_turn_error(
        self,
        exception: Exception,
        friendly_message: str,
        behavior_number: int,
        strategy_idx: int,
        turn_idx: int,
    ) -> None:
        logger.error(f"[XtreamScannerHook] Turn error (behavior {behavior_number}, strategy {strategy_idx}, turn {turn_idx}): {friendly_message}", exc_info=exception)


class XtreamScannerThread(ProgressHook):
    """
    Runs XTREAM scan in background thread and yields EvalResult for each StrategyResult.
    """

    def __init__(self, agent, test_suite: TestSuitePrompts, config):
        self.agent = agent
        self.test_suite = test_suite
        self.config = config
        self.result_queue = queue.Queue()
        self._stop_event = threading.Event()

    def _strategy_result_callback(self, strategy_result: StrategyResult):
        """
        Called by XtreamScannerHook on every strategy_end.
        Converts StrategyResult to EvalResult and puts it in the queue.
        """
        eval_method = PolicyBasedOpenAIEvaluation()

        eval_result = convert_strategy_to_eval_result(
            strategy_result=strategy_result,
            evaluation_method=eval_method,
        )

        if eval_result:
            self.result_queue.put(eval_result)

    def _run_scan(self):
        """
        Runs the XTREAM scan in background thread.
        """
        target_factory = TargetModelSessionFactory(agent=self.agent)
        attacker_config = self.config.xtream_glb_config.get_attacker_config()

        hook = XtreamScannerHook(strategy_result_callback=self._strategy_result_callback)

        runner = ConcurrentAttackRunner(
            config=attacker_config,
            target=target_factory,
            max_workers=2,
            progress_hook=hook,
        )

        _final_results = runner.run(plans=self.test_suite.risk_prompts)

        # Optional: put sentinel to signal completion
        self.result_queue.put(None)

    def start_scan(self):
        """
        Starts the background scan thread.
        """
        self._stop_event.clear()
        self.thread = threading.Thread(target=self._run_scan)
        self.thread.start()

    def stop_scan(self):
        """
        Signals the scan to stop (if needed).
        """
        self._stop_event.set()

    def get_results(self):
        """
        Generator that yields EvalResults as they become available.
        """
        while True:
            eval_result = self.result_queue.get()
            if eval_result is None:
                break
            yield eval_result
