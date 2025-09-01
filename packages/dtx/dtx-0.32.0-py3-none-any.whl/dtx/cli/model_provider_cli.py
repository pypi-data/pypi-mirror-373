from typing import Optional, Union

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from dtx_models.providers.base import ProviderType
from dtx_models.providers.litellm import LitellmProvider, LitellmProviderConfig
from dtx_models.providers.models_spec import (
    ModelSpec,
    ModelSpecRepo,
)
from dtx_models.providers.openai import OpenaiProvider, OpenaiProviderConfig


class InteractiveModelBasedProviderBuilder:
    """
    Interactive builder for providers based on model selection from repository.
    Flow:
    1. Select provider (OpenAI, Groq)
    2. Select model by index
    3. Generate provider Pydantic model (OpenaiProvider or LitellmProvider)
    """

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.repo = ModelSpecRepo()

    def run(self) -> Optional[Union[OpenaiProvider, LitellmProvider]]:
        """Run interactive builder and return provider configuration (Pydantic model)."""

        self.console.print(
            Panel(
                "[bold cyan]Let's build your provider![/bold cyan]\n"
                "First, choose a provider.",
                title="🧩 Model-based Provider Builder",
                expand=False,
            )
        )

        # Step 1: Select provider (OpenAI or Groq)
        provider_choices = {
            "openai": ProviderType.OPENAI,
            "groq": ProviderType.GROQ,
        }

        selected_provider_key = Prompt.ask(
            "Select provider",
            choices=list(provider_choices.keys()),
            default="openai",
        )

        selected_provider = provider_choices[selected_provider_key]

        # Step 2: List models for the selected provider
        models = self.repo.get_models_by_provider(selected_provider)
        if not models:
            self.console.print(
                f"[red]No models found for provider: {selected_provider.value}[/red]"
            )
            return None

        self._display_models_table(models)

        # Step 3: Select model by index
        model_index = Prompt.ask(
            "Enter the number of the model you want to use",
            choices=[str(i + 1) for i in range(len(models))],
        )

        try:
            selected_model = models[int(model_index) - 1]
        except (IndexError, ValueError):
            self.console.print(f"[red]Invalid model selection: {model_index}[/red]")
            return None

        # Step 4: Build provider object using Pydantic models
        provider_instance = self._build_provider(selected_provider, selected_model)

        self.console.print(
            Panel(
                f"[green]✅ Provider configuration generated![/green]\n"
                f"Provider: [bold]{provider_instance.id}[/bold]\n"
                f"Model: [bold]{provider_instance.config.model}[/bold]",
                title="🎯 Selection Summary",
                expand=False,
            )
        )

        return provider_instance

    def save_yaml(
        self,
        provider_instance: Union[OpenaiProvider, LitellmProvider],
        filename: Optional[str] = None,
    ):
        """Save the provider configuration to a YAML file."""
        filename = filename or Prompt.ask(
            "[bold magenta]Enter filename to save as (default: model_provider.yaml)[/]",
            default="model_provider.yaml",
        )

        yaml_output = yaml.dump(provider_instance.model_dump(), sort_keys=False)
        with open(filename, "w") as f:
            f.write(yaml_output)

        self.console.print(f"[bold green]Configuration saved to {filename} ✅[/]")

    def _build_provider(
        self, provider: ProviderType, model: ModelSpec
    ) -> Union[OpenaiProvider, LitellmProvider]:
        """Helper to build provider object from selection."""
        if provider == ProviderType.OPENAI:
            provider_instance = OpenaiProvider(
                config=OpenaiProviderConfig(model=model.name)
            )
        elif provider == ProviderType.GROQ:
            provider_instance = LitellmProvider(
                config=LitellmProviderConfig(model=model.name)
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        return provider_instance

    def _display_models_table(self, models: list[ModelSpec]):
        table = Table(title="Available Models", show_lines=True)
        table.add_column("No.", justify="center", style="bold cyan")
        table.add_column("Model Name", style="bold green")
        table.add_column("Task", style="magenta")
        table.add_column("Modalities", style="yellow")
        table.add_column("Description", style="white")

        for idx, model in enumerate(models):
            table.add_row(
                str(idx + 1),
                model.name,
                model.task.value,
                ", ".join(mod.value for mod in model.modalities),
                model.description or "-",
            )

        self.console.print(table)


# ✅ __main__ section
if __name__ == "__main__":
    console = Console()
    console.print(
        Panel(
            "[bold green]Welcome to the Model-Based Provider Builder![/bold green]",
            title="🚀 Start",
            expand=False,
        )
    )

    builder = InteractiveModelBasedProviderBuilder(console=console)
    provider_instance = builder.run()

    if provider_instance:
        builder.save_yaml(provider_instance)
    else:
        console.print("[red]No provider configuration was generated.[/red]")

    console.print(
        Panel(
            "[bold green]✅ Process complete![/bold green]",
            title="🎉 Done",
            expand=False,
        )
    )
