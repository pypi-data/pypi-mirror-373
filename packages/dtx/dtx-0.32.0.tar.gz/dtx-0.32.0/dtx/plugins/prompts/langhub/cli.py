import os
import re
import warnings
from typing import List, Optional

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table

# Assume these are defined elsewhere
from dtx_models.prompts import BaseMultiTurnConversation
from dtx_models.template.prompts.langhub import (
    LangchainHubPrompt,
    LangchainHubPromptParam,
    LangHubPromptTemplate,
    LanghubPromptTemplateConfig,
    LangHubPromptTemplates,
)
from dtx.plugins.prompts.langhub.lh_client import (
    LangHubPromptRepository,
    LangHubPromptSearchQuery,
)


class PromptParamBuilder:
    """
    Builds parameters for LangHub prompt by interactively asking the user
    or applying heuristics.
    """

    def __init__(self, console):
        self.console = console

    def build_params(self, input_variables: List[str]) -> List[LangchainHubPromptParam]:
        """Build params from known input variables."""
        params = []

        for var_name in input_variables:
            replacement_value = self._suggest_default(var_name)

            if replacement_value is None:
                replacement_value = Prompt.ask(
                    f"[bold cyan]Enter a default value for parameter '{var_name}'[/]",
                    default="default_value",
                )

            param = LangchainHubPromptParam(name=var_name, value=replacement_value)
            params.append(param)

        return params

    def manual_params(self) -> List[LangchainHubPromptParam]:
        """If no prompt is available, manually ask the user to define params."""
        params = []
        total_params = IntPrompt.ask(
            "[bold cyan]How many parameters do you want to define?[/]", default=1
        )

        for idx in range(total_params):
            var_name = Prompt.ask(
                f"[bold cyan]Enter the name of parameter #{idx + 1}[/]"
            ).strip()

            replacement_value = self._suggest_default(var_name)

            if replacement_value is None:
                replacement_value = Prompt.ask(
                    f"[bold cyan]Enter a default value for parameter '{var_name}'[/]",
                    default="default_value",
                )

            param = LangchainHubPromptParam(name=var_name, value=replacement_value)
            params.append(param)

        return params

    def _suggest_default(self, var_name: str) -> Optional[str]:
        var_name_lower = var_name.lower()

        if var_name_lower in {"context", "background"}:
            self.console.print(
                f"[bold yellow]Auto-setting parameter '{var_name}' to '{{{{context}}}}'[/]"
            )
            return "{{context}}"
        if var_name_lower in {"prompt", "query", "question", "input"}:
            self.console.print(
                f"[bold yellow]Auto-setting parameter '{var_name}' to '{{{{prompt}}}}'[/]"
            )
            return "{{prompt}}"

        return None


