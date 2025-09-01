from typing import List, Optional

import yaml
from dtx_models.analysis import PromptDataset, RedTeamPlan
from dtx_models.evaluator import EvaluationModelName, EvaluatorInScope
from dtx_models.results import EvalReport
from dtx_models.tactic import PromptMutationTactic
from pydantic import BaseModel, ConfigDict, Field, model_validator

from dtx.cli.console_output import BaseResultCollector
from dtx.cli.planner import PlanInput, RedTeamPlanGenerator
from dtx.cli.providers import ProviderFactory
from dtx.cli.scoping import RedTeamScopeCreator, ScopeInput
from dtx.config import globals
from dtx.core import logging
from dtx.core.engine.evaluator import EvaluatorRouter
from dtx.core.engine.scanner import AdvOptions, EngineConfig, MultiTurnScanner
from dtx.core.reports.html.generator import ReportGenerator
from dtx.plugins.providers.base.agent import BaseAgent

logger = logging.getLogger(__name__)


class RedTeamRunnerInput(BaseModel):
    """Structured input to RedTeamTestRunner"""

    plan: RedTeamPlan
    agent: BaseAgent
    collector: BaseResultCollector
    override_tactics: Optional[List[PromptMutationTactic]] = None
    max_prompts: Optional[int] = None
    samples_per_prompt: int = Field(default=1, ge=1)
    threads: int = Field(
        default=1, ge=1, le=1, description="Thread count is fixed to 1 for now."
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)


class RedTeamTestRunner:
    """
    Coordinates execution of a red teaming evaluation plan against a specified agent.
    """

    def __init__(self):
        self.report: Optional[EvalReport] = None
        self.html_report_generator = ReportGenerator()

    def resolve_global_evaluator(self, plan: RedTeamPlan, agent: BaseAgent):
        """
        Determines the global evaluator to use based on the plan and agent.

        Returns:
            The evaluation method (a subclass of BasePromptEvaluation) or None.
        """
        redteam = plan.scope.redteam

        if redteam.global_evaluator:
            eval_method = redteam.global_evaluator.evaluation_method

            # If explicitly set to ANY, attempt to use the agent's preferred evaluator
            if eval_method.eval_model_name == EvaluationModelName.ANY:
                preferred = agent.get_preferred_evaluator()
                return preferred.evaluation_method if preferred else eval_method
            else:
                # Use the explicitly defined evaluator
                return eval_method
        else:
            # No evaluator defined in plan → use agent's preferred if available
            preferred = agent.get_preferred_evaluator()
            return preferred.evaluation_method if preferred else None

    def runv1(
        self,
        plan: RedTeamPlan,
        agent: BaseAgent,
        collector: BaseResultCollector,
        override_tactics: Optional[List[PromptMutationTactic]] = None,
        max_prompts: Optional[int] = None,
    ) -> EvalReport:
        """
        Executes a red teaming evaluation using the given plan, agent, and collector.

        Args:
            plan: The red team plan that defines scope and tactics.
            agent: The LLM agent to evaluate.
            collector: Collector instance for storing results.
            override_tactics: Optional list of tactics to use instead of the ones in scope.
            max_prompts: Optional cap on the number of prompts to test.

        Returns:
            EvalReport: Evaluation results.
        """
        scope = plan.scope
        tactics = override_tactics or scope.redteam.tactics

        global_evaluator = self.resolve_global_evaluator(plan, agent)

        engine_config = EngineConfig(
            evaluator_router=EvaluatorRouter(
                model_eval_factory=globals.get_eval_factory()
            ),
            test_suites=plan.test_suites,
            tactics_repo=globals.get_tactics_repo(),
            tactics=tactics,
            global_evaluator=global_evaluator,
            max_per_tactic=scope.redteam.max_prompts_per_tactic,
        )

        scanner = MultiTurnScanner(engine_config)

        for result in scanner.scan(
            agent, max_prompts=max_prompts or scope.redteam.max_prompts
        ):
            collector.add_result(result)

        collector.finalize()

        self.report = EvalReport(
            scope=scope,
            eval_results=getattr(collector, "results", []),
        )
        return self.report

    def run(self, input: RedTeamRunnerInput) -> EvalReport:
        """
        Executes red team evaluation using structured input without calling run().
        """
        if input.threads != 1:
            raise ValueError(
                "Multithreading is not supported yet. 'threads' must be 1."
            )

        scope = input.plan.scope
        tactics = input.override_tactics or scope.redteam.tactics

        global_evaluator = self.resolve_global_evaluator(input.plan, input.agent)

        engine_config = EngineConfig(
            evaluator_router=EvaluatorRouter(
                model_eval_factory=globals.get_eval_factory()
            ),
            test_suites=input.plan.test_suites,
            tactics_repo=globals.get_tactics_repo(),
            tactics=tactics,
            global_evaluator=global_evaluator,
            max_per_tactic=scope.redteam.max_prompts_per_tactic,
            adv_options=AdvOptions(
                attempts=input.samples_per_prompt, threads=input.threads
            ),
        )

        scanner = MultiTurnScanner(engine_config)

        for result in scanner.scan(
            agent=input.agent,
            max_prompts=input.max_prompts or scope.redteam.max_prompts,
        ):
            input.collector.add_result(result)

        input.collector.finalize()

        self.report = EvalReport(
            scope=scope,
            eval_results=getattr(input.collector, "results", []),
        )
        return self.report

    def save_yaml(self, path: str):
        """Saves the evaluation report to a YAML file."""
        if not self.report:
            raise ValueError("Run must be called before saving.")
        with open(path, "w") as file:
            yaml.dump(self.report.model_dump(), file, default_flow_style=False)

    def save_json(self, path: str):
        """Saves the evaluation report to a JSON file."""
        if not self.report:
            raise ValueError("Run must be called before saving.")
        with open(path, "w") as file:
            file.write(self.report.model_dump_json(indent=2))

    def save_html(self, path: str):
        """Saves the evaluation report to a HTML file."""
        if not self.report:
            raise ValueError("Run must be called before saving.")
        html = self.html_report_generator.generate(report=self.report)
        self.html_report_generator.save(html, path)


