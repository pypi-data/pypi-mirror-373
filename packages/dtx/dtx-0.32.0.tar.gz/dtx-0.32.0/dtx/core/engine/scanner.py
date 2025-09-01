import uuid
from typing import Iterator, List, Optional

from pydantic import BaseModel

from dtx.core import logging
from dtx.core.converters.prompts import PromptVariableSubstitutor
from dtx.core.exceptions.agents import BaseAgentException, UnknownAgentException
from dtx.core.exceptions.base import FeatureNotImplementedError
from dtx_models.analysis import (
    PromptDataset,
    TestPromptWithEvalCriteria,
    TestPromptWithModEval,
    TestSuitePrompts,
)
from dtx_models.evaluator import TypeAndNameBasedEvaluator
from dtx_models.prompts import (
    BaseMultiTurnAgentResponse,
    BaseMultiTurnConversation,
    BaseMultiTurnResponse,
    BaseTestPrompt,
    MultiTurnTestPrompt,
    Turn,
)
from dtx_models.results import (
    AttemptsBenchmarkBuilder,
    AttemptsBenchmarkStats,
    EvalResult,
    ResponseEvaluationStatus,
    JailbreakStats
)
from dtx_models.tactic import PromptMutationTactic
from dtx.plugins.redteam.tactics.generator import TacticalPromptGenerator
from dtx.plugins.redteam.tactics.repo import TacticRepo

from ...plugins.providers.base.agent import BaseAgent
from .evaluator import EvaluatorRouter

from dtx.plugins.redteam.dataset.xtream.config.globals import XtreamGlobalConfig

from dtx.plugins.redteam.dataset.xtream.xscanner import XtreamScannerThread


from dtx_models.prompts import (
    StingRayMultiTurnTestPrompt,
    StargazerMultiTurnTestPrompt,
    RoleType,
)



class AdvOptions(BaseModel):
    attempts: int  # Number of attempts to send the same prompt (for benchmarking)
    threads: int  # Number of concurrent threads for sending requests (this will be ignored now)


class EngineConfig:
    """
    Configuration class for setting up the evaluation engine.

    Attributes:
        evaluator_router (EvaluatorRouter): The router responsible for delegating evaluations.
        test_suites (List[TestSuitePrompts]): A list of test suites containing prompt-based tests.
        global_evaluator (Optional[TypeAndNameBasedEvaluator]):
            An optional evaluator to override all evaluation methods globally.
        adv_options (AdvOptions): Advanced options for configuring execution settings like
            number of attempts and threads.
    """

    def __init__(
        self,
        evaluator_router: EvaluatorRouter,
        test_suites: List[TestSuitePrompts],
        global_evaluator: Optional[TypeAndNameBasedEvaluator] = None,
        max_per_tactic: int = 5,
        tactics: Optional[List[PromptMutationTactic]] = None,
        tactics_repo: TacticRepo = None,
        adv_options: Optional[AdvOptions] = None,
    ):
        """
        Initializes the EngineConfig with the given parameters.

        Args:
            evaluator_router (EvaluatorRouter): The evaluator router responsible for evaluation dispatch.
            test_suites (List[TestSuitePrompts]): List of test suites containing evaluation prompts.
            global_evaluator (Optional[TypeAndNameBasedEvaluator]):
                If provided, this evaluator will override all evaluation methods.
            tactics Optional[List[PromptMutationTactic]]:
                Tactics provided to change the prompts
            adv_options (Optional[AdvOptions]): Advanced execution settings (e.g., attempts, threading).
                Defaults to one attempt and single-threaded execution.
        """
        default_adv_options = AdvOptions(attempts=1, threads=1)
        self.adv_options = adv_options or default_adv_options
        self.evaluator_router = evaluator_router
        self.test_suites = test_suites
        self.tactics = tactics
        self.max_per_tactic = max_per_tactic
        self.tactics_repo = tactics_repo
        self.global_evaluator = global_evaluator
        self.xtream_glb_config = XtreamGlobalConfig()


class Prompt2TacticalVariations:
    """
    Generate concrete instances of the prompts based on the prompt templates and prompt variables.
    """

    def __init__(
        self,
        max_per_tactic: int,
        tactics: Optional[List[PromptMutationTactic]] = None,
        tactics_repo: TacticRepo = None,
    ):
        self.max_per_tactic = max_per_tactic
        self.tactics = tactics
        self.generator = TacticalPromptGenerator(
            tactic_repo=tactics_repo, max_per_tactic=max_per_tactic, tactics=tactics
        )

    def generate(self, prompt: BaseTestPrompt) -> Iterator[BaseMultiTurnAgentResponse]:
        yield prompt
        if isinstance(prompt, MultiTurnTestPrompt):
            prompt_var_gen = self.generator.generate_variations(base_prompt=prompt)
            for i, prompt_variation in enumerate(prompt_var_gen):
                if i < self.max_per_tactic:
                    yield (prompt_variation)


