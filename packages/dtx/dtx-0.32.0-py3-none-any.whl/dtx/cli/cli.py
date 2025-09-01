import sys

# from dtx.cli.check_dep import check_modules
from rich.console import Console

from pathlib import Path

# Check if torch is found in the env
# if check_modules(["torch", "transformers"], required_pkg="dtx[torch]"):
from .planner import PlanInput, RedTeamPlanGenerator

import argparse
from dotenv import load_dotenv
from rich.prompt import Prompt
from typing import List, Optional
from dtx_models.analysis import PromptDataset
from dtx_models.providers.base import ProviderType
from dtx_models.analysis import RedTeamPlan
from dtx_models.template.prompts.base import PromptsRepoType
from dtx_models.repo.plugin import PluginRepo
from dtx.plugins.providers.gradio.cli import GradioProviderGenerator
from dtx.plugins.providers.http.cli import HttpProviderBuilderCli
from dtx.plugins.prompts.langhub.cli import LangHubPromptGenerator
from .agents_builder_cli import InteractiveAgentBuilder

from .console_output import (
    RichDictPrinter,
    RichResultVisualizer,
)
from .providers import ProviderFactory
from .scoping import RedTeamScopeCreator, ScopeInput
from .env_manager import EnvLoader
from .evaluatorargs import EvalMethodArgs

from .datasetargs import DatasetArgs
from .validatorsargs import EnvValidator

from .format import SmartFormatter

from .mutation_cli import PromptsMutationRepl

# import logging
# import http.client as http_client
# http_client.HTTPConnection.debuglevel = 1  # raw HTTP request/response lines

# logging.basicConfig(level=logging.DEBUG)
# logging.getLogger("urllib3").setLevel(logging.DEBUG)
# logging.getLogger("urllib3.connectionpool").setLevel(logging.DEBUG)

# Load env
load_dotenv()

# Configure Env Variable

EnvLoader().load_env()
EnvLoader().configure()

