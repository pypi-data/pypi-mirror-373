import yaml
from rich.console import Console
from rich.prompt import Prompt, FloatPrompt, IntPrompt
from rich.table import Table
from rich.panel import Panel
from typing import Optional

from dtx_models.providers.openai import OpenaiProviderConfig, ProviderParams
from dtx_models.repo.models import ModelRegistry


class OpenAIModelSelectorCLI:
    """
    Interactive CLI to explore and configure OpenAI-compatible models.
    """

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.registry = ModelRegistry()
        self.provider = "openai"
        self.selected_model_cfg: Optional[OpenaiProviderConfig] = None

    def run(self) -> Optional[OpenaiProviderConfig]:
        self.console.print(Panel("[bold green]🔍 OpenAI Model Explorer[/]"))

        self._show_top_models()

        while not self.selected_model_cfg:
            user_input = Prompt.ask(
                "\n[bold cyan]Enter model number, keyword to search, or 'exit'[/]"
            ).strip()

            if user_input.lower() == "exit":
                self.console.print("[bold yellow]❌ Exiting...[/]")
                return None
            elif user_input.isdigit():
                idx = int(user_input)
                if 1 <= idx <= len(self._top_models):
                    self.selected_model_cfg = self._top_models[idx - 1]
                else:
                    self.console.print("[bold red]Invalid model number.[/]")
            else:
                self._search_and_select_model(user_input)

        config = self._collect_config()
        self._display_config(config)
        return config


    def _show_top_models(self):
        self.console.print("[bold magenta]Top 10 OpenAI-Compatible Models:[/]")
        models = self.registry.get_all_models_by_provider(provider=self.provider, limit=10)
        if isinstance(models, dict):
            models = models.get("openai", [])

        table = Table(show_header=True, header_style="bold green")
        table.add_column("Index", style="bold cyan", justify="center")
        table.add_column("Model Name")

        for idx, model in enumerate(models, start=1):
            table.add_row(str(idx), model.model)

        self.console.print(table)
        self._top_models = models  # store for selection

    def _select_model_from_top(self):
        if not hasattr(self, "_top_models") or not self._top_models:
            self.console.print("[bold red]No models loaded.[/]")
            return

        idx = IntPrompt.ask(
            "[bold cyan]Enter the number of the model to use[/]",
            choices=[str(i) for i in range(1, len(self._top_models) + 1)]
        )
        self.selected_model_cfg = self._top_models[int(idx) - 1]

    def _search_and_select_model(self, keyword: str):
        keyword = keyword.strip().lower()
        results = self.registry.search_by_keyword(keyword, provider=self.provider, limit=10)

        if not results:
            self.console.print(f"[bold yellow]⚠️ No models found for '{keyword}'.[/]")
            return

        table = Table(show_header=True, header_style="bold green")
        table.add_column("Index", style="bold cyan", justify="center")
        table.add_column("Model Name")

        for idx, model_cfg in enumerate(results, start=1):
            table.add_row(str(idx), model_cfg.model)

        self.console.print(table)

        idx = IntPrompt.ask(
            "[bold cyan]Enter the number of the model to use[/]",
            choices=[str(i) for i in range(1, len(results) + 1)]
        )
        self.selected_model_cfg = results[int(idx) - 1]


    def _collect_config(self) -> OpenaiProviderConfig:
        assert self.selected_model_cfg, "No model was selected."

        temperature = FloatPrompt.ask(
            "[bold cyan]Temperature (0-1)?[/]", default=0.7
        )
        max_tokens = IntPrompt.ask(
            "[bold cyan]Max tokens?[/]", default=512
        )

        stop = Prompt.ask(
            "[bold cyan]Stop sequences (comma separated, optional)?[/]", default=""
        )
        stop_tokens = [s.strip() for s in stop.split(",")] if stop else []

        # Clone and update the selected config
        return self.selected_model_cfg.model_copy(update={
            "params": ProviderParams(
                temperature=temperature,
                max_tokens=max_tokens,
                extra_params={"stop": stop_tokens} if stop_tokens else {}
            )
        })

    def _display_config(self, config: OpenaiProviderConfig):
        self.console.print(Panel("[bold green]🛠️ Final Configuration[/]"))

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Field", style="bold cyan")
        table.add_column("Value", style="bold green")

        table.add_row("Model", config.model)
        table.add_row("Task", config.task)
        table.add_row("Modality", config.modality)
        table.add_row("Temperature", str(config.params.temperature))
        table.add_row("Max Tokens", str(config.params.max_tokens))

        if config.params.extra_params:
            table.add_row("Extra Params", str(config.params.extra_params))

        self.console.print(table)

    def save_yaml(self, config: OpenaiProviderConfig, filename: Optional[str] = None):
        filename = filename or Prompt.ask(
            "[bold magenta]Enter filename to save as (default: openai_config.yaml)[/]",
            default="openai_config.yaml"
        )
        yaml_output = yaml.dump(config.model_dump(), sort_keys=False)
        with open(filename, "w") as f:
            f.write(yaml_output)
        self.console.print(f"[bold green]✅ Configuration saved to {filename}[/]")


# ---- Example usage ----
if __name__ == "__main__":
    cli = OpenAIModelSelectorCLI()
    config = cli.run()
    if config:
        cli.save_yaml(config)