class LangHubPromptGenerator:
    """
    Interactive CLI tool for generating LangHub prompts using Rich.
    Enriches provider config with prompt template details from LangSmith if API key is present.
    """

    def __init__(self, console: Console = None):
        self.console = console or Console()
        self.prompts: List[LangHubPromptTemplate] = []
        self.has_langsmith_key = self._check_environment()
        self.repo = LangHubPromptRepository() if self.has_langsmith_key else None

    def _check_environment(self) -> bool:
        """Check if LANGSMITH_API_KEY is available."""
        if "LANGSMITH_API_KEY" not in os.environ:
            warnings.warn(
                "LANGSMITH_API_KEY is not available in environment variables. "
                "Prompt details will not be enriched.",
                stacklevel=2,
            )
            self.console.print(
                "[bold yellow]⚠️ Warning: LANGSMITH_API_KEY is not available in environment variables.[/]\n"
                "Prompt details will not be enriched."
            )
            return False
        return True

    def _extract_full_name(self, full_path: str) -> str:
        """Extract full_name from full path input."""
        pattern = r"(?:https?://smith\.langchain\.com/hub)?/?(.+/.+)"
        match = re.search(pattern, full_path.strip())
        if not match:
            raise ValueError(
                "Invalid full path format.\n"
                "Example: 'https://smith.langchain.com/hub/rlm/rag-prompt' or 'rlm/rag-prompt'"
            )
        return match.group(1).strip("/")

    def _fetch_prompt_details(self, full_name: str) -> Optional[LangchainHubPrompt]:
        """Fetch prompt details from LangSmith Hub and let user choose."""
        if not self.repo:
            self.console.print(
                f"[bold yellow]⚠️ No LANGSMITH_API_KEY. Skipping generating prompt details found for '{full_name}'.[/]"
            )
            return None

        try:
            search_query = LangHubPromptSearchQuery(full_name=full_name)
            parsed_prompts = self.repo.search(search_query, limit=5)

            if not parsed_prompts:
                self.console.print(
                    f"[bold yellow]⚠️ No prompt found for '{full_name}'.[/]"
                )
                return None

            if len(parsed_prompts) == 1:
                self.console.print(
                    f"[bold green]✅ Found 1 prompt for '{full_name}'[/]"
                )
                return parsed_prompts[0]

            # Multiple prompts found, let user choose
            table = Table(
                title="Available Prompts", show_header=True, header_style="bold magenta"
            )
            table.add_column("Index", justify="center", style="bold cyan")
            table.add_column("ID", style="bold yellow")
            table.add_column("Name", style="bold green")
            table.add_column("Description", style="dim")

            for idx, prompt in enumerate(parsed_prompts, start=1):
                table.add_row(
                    str(idx),
                    prompt.metadata.id,
                    prompt.metadata.name,
                    prompt.metadata.description or "-",
                )

            self.console.print(table)

            selected_index = IntPrompt.ask(
                "[bold cyan]Enter the number of the prompt you want to select[/]",
                choices=[str(i) for i in range(1, len(parsed_prompts) + 1)],
            )

            selected_prompt = parsed_prompts[selected_index - 1]
            self.console.print(
                f"[bold green]✅ You selected: {selected_prompt.metadata.name}[/]"
            )

            # Optionally show conversation preview
            conversation = selected_prompt.to_multi_turn_conversation()
            if conversation:
                self._display_conversation(conversation)

            return selected_prompt

        except Exception as e:
            self.console.print(f"[bold red]❌ Error fetching prompt details: {e}[/]")
            return None

    def _display_conversation(self, conversation: BaseMultiTurnConversation):
        """Display the conversation turns."""
        self.console.print(Panel("[bold green]🗨️ Conversation Preview[/]", expand=False))

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Role", style="bold cyan")
        table.add_column("Message", style="bold green")

        for turn in conversation.turns:
            table.add_row(turn.role.value.title(), turn.message)

        self.console.print(table)

    def _get_user_input(self) -> Optional[LangHubPromptTemplate]:
        """Prompt user for full path or search term and create a provider."""
        user_input = Prompt.ask(
            "[bold cyan]Enter the full LangSmith Hub path or search term[/]\n"
            "Example: 'https://smith.langchain.com/hub/rlm/rag-prompt' or 'rlm/rag-prompt' or search term like 'rag'"
        ).strip()

        try:
            try:
                # Try extracting full path
                full_name = self._extract_full_name(user_input)
                prompt_details = self._fetch_prompt_details(full_name)
            except ValueError:
                # If failed, treat input as search term
                self.console.print(
                    "[bold yellow]⚠️ Input does not seem to be a valid path. Performing search...[/]"
                )
                prompt_details = self._search_and_select_prompt(user_input)

                if not prompt_details:
                    return None

                full_name = (
                    prompt_details.metadata.full_name
                )  # Ensure full name comes from selected prompt

            # Build params
            builder = PromptParamBuilder(self.console)
            if prompt_details:
                params = builder.build_params(prompt_details.input_variables)
            else:
                self.console.print(
                    "[bold yellow]No prompt details available. Let's define parameters manually.[/]"
                )
                params = builder.manual_params()

            config = LanghubPromptTemplateConfig(
                full_name=full_name, prompt=prompt_details, params=params
            )
            provider = LangHubPromptTemplate(config=config)
            return provider

        except Exception as e:
            self.console.print(f"[bold red]❌ Error: {e}[/]")
            return None

    def _display_provider(self, provider: LangHubPromptTemplate):
        """Display provider details in a table."""
        table = Table(
            title="✅ Provider Configuration",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Field", style="bold cyan")
        table.add_column("Value", style="bold green")

        provider_data = provider.model_dump()
        table.add_row("Provider ID", provider_data["id"])
        table.add_row("Full Name", provider_data["config"]["full_name"])

        prompt = provider.config.prompt
        if prompt:
            table.add_row("Prompt ID", prompt.metadata.id)
            table.add_row("Prompt Name", prompt.metadata.name)
            table.add_row("Prompt Description", prompt.metadata.description or "-")

        self.console.print(table)

    def _search_and_select_prompt(
        self, search_term: str
    ) -> Optional[LangchainHubPrompt]:
        """Search prompts by keyword and let user select."""
        if not self.repo:
            self.console.print(
                "[bold yellow]⚠️ No LANGSMITH_API_KEY. Cannot search prompts.[/]"
            )
            return None

        try:
            while True:
                search_query = LangHubPromptSearchQuery(query=search_term)
                parsed_prompts = self.repo.search(search_query, limit=10)

                if not parsed_prompts:
                    self.console.print(
                        f"[bold yellow]⚠️ No prompts found for search term '{search_term}'.[/]"
                    )
                    # Ask if user wants to try a new search term
                    search_term = Prompt.ask(
                        "[bold cyan]Enter a new search term (or leave blank to cancel)[/]"
                    ).strip()
                    if not search_term:
                        return None
                    continue  # Retry with new search term

                # Display options
                table = Table(
                    title=f"Search Results for '{search_term}'",
                    show_header=True,
                    header_style="bold magenta",
                )
                table.add_column("Index", justify="center", style="bold cyan")
                table.add_column("Name", style="bold green")
                table.add_column("Description", style="dim")

                for idx, prompt in enumerate(parsed_prompts, start=1):
                    table.add_row(
                        str(idx),
                        prompt.metadata.full_name,
                        prompt.metadata.description or "-",
                    )

                self.console.print(table)

                selected_input = Prompt.ask(
                    "[bold cyan]Enter the number of the prompt you want to select (or leave blank to search again)[/]"
                ).strip()

                if not selected_input:
                    # User wants to search again
                    search_term = Prompt.ask(
                        "[bold cyan]Enter a new search term[/]"
                    ).strip()
                    if not search_term:
                        return None
                    continue  # Restart the loop with the new term

                if not selected_input.isdigit():
                    self.console.print(
                        "[bold red]❌ Invalid input. Please enter a valid number.[/]"
                    )
                    continue  # Retry

                selected_index = int(selected_input)

                if not (1 <= selected_index <= len(parsed_prompts)):
                    self.console.print(
                        f"[bold red]❌ Invalid selection. Enter a number between 1 and {len(parsed_prompts)}.[/]"
                    )
                    continue  # Retry

                selected_prompt = parsed_prompts[selected_index - 1]
                self.console.print(
                    f"[bold green]✅ You selected: {selected_prompt.metadata.name}[/]"
                )

                return selected_prompt

        except Exception as e:
            self.console.print(f"[bold red]❌ Error during search: {e}[/]")
            return None

    def run(self) -> Optional[LangHubPromptTemplates]:
        """Run the interactive CLI tool."""
        self.console.print(
            Panel("[bold green]LangHub Provider Generator[/]", expand=False)
        )

        while True:
            provider = self._get_user_input()
            if provider:
                self._display_provider(provider)
                self.prompts.append(provider)

            if (
                Prompt.ask(
                    "[bold cyan]Do you want to add another provider? (yes/no)[/]",
                    default="no",
                ).lower()
                != "yes"
            ):
                break

        if not self.prompts:
            self.console.print("[bold yellow]No prompts were created. Exiting.[/]")
            return None

        self.console.print("[bold green]🎉 prompts generated successfully![/]")
        return LangHubPromptTemplates(prompts=self.prompts)

    def save_yaml(
        self, prompts: LangHubPromptTemplates, filename: Optional[str] = None
    ):
        """Save prompts to a YAML file."""
        filename = filename or Prompt.ask(
            "[bold magenta]Enter filename to save as (default: langhub_prompts.yaml)[/]",
            default="langhub_prompts.yaml",
        )
        yaml_output = yaml.dump(prompts.model_dump(), sort_keys=False)
        with open(filename, "w") as f:
            f.write(yaml_output)
        self.console.print(f"[bold green]✅ Configuration saved to {filename}[/]")


# Example usage
if __name__ == "__main__":
    generator = LangHubPromptGenerator()
    prompts = generator.run()
    if prompts:
        generator.save_yaml(prompts)