class AgentScanner:
    """Command-line tool to create and manage agent scope YAML files."""

    def __init__(self):
        self.selected_evaluator = EvalMethodArgs()
        self.select_dataset = DatasetArgs()
        self.args = self._parse_arguments()

    # --- Argument parsing ---
    def _parse_arguments(self):
        parser = argparse.ArgumentParser(
            description="Agent Scanner CLI",
            formatter_class=lambda prog: SmartFormatter(
                prog, max_help_position=40, width=150
            ),
        )
        subparsers = parser.add_subparsers(
            dest="command", help="Available commands", required=True
        )

        # REDTEAM COMMANDS
        redteam_parser = subparsers.add_parser(
            "redteam",
            help="Red teaming operations",
            formatter_class=lambda prog: SmartFormatter(
                prog, max_help_position=40, width=150
            ),
        )
        redteam_parser.add_argument("--headless", action="store_true", help="Disable all output saving")
        redteam_subparsers = redteam_parser.add_subparsers(
            dest="redteam_command", required=True
        )

        ## Quick Red Teaming
        redteam_subparsers.add_parser(
            "quick",
            help="Assistant to create plan and initiate Redteam",
        )

        ## Create Red Team Scope
        scope_parser = redteam_subparsers.add_parser(
            "scope", help="Generate red team scope"
        )

        scope_parser.add_argument(
            "--plugin", dest="plugins", action="append", default=[],
            help="Plugin ID, keyword, or regex expression (use multiple times for more plugins)"
        )

        scope_parser.add_argument(
            "--framework", dest="frameworks", action="append", default=[],
            help="AI Framework name or pattern (use multiple times for more)"
        )

        scope_parser.add_argument("description", type=str, help="Scope description")
        scope_parser.add_argument(
            "output", type=str, nargs="?", default="redteam_scope.yml"
        )

        plan_parser = redteam_subparsers.add_parser(
            "plan",
            help="Generate red team plan",
            formatter_class=lambda prog: SmartFormatter(
                prog, max_help_position=40, width=150
            ),
        )
        plan_parser.add_argument("scope_file", type=str)
        plan_parser.add_argument(
            "output", type=str, nargs="?", default="redteam_plan.yml"
        )
        plan_parser.add_argument("--max_prompts", type=int, default=20)
        plan_parser.add_argument("--max_prompts_per_plugin", type=int, default=100)
        plan_parser.add_argument("--max_goals_per_plugin", type=int, default=10)

        self.select_dataset.augment_args(plan_parser)

        run_parser = redteam_subparsers.add_parser(
            "run",
            help="Run red team tests",
            formatter_class=lambda prog: SmartFormatter(
                prog, max_help_position=40, width=150
            ),
        )
        run_parser.add_argument(
            "--agent",
            type=str,
            choices=ProviderType.values() + PromptsRepoType.values(),
            help="Choose an AgentInfo (optional if plan provided)",
        )
        run_parser.add_argument(
            "--plugin", dest="plugins", action="append", default=[],
            help="Plugin ID, keyword, or regex expression (use multiple times for more plugins)"
        )

        run_parser.add_argument(
            "--framework", dest="frameworks", action="append", default=[],
            help="AI Framework name or pattern (use multiple times for more)"
        )

        run_parser.add_argument("--plan_file", type=str, help="Redteam plan file path")
        run_parser.add_argument("--url", type=str, default="", help="Agent Url / Model Name")
        run_parser.add_argument("--max_prompts", type=int, default=20)
        run_parser.add_argument("--tactics", type=str, action="append", default=[])
        run_parser.add_argument("--samples", type=int, default=1, help="Number of samples per prompt")
        run_parser.add_argument("--threads", type=int, default=1, help="Number of threads to use (currently must be 1)")
        run_parser.add_argument("--headless", action="store_true", help="Disable all output saving")

        run_parser.add_argument(
            "--yml", type=str, default="report.yml", help="output yml file path"
        )
        run_parser.add_argument(
            "--json", type=str, default="report.json", help="output json file path"
        )
        run_parser.add_argument(
            "--html", type=str, default="report.html", help="output html file path"
        )
        run_parser.add_argument(
            "-o", "--output", action="store_true", help="Enable saving output file"
        )
        run_parser.add_argument("--max_prompts_per_plugin", type=int, default=100)
        run_parser.add_argument("--max_goals_per_plugin", type=int, default=20)
        
        self.select_dataset.augment_args(run_parser)
        self.selected_evaluator.augment_args(run_parser)

        # PLUGINS
        plugins_parser = subparsers.add_parser("plugins", help="Manage plugins")
        plugins_subparsers = plugins_parser.add_subparsers(dest="plugins_command")
        plugins_subparsers.add_parser("list", help="List plugins")

        # PROVIDERS
        providers_parser = subparsers.add_parser("providers", help="Manage providers")
        providers_subparsers = providers_parser.add_subparsers(dest="providers_command")
        generate_parser = providers_subparsers.add_parser("generate")
        generate_parser.add_argument(
            "provider", type=ProviderType, choices=ProviderType.values()
        )
        generate_parser.add_argument("--url", type=str, default="")
        generate_parser.add_argument("--output", type=str, default="")

        # PROMPTS
        prompts_parser = subparsers.add_parser("prompts", help="Manage prompts")
        prompts_subparsers = prompts_parser.add_subparsers(dest="prompts_command")
        generate_prompts_parser = prompts_subparsers.add_parser(
            "generate", help="Generate prompts"
        )
        generate_prompts_parser.add_argument(
            "prompts_repo", type=PromptsRepoType, choices=PromptsRepoType.values()
        )
        generate_prompts_parser.add_argument(
            "--url", type=str, default="", help="URL for prompt repository provider"
        )
        generate_prompts_parser.add_argument(
            "--output", type=str, default="", help="Output file for prompts"
        )

        # DATASETS & TACTICS
        subparsers.add_parser("datasets").add_subparsers(
            dest="datasets_command"
        ).add_parser("list")
        subparsers.add_parser("tactics").add_subparsers(
            dest="tactics_command"
        ).add_parser("list")

        # ENV
        env_parser = subparsers.add_parser("env", help="Environment variable helpers")
        env_parser.add_subparsers(dest="env_command").add_parser(
            "list", help="List required environment variables"
        )

        # ATTACKS (Unified)
        attack_parser = subparsers.add_parser(
            "attack",
            help="Unified TAP/PAIR/BON/AUTODAN/ACTOR entrypoint",
            formatter_class=lambda prog: SmartFormatter(prog, max_help_position=40, width=150),
        )
        attack_sub = attack_parser.add_subparsers(dest="attack_command", required=True)

        attack_run = attack_sub.add_parser(
            "run",
            help="Run an attack with minimal, common options",
            formatter_class=lambda prog: SmartFormatter(prog, max_help_position=40, width=150),
        )

        # Common, minimal options
        attack_run.add_argument(
            "--attack",
            required=True,
            choices=["TAP", "PAIR", "BON", "AUTODAN", "ACTOR", "CRESCENDO"],
            help="Attack algorithm to run.",
        )
        attack_run.add_argument("--task", required=True, help="Unified task text (root/goal/prompt).")
        attack_run.add_argument("--attacker-model", default=None, help="Attacker model (TAP/PAIR only).")
        attack_run.add_argument("--eval-model", default=None, help="Judge model.")
        attack_run.add_argument("--target-model", default=None, help="Target model.")
        attack_run.add_argument("--temperature", type=float, default=0.2, help="Target temperature.")
        attack_run.add_argument("--max-new-tokens", type=int, default=256, help="Max tokens for target generations.")
        attack_run.add_argument("--success-threshold", type=float, default=10.0, help="Early stop score threshold.")
        attack_run.add_argument("--judge-template", default=None, help="Judge template (defaults per attack).")
        attack_run.add_argument("--log-level", default="INFO", help="Loguru log level.")
        attack_run.add_argument("--no-logging", action="store_true", help="Disable loguru logging output.")

        # TAP minimal knobs
        attack_run.add_argument("--tap-depth", type=int, default=5, help="TAP tree depth.")
        attack_run.add_argument("--tap-width", type=int, default=5, help="TAP beam width.")
        attack_run.add_argument("--tap-branch", type=int, default=3, help="TAP branching factor.")
        attack_run.add_argument("--tap-keep-last-n", type=int, default=3, help="TAP attacker history turns kept.")
        attack_run.add_argument("--tap-max-attempts", type=int, default=5, help="TAP attacker JSON retry budget.")
        attack_run.add_argument("--no-delete-off-topic", action="store_true", help="Disable TAP DeleteOffTopic filter.")

        # PAIR minimal knobs
        attack_run.add_argument("--pair-streams", type=int, default=3, help="PAIR streams.")
        attack_run.add_argument("--pair-iters", type=int, default=3, help="PAIR iterations per stream.")
        attack_run.add_argument("--pair-max-attempts", type=int, default=3, help="PAIR JSON retry budget.")

        # BON minimal knobs
        attack_run.add_argument("--bon-candidates", type=int, default=20, help="BON candidates per round.")
        attack_run.add_argument("--bon-rounds", type=int, default=1, help="BON rounds.")
        attack_run.add_argument("--bon-sigma", type=float, default=0.4, help="BON augmentation strength.")
        attack_run.add_argument("--bon-seed", type=int, default=None, help="BON RNG seed.")

        # AUTODAN knobs
        attack_run.add_argument("--ad-candidates", type=int, default=32, help="AutoDAN population size.")
        attack_run.add_argument("--ad-steps", type=int, default=20, help="AutoDAN outer evolutionary steps.")
        attack_run.add_argument("--ad-sent-steps", type=int, default=3, help="AutoDAN sentence-level mutation steps per gen.")
        attack_run.add_argument("--ad-mutation-rate", type=float, default=0.02, help="AutoDAN per-template rephrase mutation rate.")
        attack_run.add_argument("--ad-ratio-elites", type=float, default=0.1, help="AutoDAN fraction of elites kept each generation.")
        attack_run.add_argument("--ad-num-points", type=int, default=5, help="AutoDAN crossover cut points.")
        attack_run.add_argument("--ad-crossover-rate", type=float, default=0.5, help="AutoDAN crossover probability.")
        attack_run.add_argument("--ad-word-dict-size", type=int, default=50, help="AutoDAN top-k momentum dictionary size.")
        attack_run.add_argument("--ad-model-display-name", type=str, default="Llama 2", help="Friendly label for seeds/logging.")
        attack_run.add_argument("--ad-rephrase-model", type=str, default=None, help="OpenAI model for AutoDAN rephrase step.")

        # Whitebox HF target (AUTODAN)
        attack_run.add_argument(
            "--ad-hf-target-model",
            type=str,
            default="HuggingFaceTB/SmolLM-135M-Instruct",
            help="HF target model name/path for AutoDAN (default: HuggingFaceTB/SmolLM-135M-Instruct).",
        )
        attack_run.add_argument(
            "--ad-system-prompt",
            type=str,
            default="You are a helpful, safe assistant.",
            help="System prompt injected into the HF whitebox target.",
        )
        attack_run.add_argument(
            "--ad-dtype",
            type=str,
            choices=["auto", "float16", "bfloat16", "float32"],
            default="float16",
            help="Torch dtype for the HF target model.",
        )
        attack_run.add_argument(
            "--ad-vllm",
            action="store_true",
            help="Use vLLM backend for the HF target if available.",
        )
        attack_run.add_argument(
            "--ad-trust-remote-code",
            action="store_true",
            help="Pass trust_remote_code=True to the HF tokenizer/model loaders.",
        )

        # ACTOR knobs
        attack_run.add_argument(
            "--actor-behavior-model",
            type=str,
            default="gpt-4o-mini",
            help="OpenAI model for behavior extraction (ACTOR).",
        )
        attack_run.add_argument(
            "--actor-actors-model",
            type=str,
            default="gpt-4o-mini",
            help="OpenAI model for actor generation (ACTOR).",
        )
        attack_run.add_argument(
            "--actor-questions-model",
            type=str,
            default="deepseek-r1-distill-llama-70b",
            help="Model for questions generation (Groq/OpenAI based on provider) (ACTOR).",
        )
        attack_run.add_argument(
            "--actor-questions-provider",
            type=str,
            choices=["auto", "groq", "openai"],
            default="auto",
            help="Provider for questions model: auto uses Groq if GROQ_API_KEY is present, else OpenAI.",
        )

        # --- CRESCENDO (two-model) ---
        attack_run.add_argument(
            "--cres-question-model",
            type=str,
            default="deepseek-r1-distill-llama-70b",
            help="Question model for Crescendo (Groq/OpenAI depending on provider).",
        )
        attack_run.add_argument(
            "--cres-answer-model",
            type=str,
            default="gpt-4o-mini",
            help="Answer (target) model for Crescendo.",
        )
        attack_run.add_argument(
            "--cres-questions-provider",
            type=str,
            choices=["auto", "groq", "openai"],
            default="auto",
            help="Provider for the question model: auto uses Groq when GROQ_API_KEY is set, otherwise OpenAI.",
        )

        # Behavior / loop controls
        attack_run.add_argument(
            "--cres-less-questions",
            dest="cres_less_questions",
            action="store_true",
            default=True,
            help="Bias question model toward fewer, more targeted steps (default: on).",
        )
        attack_run.add_argument(
            "--no-cres-less-questions",
            dest="cres_less_questions",
            action="store_false",
            help="Allow longer question chains.",
        )
        attack_run.add_argument("--cres-iterations", type=int, default=3, help="Crescendo outer iterations N.")
        attack_run.add_argument("--cres-rounds", type=int, default=6, help="Crescendo rounds per iteration R.")
        attack_run.add_argument("--cres-refusal-limit", type=int, default=2, help="Max backtracks for refusals per iteration.")

        # Generation knobs
        attack_run.add_argument("--cres-qgen-temperature", type=float, default=0.2, help="Question model temperature.")
        attack_run.add_argument("--cres-qgen-max-new-tokens", type=int, default=512, help="Question model max tokens.")
        attack_run.add_argument("--cres-answer-temperature", type=float, default=0.7, help="Answer model temperature.")
        attack_run.add_argument("--cres-answer-max-new-tokens", type=int, default=250, help="Answer model max tokens.")


        # REPL (Interactive)
        repl_parser = subparsers.add_parser(
            "copilot",
            help="Interactive REPL utilities",
            formatter_class=lambda prog: SmartFormatter(prog, max_help_position=40, width=150),
        )
        repl_subparsers = repl_parser.add_subparsers(dest="repl_command", required=True)

        # REPL: mutation
        repl_mutation = repl_subparsers.add_parser(
            "prompts",
            help="Interactive prompt mutation REPL",
            formatter_class=lambda prog: SmartFormatter(prog, max_help_position=40, width=150),
        )
        repl_mutation.add_argument("--tech", type=str, default=None, help="Default technique name/id")
        repl_mutation.add_argument("--seed", type=int, default=None, help="Random seed for stochastic techniques")
        repl_mutation.add_argument("--no-color", action="store_true", help="Disable colorized output")


        return parser.parse_args()

    # --- Main entrypoint ---
    def run(self):
        match self.args.command:
            case "redteam":
                self._handle_redteam()
            case "providers":
                self._handle_providers()
            case "prompts":
                self._handle_prompts()
            case "datasets" if self.args.datasets_command == "list":
                self.list_datasets()
            case "plugins" if self.args.plugins_command == "list":
                self.list_plugins()
            case "tactics" if self.args.tactics_command == "list":
                self.list_tactics()
            case "env" if self.args.env_command == "list":
                self.list_env_dependencies()
            case "attack" if self.args.attack_command == "run":
                self._handle_attack_run()
            case "copilot":
                self._handle_repl()
            case _:
                print("Invalid command. Use --help for usage.")

    # --- REDTEAM Operations ---
    def _handle_redteam(self):

        if self.args.headless:
            from dtx.core import logging
            logging.set_level("error")
        try:
            EnvValidator.validate(
                dataset=getattr(self.args, "dataset", None),
                eval_name=getattr(self.args, "eval", None),
            )
        except EnvironmentError as e:
            print(str(e))
            sys.exit(1)

        match self.args.redteam_command:
            case "scope":
                self._generate_scope(self.args.description, self.args.output, plugins=self.args.plugins)
            case "plan":
                self._generate_plan(
                    scope_file=self.args.scope_file,
                    output=self.args.output,
                    max_prompts=self.args.max_prompts,
                    max_prompts_per_plugin=self.args.max_prompts_per_plugin,
                    max_goals_per_plugin=self.args.max_goals_per_plugin
                )
            case "run":
                self._run_tests()
            case "quick":
                self._redteam_interactive_quick()
            case _:
                print("Invalid redteam subcommand")

    def _run_tests(self):

        from .runner import QuickRedteamRunner, QuickRedteamRunnerInput

        collector = RichResultVisualizer(headless=self.args.headless)

        if self.args.plan_file:
            input_data = QuickRedteamRunnerInput(
                plan_file=self.args.plan_file,
                max_prompts=self.args.max_prompts,
                max_prompts_per_plugin=self.args.max_prompts_per_plugin,
                max_goals_per_plugin=self.args.max_goals_per_plugin,
                agent=self.args.agent,
                url=self.args.url,
                output=self.args.output,
                yml_file=self.args.yml,
                json_file=self.args.json,
                collector=collector,
                html_file=self.args.html
            )
        else:
            # Validate argument combinations before running
            self._validate_args_combinations()

            dataset = self.select_dataset.parse_args(self.args)
            global_eval = self.selected_evaluator.parse_args(self.args)

            input_data = QuickRedteamRunnerInput(
                plan_file=self.args.plan_file,
                max_prompts=self.args.max_prompts,
                max_prompts_per_plugin=self.args.max_prompts_per_plugin,
                max_goals_per_plugin=self.args.max_goals_per_plugin,
                samples_per_prompt=self.args.samples,
                threads=self.args.threads,
                agent=self.args.agent,
                url=self.args.url,
                output=self.args.output,
                yml_file=self.args.yml,
                json_file=self.args.json,
                html_file=self.args.html,
                dataset=dataset,
                evaluator=global_eval,
                tactics=[],
                plugins=self.args.plugins,
                frameworks=self.args.frameworks,
                collector=collector,
            )
            input_data.set_tactics_by_name(names=self.args.tactics)

        runner = QuickRedteamRunner(input_data)
        runner.run()

    def _resolve_agent_and_url(self, plan: RedTeamPlan):
        if self.args.agent:
            return self.args.agent, self.args.url

        return self._resolve_agent_and_url_from_plan(plan=plan)

    def _resolve_agent_and_url_from_plan(self, plan: RedTeamPlan):
        if plan.scope.providers:
            provider = plan.scope.providers[0]
            agent_type = provider.provider
            url = getattr(provider.config, "model", getattr(provider.config, "url", ""))
            print(f"🧩 Using provider from plan: agent={agent_type}, url={url}")
            return agent_type, url

        raise ValueError(
            "No agent specified. Use --agent or provide a plan file with provider information."
        )

    def _create_scope(self, description=None):
        description = description or "It is a default scope"
        scope_config = ScopeInput(
            description=description,
            plugins=self.args.plugins,
            frameworks=self.args.frameworks
        )
        creator = RedTeamScopeCreator(config=scope_config)
        scope = creator.run()

        global_eval = self.selected_evaluator.parse_args(self.args)
        if global_eval:
            scope.redteam.global_evaluator = global_eval
        return scope

    def _run_tests_initialize_agent(self, plan, agent_type, url):
        return ProviderFactory(load_env_vars=True).get_agent(plan.scope, agent_type, url)

    def _run_tests_initialize_collector(self, headless=False):
        return RichResultVisualizer(headless=headless)

    def _generate_scope(self, description, output, plugins: Optional[List[str]]=None):
        config = ScopeInput(description=description, plugins=plugins, frameworks=self.args.frameworks)
        creator = RedTeamScopeCreator(config=config)
        creator.run()
        creator.save_yaml(output)

    def _generate_plan(self, scope_file, output, 
                    max_prompts, 
                    max_prompts_per_plugin, 
                    max_goals_per_plugin=5):
        scope = RedTeamScopeCreator.load_yaml(scope_file)
        dataset = self.select_dataset.parse_args(self.args)
        scope.redteam.max_prompts = max_prompts
        scope.redteam.max_prompts_per_plugin = max_prompts_per_plugin
        scope.redteam.max_goals_per_plugin = max_goals_per_plugin

        config = PlanInput(
            dataset=dataset
        )
        generator = RedTeamPlanGenerator(scope=scope, config=config)
        generator.run()
        generator.save_yaml(output)

    def _redteam_interactive_quick(self):

        from .runner import QuickRedteamRunner, QuickRedteamRunnerInput

        console = Console()
        builder = InteractiveAgentBuilder(console=console)
        plan = builder.run()

        if not plan:
            console.print("[red]❌ Plan creation failed or was cancelled.[/red]")
            return

        # Step 1: Save YAML files (scope + plan)
        plan_file = builder.save_yaml(plan=plan)

        # Step 2: Ask user if they want to run the tests now
        run_now = Prompt.ask(
            "[bold cyan]Do you want to run the RedTeam tests now?[/bold cyan] (yes/no)",
            choices=["yes", "no"],
            default="yes",
        )

        if run_now.lower() != "yes":
            console.print("[yellow]⚠️ Skipping RedTeam test execution.[/yellow]")
            return

        # Step 3: Ask user for output report file
        output_file = Prompt.ask(
            "Enter the filename to save the RedTeam test results",
            default="report.yml",
        )
        output_json = Path(output_file).with_suffix(".json").as_posix()
        output_html = Path(output_file).with_suffix(".html").as_posix()

        # Step 4: Resolve agent info and prepare runner input
        agent_type, url = self._resolve_agent_and_url_from_plan(plan)
        agent = self._run_tests_initialize_agent(plan, agent_type, url)
        collector = self._run_tests_initialize_collector(headless=self.args.headless)

        input_data = QuickRedteamRunnerInput(
            plan_file=plan_file,
            agent=agent_type,
            url=url,
            max_prompts=1000,
            tactics=[],
            output=True,
            yml_file=output_file,
            json_file=output_json,
            html_file=output_html,
            collector=collector
        )

        # Step 5: Run the tests using QuickRedteamRunner
        console.print("[bold green]🚀 Running RedTeam tests...[/bold green]")
        runner = QuickRedteamRunner(input_data)
        runner.run()

        # Step 6: Confirm save location
        console.print(f"RedTeam test results saved to [green]{output_file}[/green]")

    # --- Utilities ---
    def list_env_dependencies(self):
        deps = EnvValidator.list_all_dependencies()
        all_rows = {}

        for dataset, envs in deps["datasets"].items():
            deps_list = self._format_env_dependency(envs)
            if deps_list != "-":
                all_rows[f"Dataset: {dataset}"] = deps_list

        for eval_name, envs in deps["evals"].items():
            deps_list = ", ".join(envs) if envs else "-"
            if deps_list != "-":
                all_rows[f"Eval: {eval_name}"] = deps_list

        if not all_rows:
            print("🎉 No environment dependencies found!")
            return

        printer = RichDictPrinter("Environment Dependencies", "Item", "Dependencies")
        printer.print(all_rows)

    @staticmethod
    def _format_env_dependency(env_map):
        parts = []
        if env_map.get("all"):
            parts.append("All: " + ", ".join(env_map["all"]))
        if env_map.get("any"):
            parts.append("Any: " + ", ".join(env_map["any"]))
        return " | ".join(parts) if parts else "-"

    def _validate_args_combinations(self):

        global_eval = self.selected_evaluator.parse_args(self.args)
        dataset = self.select_dataset.parse_args(self.args)
        dataset_input = getattr(self.args, "dataset", None)

        if dataset in [PromptDataset.STINGRAY] and global_eval:
            if not self.args.eval:
                print(
                    f"❌ Error: It seems '{dataset_input}' dataset, and agent are not compatible."
                )
                sys.exit(1)
            else:
                print(
                    f"❌ Error: When using '{dataset_input}' dataset, you must not specify an evaluator with --eval."
                )
                sys.exit(1)

    # --- Providers and Prompts ---
    def _handle_providers(self):
        if self.args.providers_command == "generate":
            if self.args.provider == ProviderType.GRADIO:
                generator = GradioProviderGenerator(gradio_url=self.args.url)
                providers = generator.run()
                if providers:
                    generator.save_yaml(providers)
            elif self.args.provider == ProviderType.HTTP:
                builder = HttpProviderBuilderCli(url=self.args.url)
                provider_output = builder.run()
                builder.dump_yaml(provider_output, filename=self.args.output)
            else:
                print("Unsupported provider type for generation.")
        else:
            print("Invalid providers command")

    def _handle_prompts(self):
        if self.args.prompts_command == "generate":
            if self.args.prompts_repo == PromptsRepoType.LANGHUB:
                generator = LangHubPromptGenerator()
                providers = generator.run()
                if providers:
                    generator.save_yaml(providers)
            else:
                print("Unsupported prompts repository type for generation.")
        else:
            print("Invalid prompts command")

    def list_datasets(self):
        printer = RichDictPrinter("Available Prompt Datasets", "Dataset", "Description")
        printer.print(PromptDataset.descriptions())

    def list_plugins(self):
        plugin_map = PluginRepo.get_plugin_descriptions()
        printer = RichDictPrinter("Available Plugins", "Plugin", "Description")
        printer.print(plugin_map)

    def list_tactics(self):
        from dtx.config import globals
        tactics_repo = globals.get_tactics_repo(only=True)
        plugin_map = tactics_repo.get_tactics()
        printer = RichDictPrinter("Available Tactics", "Tactic", "Description")
        printer.print(plugin_map)

    def _handle_attack_run(self):
        from dtx.cli.attacks import AttackCommonArgs, run_attack

        args_ns = self.args  # argparse.Namespace

        common = AttackCommonArgs(
            attack=args_ns.attack,
            task=args_ns.task,
            attacker_model=args_ns.attacker_model,
            eval_model=args_ns.eval_model,
            target_model=args_ns.target_model,
            temperature=args_ns.temperature,
            max_new_tokens=args_ns.max_new_tokens,
            success_threshold=args_ns.success_threshold,
            judge_template=args_ns.judge_template,
            log_level=args_ns.log_level,
            no_logging=args_ns.no_logging,

            tap_depth=args_ns.tap_depth,
            tap_width=args_ns.tap_width,
            tap_branch=args_ns.tap_branch,
            tap_keep_last_n=args_ns.tap_keep_last_n,
            tap_max_attempts=args_ns.tap_max_attempts,
            tap_delete_off_topic=not args_ns.no_delete_off_topic,

            pair_streams=args_ns.pair_streams,
            pair_iters=args_ns.pair_iters,
            pair_max_attempts=args_ns.pair_max_attempts,

            bon_candidates=args_ns.bon_candidates,
            bon_rounds=args_ns.bon_rounds,
            bon_sigma=args_ns.bon_sigma,
            bon_seed=args_ns.bon_seed,

            # AUTODAN
            ad_candidates=args_ns.ad_candidates,
            ad_steps=args_ns.ad_steps,
            ad_sent_steps=args_ns.ad_sent_steps,
            ad_mutation_rate=args_ns.ad_mutation_rate,
            ad_ratio_elites=args_ns.ad_ratio_elites,
            ad_num_points=args_ns.ad_num_points,
            ad_crossover_rate=args_ns.ad_crossover_rate,
            ad_word_dict_size=args_ns.ad_word_dict_size,
            ad_model_display_name=args_ns.ad_model_display_name,
            ad_rephrase_model=args_ns.ad_rephrase_model,
            ad_hf_target_model=args_ns.ad_hf_target_model,

            # ACTOR
            actor_behavior_model=args_ns.actor_behavior_model,
            actor_actors_model=args_ns.actor_actors_model,
            actor_questions_model=args_ns.actor_questions_model,
            actor_questions_provider=args_ns.actor_questions_provider,

            # CRESCENDO
            cres_question_model=args_ns.cres_question_model,
            cres_answer_model=args_ns.cres_answer_model,
            cres_questions_provider=args_ns.cres_questions_provider,
            cres_less_questions=args_ns.cres_less_questions,
            cres_iterations=args_ns.cres_iterations,
            cres_rounds=args_ns.cres_rounds,
            cres_refusal_limit=args_ns.cres_refusal_limit,
            cres_qgen_temperature=args_ns.cres_qgen_temperature,
            cres_qgen_max_new_tokens=args_ns.cres_qgen_max_new_tokens,
            cres_answer_temperature=args_ns.cres_answer_temperature,
            cres_answer_max_new_tokens=args_ns.cres_answer_max_new_tokens,

        )

        run_attack(common)


    def _handle_repl(self):
        if self.args.repl_command == "prompts":
            repl = PromptsMutationRepl(
                default_tech=self.args.tech,
                seed=self.args.seed,
                no_color=self.args.no_color,
            )
            repl.run()
        else:
            print("Invalid repl subcommand")


def main():
    scanner = AgentScanner()
    scanner.run()
