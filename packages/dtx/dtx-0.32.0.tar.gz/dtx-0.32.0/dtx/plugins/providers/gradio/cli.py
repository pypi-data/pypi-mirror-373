from typing import Any, List, Optional

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from dtx.core import logging
from dtx_models.providers.gradio import (
    GradioApiSignatureParam,
    GradioApiSpecs,
    GradioProvider,
    GradioProviderApi,
    GradioProviderApiParam,
    GradioProviderConfig,
    GradioProviders,
)

from .api_specs_generator import GradioApiSpecGenerator
from .client import GradioProviderClient
from .parsers.response.parser_builder import GradioResponseParserBuilder


class GradioProviderGenerator:
    """
    Interactive CLI tool for generating Gradio API providers using Rich.
    Allows API inspection before provider generation.
    """

    def __init__(self, gradio_url: Optional[str] = None):
        """
        Initializes the generator and retrieves API specifications.

        :param gradio_url: The base URL of the Gradio API provider.
        """
        self.console = Console()
        self.url = gradio_url or self._get_gradio_url()
        self.api_spec_generator = GradioApiSpecGenerator(self.url)
        self.api_specs: Optional[GradioApiSpecs] = (
            self.api_spec_generator.generate_api_specs()
        )

    def _get_gradio_url(self) -> str:
        """Prompt user to enter the Gradio API base URL."""
        return Prompt.ask(
            "[bold cyan]Enter the Gradio API URL or HF Space Name[/]"
        ).strip()

    def _list_apis(self):
        """Displays available API endpoints in a table."""
        if not self.api_specs or not self.api_specs.apis:
            self.console.print("[bold red]No APIs found for this Gradio provider.[/]")
            return

        table = Table(
            title="Available APIs", show_header=True, header_style="bold magenta"
        )
        table.add_column("Index", style="bold cyan", justify="center")
        table.add_column("API Path", style="bold yellow")

        for i, api in enumerate(self.api_specs.apis):
            table.add_row(str(i + 1), api.api_name)

        self.console.print(table)

    def _inspect_apis(self):
        """Allows the user to inspect API details."""
        while True:
            self._list_apis()
            selected_api = Prompt.ask(
                "[bold cyan]Enter the number of the API to inspect (or press Enter to return)[/]",
                default="",
            ).strip()

            if not selected_api:
                return

            try:
                index = int(selected_api) - 1
                if 0 <= index < len(self.api_specs.apis):
                    api = self.api_specs.apis[index]
                    self.console.print(
                        Panel(
                            f"[bold yellow]Inspecting API: {api.api_name}[/]",
                            expand=False,
                        )
                    )

                    table = Table(
                        title="API Parameters",
                        show_header=True,
                        header_style="bold magenta",
                    )
                    table.add_column("Parameter Name", style="bold cyan")
                    table.add_column("Default Value", style="bold green")
                    table.add_column("Type", style="bold red")

                    for param in api.params:
                        table.add_row(
                            param.name, str(param.default_value), param.python_type
                        )

                    self.console.print(table)
                else:
                    self.console.print(
                        "[bold red]Invalid selection. Please try again.[/]"
                    )

            except ValueError:
                self.console.print("[bold red]Invalid input. Please enter a number.[/]")

    def _get_user_selected_apis(self) -> List[str]:
        """Asks the user to select APIs interactively."""
        if not self.api_specs or not self.api_specs.apis:
            return []

        self._list_apis()

        while True:
            selected_indexes = Prompt.ask(
                "[bold cyan]Enter the numbers of the APIs you want to use (comma-separated)[/]",
                default="",
            )
            try:
                indexes = [int(i.strip()) - 1 for i in selected_indexes.split(",")]
                selected_apis = [
                    self.api_specs.apis[i].api_name
                    for i in indexes
                    if 0 <= i < len(self.api_specs.apis)
                ]
                if selected_apis:
                    return selected_apis
                else:
                    self.console.print(
                        "[bold red]Invalid selection. Please try again.[/]"
                    )
            except ValueError:
                self.console.print(
                    "[bold red]Invalid input. Enter numbers separated by commas.[/]"
                )

    def _parse_possible_values(self, python_type: str) -> Optional[List[str]]:
        """Extracts possible values if the parameter type is a Literal."""
        if python_type.startswith("Literal"):
            try:
                literal_values = eval(python_type.replace("Literal", "(") + ")")
                return list(literal_values)
            except Exception as e:
                logging.error(f"Failed to parse Literal type: {e}")
        return None

    def _get_user_params(
        self, api_name: str, params: List[GradioApiSignatureParam]
    ) -> List[GradioProviderApiParam]:
        """Prompts the user to enter values for each API parameter interactively."""
        user_params = []
        self.console.print(
            Panel(
                f"[bold yellow]Configuring parameters for API: {api_name}[/]",
                expand=False,
            )
        )

        for param in params:
            possible_values = self._parse_possible_values(param.python_type)

            # Determine default value
            if possible_values:
                default_value = possible_values[0]  # Pick the first value if a list
                self.console.print(
                    f"[bold cyan]Choose a value for '{param.name}'[/] from: {', '.join(map(str, possible_values))}"
                )
            else:
                default_value = param.default_value

            while True:
                value = Prompt.ask(
                    f"[bold cyan]Enter value for '{param.name}'[/] (press Enter to keep default: [bold magenta]{default_value}[/])",
                    default=str(default_value) if default_value is not None else "",
                ).strip()

                value = value or default_value

                # If possible values exist, and it is not default, validate input
                if possible_values and not value == default_value:
                    if value not in possible_values:
                        self.console.print(
                            f"[bold red]Invalid choice. Please select from: {', '.join(map(str, possible_values))}[/]"
                        )
                        continue
                else:
                    try:
                        value = self._convert_type(
                            value, param.python_type, default_value
                        )
                    except ValueError as e:
                        self.console.print(
                            f"[bold red]Invalid input: {e}. Try again.[/]"
                        )
                        continue

                user_params.append(GradioProviderApiParam(name=param.name, value=value))
                break

        return user_params

    def _adapt_default_value(self, python_type: str, default_value: Any):
        python_type = (python_type or "").lower()
        if default_value is None:
            if python_type.startswith("list") or python_type.startswith("tuple"):
                default_value = []
            elif python_type.startswith("dict"):
                default_value = {}
        return default_value

    def _convert_type(self, value: str, python_type: str, default_value: Any):
        """Converts user input to the correct parameter type."""
        if value == default_value:
            # In case of tuple or list convert None to empty structure
            return self._adapt_default_value(python_type, value)
        python_type = (python_type or "").lower()
        try:
            if python_type.startswith("int"):
                return int(value)
            elif python_type.startswith("float"):
                return float(value)
            elif python_type.startswith("bool"):
                return value.lower() in ["true", "1", "yes"]
            elif (
                python_type.startswith("list")
                or python_type.startswith("literal")
                or python_type.startswith("tuple")
            ):
                return [value] if not isinstance(value, list) else value
            else:
                return value  # Default to string if no type conversion needed
        except ValueError:
            raise ValueError(f"Expected {python_type}, but got '{value}'")

    def _get_fuzzable_params(self, api: GradioProviderApi) -> List[str]:
        """Finds parameters with Jinja templates."""
        return [
            param.name
            for param in api.params
            if isinstance(param.value, str) and "{{prompt}}" in param.value
        ]

    def _learn_response_structure(
        self, provider: GradioProvider, api: GradioProviderApi
    ) -> Optional[str]:
        """
        Calls the API with different fuzz values and generates a jq expression.

        :param provider: The provider configuration.
        :return: A jq expression for response parsing.
        """
        client = GradioProviderClient(url=provider.config.url)

        fuzzable_params = self._get_fuzzable_params(api)
        if not fuzzable_params:
            self.console.print(
                "[bold yellow]No Jinja template parameters found. Skipping jq extraction.[/]"
            )
            return None

        builder = GradioResponseParserBuilder(client=client)
        _response_parser = builder.generate(api=api, prompt_placeholder="prompt")
        return _response_parser

    def run(self) -> GradioProviders:
        """Runs the interactive CLI tool and returns generated providers."""
        self.console.print(
            Panel("[bold green]Gradio Provider Generator[/]", expand=False)
        )
        providers = []

        while True:
            action = Prompt.ask(
                "[bold cyan]Do you want to (1) Inspect APIs or (2) Generate Providers? (Enter 1 or 2)[/]",
                default="2",
            )

            if action == "1":
                self._inspect_apis()
            elif action == "2":
                selected_apis = self._get_user_selected_apis()
                if not selected_apis:
                    self.console.print("[bold red]No APIs selected. Exiting.[/]")
                    return None

                apis: List[GradioProviderApi] = []
                for api_spec in self.api_specs.apis:
                    if api_spec.api_name in selected_apis:
                        params = self._get_user_params(
                            api_spec.api_name, api_spec.params
                        )
                        apis.append(
                            GradioProviderApi(path=api_spec.api_name, params=params)
                        )
                api = apis[0]
                provider_config = GradioProviderConfig(url=self.url, apis=[api])
                provider = GradioProvider(config=provider_config)
                providers.append(provider)

                self.console.print("\n[bold green]Provider generated successfully![/]")
                res_parser = self._learn_response_structure(provider, api)
                api.transform_response = res_parser
                if res_parser:
                    self.console.print(
                        f"\n[bold cyan]Generated Response Location :[/] `{res_parser.model_dump()}`"
                    )

                if (
                    Prompt.ask(
                        "[bold cyan]Do you want to add more APIs (yes/no)[/]",
                        default="no",
                    ).lower()
                    == "no"
                ):
                    break

        return GradioProviders(providers=providers)

    def save_yaml(self, providers: GradioProviders, filename: Optional[str] = None):
        """Saves a list of providers to a YAML file."""
        filename = filename or Prompt.ask(
            "[bold magenta]Enter filename to save as (default: gradio_providers.yaml)[/]",
            default="gradio_providers.yaml",
        )
        yaml_output = yaml.dump(providers.model_dump(), sort_keys=False)
        with open(filename, "w") as f:
            f.write(yaml_output)
        self.console.print(f"[bold green]Configuration saved to {filename} ✅[/]")


# Example Usage
if __name__ == "__main__":
    generator = GradioProviderGenerator()
    providers = generator.run()
    if providers:
        providers.save_yaml(providers)