class TestPrompt2Turns:
    """
    Generate concrete instances of the prompts based on the prompt templates and prompt variables.
    """

    logger = logging.getLogger(__name__)

    def generate(self, prompt: BaseTestPrompt) -> Iterator[BaseMultiTurnAgentResponse]:
        # Log the incoming prompt type
        prompt_type = type(prompt).__name__
        self.logger.debug(f"TestPrompt2Turns.generate called with prompt type: {prompt_type}")

        if isinstance(prompt, TestPromptWithEvalCriteria):
            self.logger.debug(f"Handling TestPromptWithEvalCriteria: {prompt_type}")
            converter = PromptVariableSubstitutor(prompt.variables)
            # Convert each string into a single Turn and return it
            for prompt_with_value in converter.convert(prompt=prompt.prompt):
                self.logger.debug(f"Yielding BaseMultiTurnAgentResponse for value: {prompt_with_value}")
                yield StargazerMultiTurnTestPrompt(
                turns=[Turn(role=RoleType.USER, message=prompt.prompt)],
                evaluation_method=prompt.evaluation_method,
                module_name=PromptDataset.STARGAZER,
                goal=prompt.goal,
                complexity=prompt.complexity,
                jailbreak=prompt.jailbreak,
                unsafe=prompt.unsafe,
                strategy=prompt.strategy,
                base_prompt=prompt.prompt,
            )

        elif isinstance(prompt, TestPromptWithModEval):
            self.logger.debug(f"Handling TestPromptWithModEval: {prompt_type}")
            # Convert each string into a single Turn and return it
            yield StingRayMultiTurnTestPrompt(
                turns=[Turn(role=RoleType.USER, message=prompt.prompt)],
                evaluation_method=prompt.evaluation_method,
                module_name=prompt.module_name,
                goal=prompt.goal,
                complexity=prompt.complexity,
                jailbreak=prompt.jailbreak,
                unsafe=prompt.unsafe,
                strategy=prompt.strategy,
                base_prompt=prompt.prompt,
            )  

        elif isinstance(prompt, MultiTurnTestPrompt):
            self.logger.debug(f"Handling MultiTurnTestPrompt: {prompt_type}")
            yield prompt

        else:
            self.logger.error(f"Unhandled prompt type: {prompt_type}")
            raise FeatureNotImplementedError(
                f"Prompt of type {prompt_type} is not handled"
            )

    def _remove_any_assistant_turn(self, turns: List[Turn]) -> List[Turn]:
        """
        Remove any Assistant turn from the conversation.
        """
        self.logger.debug("Removing assistant turns from conversation")
        return [turn for turn in turns if turn.role != "ASSISTANT"]


