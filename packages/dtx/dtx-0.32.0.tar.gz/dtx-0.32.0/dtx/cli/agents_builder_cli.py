from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from dtx.cli.model_provider_cli import InteractiveModelBasedProviderBuilder
from dtx.core.builders.redteam import RedTeamScopeBuilder
from dtx_models.analysis import PromptDataset, RedTeamPlan
from dtx_models.providers.gradio import (
    GradioProviders,
)
from dtx_models.scope import AgentInfo, RedTeamScope
from dtx.plugins.prompts.langhub.cli import LangHubPromptGenerator
from dtx.plugins.providers.gradio.cli import GradioProviderGenerator
from dtx.plugins.providers.http.cli import HttpProviderBuilderCli
from dtx.plugins.providers.openai.cli import OpenAIModelSelectorCLI
from dtx_models.providers.openai import OpenaiProvider

from .planner import PlanInput, RedTeamPlanGenerator


class InteractiveAgentBuilder:
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.scope_builder = RedTeamScopeBuilder()

    def run(self):
        self.console.print(
            Panel(
                "[bold cyan]Let's build your agent interactively![/bold cyan]\n"
                "Choose from web models or template repositories.",
                title="🧩 AgentInfo Builder",
                expand=False,
            )
        )

        # Group choices
        choices_map = {
            "1": ("HTTP Provider", self._build_http_provider_flow),
            "2": ("Gradio Provider", self._build_gradio_provider_flow),
            "3": ("LangHub Prompts", self._build_langhub_scope_flow),
            "4": ("OpenAI Model", self._build_openai_provider_flow),  # ✅ NEW
        }


        # Display choices as table
        table = Table(title="Agent Options", show_lines=True)
        table.add_column("No.", justify="center", style="bold cyan")
        table.add_column("Option", style="bold green")

        for index, (label, _) in choices_map.items():
            table.add_row(index, label)

        self.console.print(table)

        # Step 1: Select agent type
        agent_choice = Prompt.ask(
            "Enter the number of the agent type you want to use",
            choices=list(choices_map.keys()),
            default="4",  # Optional: default to LangHub
        )

        # Step 2: Dispatch
        handler = choices_map.get(agent_choice)
        if handler:
            method = handler[1]
            rt_scope = method()  # Return RedTeamScope if applicable
            rt_plan = self._generate_plan(rt_scope)
            return rt_plan
        else:
            self.console.print(f"[red]Invalid selection: {agent_choice}[/red]")
            return None

    def _build_http_provider_flow(self):
        self.console.print(
            Panel(
                "[bold magenta]HTTP Provider selected.[/bold magenta]",
                title="🌐 HTTP Provider",
                expand=False,
            )
        )
        builder = HttpProviderBuilderCli(console=self.console)
        http_providers = builder.run()

        if not http_providers.providers:
            self.console.print("[red]No provider configuration was generated.[/red]")
            return None

        # Build RedTeamScope
        redteam_scope = (
            self.scope_builder.set_agent(
                agent=AgentInfo(
                    name="HTTP Agent",
                    description="Agent configured via HTTP Provider",
                    capabilities=["http-api integration"],
                )
            )
            .set_providers(http_providers.providers)
            .add_plugins_by_expression()
            .build()
        )

        return redteam_scope

    def _build_gradio_provider_flow(self):
        self.console.print(
            Panel(
                "[bold magenta]Gradio Provider selected.[/bold magenta]",
                title="🌐 Gradio Provider",
                expand=False,
            )
        )
        generator = GradioProviderGenerator(gradio_url="")
        gr_providers: GradioProviders = generator.run()

        if not gr_providers.providers:
            self.console.print("[red]No provider configuration was generated.[/red]")
            return None

        # Build RedTeamScope
        redteam_scope = (
            self.scope_builder.set_agent(
                agent=AgentInfo(
                    name="Gradio Agent",
                    description="Agent configured via Gradio Provider",
                    capabilities=["gradio web interface"],
                )
            )
            .set_providers(gr_providers.providers)
            .add_plugins_by_expression()
            .build()
        )

        return redteam_scope

    def _build_langhub_scope_flow(self):
        # Step 1: Generate prompts
        self.console.print(
            Panel(
                "[bold magenta]LangHub Template selected.[/bold magenta]",
                title="📄 LangHub Prompts",
                expand=False,
            )
        )
        generator = LangHubPromptGenerator()
        prompts_output = generator.run()
        prompts_list = prompts_output.prompts

        if not prompts_list:
            self.console.print("[red]No prompts were generated from LangHub![/red]")
            return None

        # Step 2: Notify user we are proceeding to provider generation
        self.console.print(
            Panel(
                "[bold yellow]You are about to configure your model provider for LangHub prompts.[/bold yellow]\n"
                "Provider configuration is required to complete the agent setup.",
                title="⚙️ Prepare to Generate Provider",
                expand=False,
            )
        )

        _ = Prompt.ask(
            "[bold cyan]Do you want to continue and configure your model provider? Press Enter to continue[/]",
        )

        # Step 3: Launch provider builder
        self.console.print(
            Panel(
                "[bold cyan]Let's configure your model provider![/bold cyan]",
                title="🔌 Model Provider Builder",
                expand=False,
            )
        )

        provider_builder = InteractiveModelBasedProviderBuilder(console=self.console)
        provider_output = provider_builder.run()

        if provider_output:
            # Step 4: Build RedTeamScope
            prompt_description = (
                prompts_list[0].config.prompt.metadata.description
                or "No description provided."
            )
            prompt_name = prompts_list[0].config.prompt.metadata.name or "Unnamed Agent"

            redteam_scope = (
                self.scope_builder.set_agent(
                    agent=AgentInfo(
                        name=prompt_name,
                        description=prompt_description,
                        capabilities=["prompt-based generation"],
                        llms=[provider_output.config.model],
                    )
                )
                .add_prompt(prompts_list[0])
                .add_provider(provider_output)
                .add_plugins_by_expression("injection")
                .build()
            )

            return redteam_scope

        else:
            self.console.print("[red]No provider configuration was generated.[/red]")
            return None

    def _generate_plan(self, scope: RedTeamScope):
        # Step 1: Introduction message
        self.console.print(
            Panel(
                "[bold cyan]We are going to generate a Red Team Plan.[/bold cyan]\n"
                "Start by choosing a dataset for prompt generation.",
                title="🧩 Plan Generator",
                expand=False,
            )
        )

        dataset_map = PromptDataset.descriptions()
        dataset_keys = list(dataset_map.keys())

        # Pagination settings
        page_size = 5
        total = len(dataset_keys)
        current_index = 0
        display_index = 1  # actual display numbering

        table = Table(title="Available Datasets", show_lines=True)
        table.add_column("No.", justify="center", style="bold cyan")
        table.add_column("Dataset", style="bold green")
        table.add_column("Description", style="white")

        while current_index < total:
            # Print next page
            for _ in range(page_size):
                if current_index >= total:
                    break
                dataset_name = dataset_keys[current_index]
                table.add_row(
                    str(display_index), dataset_name, dataset_map[dataset_name]
                )
                current_index += 1
                display_index += 1

            self.console.print(table)

            # If more datasets left, wait for Enter to show more
            if current_index < total:
                input("[bold cyan]Press [Enter] to show more datasets...[/bold cyan]")
                table = Table(title="Available Datasets (continued)", show_lines=True)
                table.add_column("No.", justify="center", style="bold cyan")
                table.add_column("Dataset", style="bold green")
                table.add_column("Description", style="white")
            else:
                break

        # Step 2: Dataset selection by number
        dataset_index = int(
            Prompt.ask(
                "Enter the number of the dataset you want to use",
                choices=[str(i) for i in range(1, total + 1)],
                default="1",
            )
        )
        selected_dataset = dataset_keys[dataset_index - 1]
        self.console.print(
            f"Selected dataset: [bold green]{selected_dataset}[/bold green]"
        )

        # Step 3: Max prompts
        max_prompts = int(
            Prompt.ask("Enter max number of prompts to generate", default="20")
        )

        # Step 4: Prompts per risk
        max_prompts_per_plugin = int(
            Prompt.ask("Enter number of prompts per risk category", default="5")
        )

        max_goals_per_plugin = int(
            Prompt.ask("Enter number of prompts per risk category", default="2")
        )

        scope.redteam.max_prompts = max_prompts
        scope.redteam.max_prompts_per_plugin = max_prompts_per_plugin
        scope.redteam.max_goals_per_plugin = max_goals_per_plugin

        # Step 5: Build PlanInput
        config = PlanInput(
            dataset=selected_dataset,
        )

        # Step 6: Generate plan
        generator = RedTeamPlanGenerator(scope=scope, config=config)
        plan = generator.run()

        return plan

    def save_yaml(
        self,
        plan: RedTeamPlan,
        default_plan_file: str = "redteam_plan.yml",
        default_scope_file: str = "redteam_scope.yml",
    ) -> str:
        import yaml

        # Step 1: Ask for plan file name
        plan_file = Prompt.ask(
            "Enter filename to save the RedTeam Plan",
            default=default_plan_file,
        )

        # Step 2: Save the plan YAML
        with open(plan_file, "w") as f:
            yaml.dump(plan.model_dump(), f, sort_keys=False)

        self.console.print(f"RedTeam Plan saved to [green]{plan_file}[/green]")

        # Step 3: Ask for scope file name
        scope_file = Prompt.ask(
            "Enter filename to save the RedTeam Scope",
            default=default_scope_file,
        )

        # Step 4: Save the scope YAML
        with open(scope_file, "w") as f:
            yaml.dump(plan.scope.model_dump(), f, sort_keys=False)

        self.console.print(f"RedTeam Scope saved to [green]{scope_file}[/green]")
        return plan_file

    def _build_openai_provider_flow(self):
        self.console.print(
            Panel(
                "[bold magenta]OpenAI Model selected.[/bold magenta]",
                title="🤖 OpenAI Provider",
                expand=False,
            )
        )

        cli = OpenAIModelSelectorCLI(console=self.console)
        config = cli.run()

        if not config:
            self.console.print("[red]No OpenAI model was selected.[/red]")
            return None

        provider = OpenaiProvider(config=config)

        # Build RedTeamScope
        redteam_scope = (
            self.scope_builder.set_agent(
                agent=AgentInfo(
                    name=config.model,
                    description="OpenAI Model Agent",
                    capabilities=["LLM generation"],
                    llms=[config.model],
                )
            )
            .add_provider(provider)
            .add_plugins_by_expression("injection")
            .build()
        )

        return redteam_scope



# __main__ section
if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    console = Console()
    console.print(
        Panel(
            "[bold green]Welcome to the Interactive AgentInfo Builder![/bold green]",
            title="🚀 Start",
            expand=False,
        )
    )
    builder = InteractiveAgentBuilder(console=console)
    plan = builder.run()
    if plan:
        builder.save_yaml(plan=plan)
    console.print(
        Panel(
            "[bold green]Interactive agent building complete![/bold green]",
            title="🎉 Done",
            expand=False,
        )
    )