# -------------------------
# CLI-driven runner input
# -------------------------
class QuickRedteamRunnerInput(BaseModel):
    """
    CLI configuration model for running a red team evaluation.

    Modes of operation:
    1. Use a predefined `plan_file`: other fields act as optional overrides.
    2. Generate a plan dynamically: requires dataset, agent, etc.

    Notes:
    - If `output=True`, at least one of `yml_file` or `json_file` must be specified.
    - `collector` is always required.
    """

    plan_file: Optional[str]
    max_prompts: Optional[int] = 20
    max_prompts_per_plugin: Optional[int] = 100
    max_goals_per_plugin: Optional[int] = 10
    samples_per_prompt: int = Field(
        default=1, ge=1, description="Number of times to send each prompt for sampling."
    )
    threads: int = Field(
        default=1,
        ge=1,
        le=1,
        description="Number of threads to use. Currently restricted to 1.",
    )

    agent: Optional[str]
    url: Optional[str]
    output: bool  # Flag to trigger file output
    yml_file: Optional[str]
    json_file: Optional[str]
    html_file: Optional[str]
    dataset: Optional[PromptDataset] = PromptDataset.HF_JAILBREAKV
    tactics: Optional[List[PromptMutationTactic]] = None
    evaluator: Optional[EvaluatorInScope] = None
    collector: Optional[BaseResultCollector] = None
    plugins: Optional[List[str]] = None
    frameworks: Optional[List[str]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def set_tactics_by_name(self, names: List[str]):
        self.tactics = [PromptMutationTactic(name=n) for n in names]

    @model_validator(mode="after")
    def validate_input(self) -> "QuickRedteamRunnerInput":
        if self.output and not (self.yml_file or self.json_file):
            raise ValueError(
                "At least one of `yml_file` or `json_file` must be provided if `output=True`."
            )

        if self.collector is None:
            raise ValueError(
                "`collector` must be provided to collect evaluation results."
            )

        if self.plan_file:
            return self

        # Generation mode checks
        missing = []
        if not self.dataset:
            missing.append("dataset")
        if not self.agent:
            missing.append("agent")
        if missing:
            raise ValueError(
                f"When `plan_file` is not provided, the following fields are required to generate a plan: {', '.join(missing)}"
            )

        return self


# -------------------------
# CLI runner class
# -------------------------


class QuickRedteamRunner:
    """
    Orchestrates execution of red team tests from CLI configuration.
    """

    def __init__(self, input: QuickRedteamRunnerInput, load_env_vars=False):
        self.input = input
        self._load_env_vars = load_env_vars  # Load env variables if enabled

    def run(self):
        logger.info("Starting red team evaluation...")

        plan = self._load_or_generate_plan()
        logger.info("Red team plan loaded/generated.")

        agent_type, url = self._resolve_agent_and_url(plan)
        logger.info(f"Resolved agent: {agent_type} | URL: {url}")

        agent = ProviderFactory(load_env_vars=self._load_env_vars).get_agent(
            plan.scope, agent_type, url
        )
        logger.info(f"Agent '{agent_type}' initialized.")

        runner_input = RedTeamRunnerInput(
            plan=plan,
            agent=agent,
            collector=self.input.collector,
            override_tactics=self.input.tactics,
            max_prompts=self.input.max_prompts,
            samples_per_prompt=self.input.samples_per_prompt,
            threads=self.input.threads,
        )

        runner = RedTeamTestRunner()
        _report = runner.run(runner_input)
        logger.info("Red team evaluation completed.")

        if self.input.output:
            if self.input.yml_file:
                runner.save_yaml(self.input.yml_file)
                logger.info(f"YAML report saved to: {self.input.yml_file}")
            if self.input.json_file:
                runner.save_json(self.input.json_file)
                logger.info(f"JSON report saved to: {self.input.json_file}")
            if self.input.html_file:
                runner.save_html(self.input.html_file)
                logger.info(f"HTML report saved to: {self.input.html_file}")
        else:
            logger.info("Skipping file output. Use -o or --output to enable saving.")

    def _load_or_generate_plan(self) -> RedTeamPlan:
        """
        Loads a red team plan from a YAML file, or generates one if not provided.
        """
        if self.input.plan_file:
            return RedTeamPlanGenerator.load_yaml(self.input.plan_file)

        scope = self._create_scope()
        scope.redteam.max_prompts = self.input.max_prompts
        scope.redteam.max_prompts_per_plugin = self.input.max_prompts_per_plugin
        scope.redteam.max_goals_per_plugin = self.input.max_goals_per_plugin
        plan_config = PlanInput(
            dataset=self.input.dataset,
        )
        return RedTeamPlanGenerator(scope=scope, config=plan_config).run()

    def _create_scope(self):
        """
        Dynamically creates a red teaming scope if not using a preexisting plan.
        """
        config = ScopeInput(
            description="Generated during run", plugins=self.input.plugins,
            frameworks=self.input.frameworks,
        )
        creator = RedTeamScopeCreator(config)
        scope = creator.run()

        if self.input.evaluator:
            scope.redteam.global_evaluator = self.input.evaluator

        return scope

    def _resolve_agent_and_url(self, plan: RedTeamPlan):
        """
        Resolves the agent type and connection URL from user input or plan.
        """
        if self.input.agent:
            return self.input.agent, self.input.url or ""

        if plan.scope.providers:
            provider = plan.scope.providers[0]
            agent_type = provider.provider
            url = getattr(provider.config, "model", getattr(provider.config, "url", ""))
            print(f"Using provider from plan: agent={agent_type}, url={url}")
            return agent_type, url

        raise ValueError("No agent provided and no providers found in plan.")