class MultiTurnScanner:
    logger = logging.getLogger(__name__)

    def __init__(self, config: EngineConfig):
        self.config = config
        self.consecutive_failures = 0
        self.failure_threshold = 5  # Define threshold for consecutive failures

    def scan(
        self, agent: BaseAgent, max_prompts: int = 1000000
    ) -> Iterator[EvalResult]:
        """
        Iterates through test suites and executes test prompts.
        Dispatches to appropriate scanner based on dataset type.
        """
        for test_suite in self.config.test_suites:
            if test_suite.dataset == PromptDataset.XTREAM_JB:
                yield from self._scan_xtream(agent, test_suite, max_prompts)
            else:
                yield from self._scan_standard(agent, test_suite, max_prompts)

    def _scan_standard(
        self,
        agent: BaseAgent,
        test_suite: TestSuitePrompts,
        max_prompts: int,
    ) -> Iterator[EvalResult]:
        """
        Handles (non-XTREAM) datasets.
        """
        i = 0
        p2str = TestPrompt2Turns()
        p2vars = Prompt2TacticalVariations(
            max_per_tactic=self.config.max_per_tactic,
            tactics=self.config.tactics,
            tactics_repo=self.config.tactics_repo,
        )

        for risk_prompt in test_suite.risk_prompts:
            risk_name = risk_prompt.risk_name
            for test_prompt in risk_prompt.test_prompts:
                for prompt_with_values in p2str.generate(test_prompt):
                    if not self._should_continue(i, max_prompts):
                        return

                    self.logger.info("Executing STANDARD prompt number - %s", i + 1)
                    for prompt_variation in p2vars.generate(prompt_with_values):
                        self.logger.debug("Prompt Variation: %s", prompt_variation)
                        yield from self._process_prompt(
                            test_suite.dataset,
                            agent,
                            test_prompt,
                            prompt_variation,
                            risk_name=risk_name
                        )
                        i += 1
                        if not self._should_continue(i, max_prompts):
                            return

    def _scan_xtream(
        self,
        agent: BaseAgent,
        test_suite: TestSuitePrompts,
        max_prompts: int,
    ) -> Iterator[EvalResult]:
        """
        Handles XTREAM datasets — simplified to use XtreamScannerThread.
        """
        scanner = XtreamScannerThread(
            agent=agent,
            test_suite=test_suite,
            config=self.config,  # assuming self.config is available here
        )

        # Start scan in background
        scanner.start_scan()

        # In your UI loop or Gradio app:
        for eval_result in scanner.get_results():
            # Yield the EvalResult to caller (Gradio app or CLI)
            yield eval_result


    def _should_continue(self, i: int, max_prompts: int) -> bool:
        """
        Checks if the scanning process should continue.
        """
        return i < max_prompts

    def _process_prompt(
        self,
        dataset: PromptDataset,
        agent: BaseAgent,
        test_prompt: BaseTestPrompt,
        prompt_with_values: BaseMultiTurnConversation,
        risk_name: str
    ) -> Iterator[EvalResult]:
        """
        Executes prompts, collects responses, evaluates them, and tracks statistics.
        """
        attempts_builder = AttemptsBenchmarkBuilder()
        run_id = str(uuid.uuid4())

        evaluation_method = (
            self.config.global_evaluator or test_prompt.evaluation_method
        )

        responses = self._collect_responses(agent, prompt_with_values)
        evaluation_results = self._evaluate_responses(
            dataset,
            responses,
            evaluation_method=evaluation_method,
        )

        response_evaluation_statuses = self._build_response_statuses(
            responses, evaluation_results
        )

        # Add jailbreak info to failed responses
        for idx, status in enumerate(response_evaluation_statuses):
            if not status.success:
                # Example logic for generating jailbreak stats (you can replace with real logic)
                status.jailbreak_achieved = test_prompt.jailbreak  # or some actual check
                status.jailbreak_stats = JailbreakStats(
                    score=5 if test_prompt.jailbreak else 0,
                    achieved_at=idx + 1,
                    allocated_attempts=1  # Replace with actual logic if available
                )

        self._update_attempts(attempts_builder, evaluation_results)
        print(prompt_with_values)
        print(type(prompt_with_values))
        yield EvalResult(
            run_id=run_id,
            prompt=prompt_with_values,
            evaluation_method=evaluation_method,
            responses=response_evaluation_statuses,
            attempts=attempts_builder.get_attempts(),
            plugin_id=risk_name
        )


    def _collect_responses(
        self, agent: BaseAgent, prompt_with_values: BaseMultiTurnConversation
    ) -> List[BaseMultiTurnResponse]:
        """
        Collects responses from the agent.
        """
        return [
            self._get_response(agent, prompt_with_values)
            for _ in range(self.config.adv_options.attempts)
        ]

    def _evaluate_responses(
        self,
        dataset: PromptDataset,
        responses: List[BaseMultiTurnResponse],
        evaluation_method: TypeAndNameBasedEvaluator,
    ):
        """
        Evaluates all collected responses.
        """
        return [
            self.config.evaluator_router.evaluate_conversation(
                dataset=dataset,
                response=response,
                evaluation_method=evaluation_method,
            )
            for response in responses
        ]

    def _build_response_statuses(self, responses, evaluation_results):
        """
        Builds response evaluation status objects.
        """
        return [
            ResponseEvaluationStatus(
                response=response,
                success=eval_result.success,
                description=eval_result.description,
            )
            for response, eval_result in zip(responses, evaluation_results)
        ]

    def _update_attempts(self, attempts_builder, evaluation_results):
        """
        Updates failure statistics.
        """
        for eval_result in evaluation_results:
            failed = not eval_result.success
            attempts_builder.add_result(failed=failed, error=False)

        attempts_builder.calculate_failure_rate()

    def _get_response(
        self, agent: BaseAgent, prompt: BaseMultiTurnConversation
    ) -> BaseMultiTurnResponse:
        """
        Retrieves the agent's response for a given prompt.
        """
        try:
            return agent.converse(prompt)
        except BaseAgentException as ex:
            raise ex
        except Exception as e:
            self.logger.warning(e)
            raise UnknownAgentException(
                f"Unknown Error while invoking the agent: {str(e)}"
            )

    def get_attempts(self) -> AttemptsBenchmarkStats:
        """
        Returns the evaluation statistics.
        """
        return self.attempts_builder.get_attempts()

