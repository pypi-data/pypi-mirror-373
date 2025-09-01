from typing import List, Optional

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.prompt import Confirm, Prompt

from dtx.core import logging
from dtx_models.scope import ProvidersWithEnvironments, ProviderVars

from .playwright.hac import (
    FuzzingRequestExtractor,
    FuzzingRequestModel,
    FuzzingRequestToProviderConverter,
)


class HttpProviderBuilderCli:
    def __init__(
        self,
        fuzz_markers: Optional[List[str]] = None,
        url: Optional[str] = None,
        console: Optional[Console] = None,
    ):
        self.fuzz_markers = fuzz_markers or ["FUZZ"]
        self.console = console or Console()
        self.url = url
        self.converter = FuzzingRequestToProviderConverter(self.fuzz_markers)

    def _build_providers(
        self, requests: List[FuzzingRequestModel]
    ) -> ProvidersWithEnvironments:
        self.console.print(
            Panel(
                "[bold cyan]Building provider configurations...[/bold cyan]\n"
                "This step will analyze requests and convert them to reproducible providers.",
                title="⚙️ Provider Builder",
                expand=False,
            )
        )

        providers = []
        environments: List[ProviderVars] = []  # Always include ENV_HOST by default

        for req in track(requests, description="Converting requests..."):
            provider_with_keys = self.converter.convert(req)
            providers.append(provider_with_keys.provider)
            pvars = ProviderVars()
            if provider_with_keys.env_keys:
                for env in provider_with_keys.env_keys:
                    pvars.vars[env] = f"env.{env}"
            environments.append(pvars)

        self.console.print(
            f"\n[green]✅ Successfully built [bold]{len(providers)}[/bold] providers.[/green]"
        )

        return ProvidersWithEnvironments(providers=providers, environments=environments)

    def dump_yaml(
        self,
        provider_output: ProvidersWithEnvironments,
        filename: str = None,
    ) -> str:
        # class LiteralString(str):
        #     pass

        # def literal_string_representer(dumper, data):
        #     return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")

        # yaml.add_representer(
        #     LiteralString, literal_string_representer, Dumper=yaml.SafeDumper
        # )

        # for provider in provider_output.providers:
        #     raw = provider.config.raw_request
        #     if raw:
        #         provider.config.raw_request = LiteralString(raw)

        filename = filename or "http_providers.yml"
        yaml_output = yaml.dump(provider_output.model_dump(), sort_keys=False)
        with open(filename, "w") as f:
            f.write(yaml_output)
        self.console.print(f"[bold green]Configuration saved to {filename} ✅[/]")

    def run(self) -> ProvidersWithEnvironments:
        logging.basicConfig(level=logging.INFO)

        if not self.url:
            self.url = Prompt.ask("Enter the target URL for fuzzing")

        confirmed = Confirm.ask(
            f"Do you want to open a browser and start capturing requests for [cyan]{self.url}[/cyan]?"
        )
        if not confirmed:
            self.console.print("[yellow]Aborted by user.[/yellow]")
            raise SystemExit(0)

        self.console.print(
            Panel(
                f"[bold magenta]Please insert your {self.fuzz_markers[0]} marker into the prompt or input field in the browser.\n"
                "Once done, close the browser to generate provider configuration.[/bold magenta]",
                title="🧪 Insert FUZZ and Close Browser",
                expand=False,
            )
        )

        extractor = FuzzingRequestExtractor(self.url, fuzz_marker=self.fuzz_markers[0])
        fuzz_requests = extractor.extract_fuzzing_requests()

        return self._build_providers(fuzz_requests)
