# result_collector.py
import time
from abc import ABC, abstractmethod
from time import sleep
from typing import Dict, List

from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table
from rich.text import Text             
from rich.markup import escape          
import json  

from dtx_models.results import EvalResult


class BaseResultCollector(ABC):
    @abstractmethod
    def add_result(self, result: EvalResult) -> None: ...

    @abstractmethod
    def finalize(self) -> None:
        """Called once after all results are collected. Optional for display/logging."""
        ...


class DummyResultCollector(BaseResultCollector):
    def __init__(self):
        self.results: List[EvalResult] = []

    def add_result(self, result: EvalResult) -> None:
        self.results.append(result)

    def finalize(self) -> None:
        pass  # Nothing to display — headless or test mode


class DummyConsole:
    """A no-op console that suppresses all output (for headless mode)."""
    def print(self, *args, **kwargs):
        pass

    def clear(self):
        pass

    def get_time(self):
        """Return time to satisfy Progress bar interface."""
        return time.time()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

class RichDictPrinter:
    def __init__(
        self,
        title: str = "Items",
        header_key: str = "Key",
        header_value: str = "Description",
    ):
        self.console = Console()
        self.title = title
        self.header_key = header_key
        self.header_value = header_value

    def print(self, data: Dict[str, str]):
        if not data:
            self.console.print("[bold yellow]No data to display.[/bold yellow]")
            return

        table = Table(title=self.title)

        table.add_column(self.header_key, style="cyan", no_wrap=True)
        table.add_column(self.header_value, style="magenta")

        for key, value in data.items():
            table.add_row(str(key), str(value))

        self.console.print(table)


class RichResultVisualizer(BaseResultCollector):
    """
    A class to visualize scanner results using Rich.
    Displays a progress summary during scanning and a detailed final report upon completion.
    """

    def __init__(self, headless=False):
        self.console =  Console(quiet=headless) 
        self.results = []
        self.total_tests = 0
        self.total_passed = 0
        self.total_failed = 0

    def _safe_text(self, x: object) -> Text:
        """
        Return a Rich Text that won't parse markup from untrusted content.
        """
        if x is None:
            return Text("")
        if not isinstance(x, str):
            try:
                x = json.dumps(x, ensure_ascii=False)
            except Exception:
                x = str(x)
        return Text(escape(x), overflow="fold", no_wrap=False)



    def add_result(self, result):
        """
        Add a result object from the scanner for visualization.

        :param result: A result object containing evaluation details.
        """
        self.results.append(result)
        self.total_tests += result.attempts.total
        self.total_passed += result.attempts.success
        self.total_failed += result.attempts.failed
        self._display_summary()

    def _display_summary(self):
        """
        Display a quick progress summary after each result is added.
        """
        table = Table(title=Text("Scanning Progress Summary", style="bold yellow"))
        table.add_column("Progress", justify="center", style="bold blue")

        summary_text = f"Total: {self.total_tests} | Passed: {self.total_passed} | Failed: {self.total_failed}"
        table.add_row(summary_text)

        self.console.clear() # Clear previous summary
        self.console.print(table)

    def finalize(self):
        """
        Display the final detailed report visually using Rich, with structured response details.
        """
        self.console.print(Text("\nFinal Results Report:", style="bold green"))

        with Progress(
            TextColumn("Processing Final Report...", style="bold blue"),     # <- string + style
            BarColumn(),
            TextColumn("{task.percentage:>3.0f}%", style="progress.percentage"),  # no markup brackets
            TextColumn("{task.completed}/{task.total} processed", style="green"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Generating Report", total=len(self.results))

            for result in self.results:
                # Title styled via Text (no bracket markup)
                table = Table(title=Text(f"Attempt ID: {result.run_id}", style="bold yellow"))
                table.add_column("Details", style="bold cyan")

                for resp_status in result.responses:
                    status_text = "✅ Pass" if resp_status.success else "❌ Fail"
                    reason_text = resp_status.description
                    response_text = str(resp_status.response.to_text())

                    first_1000 = response_text[:300]
                    last_1000 = response_text[-300:] if len(response_text) > 300 else ""
                    formatted_response = (
                        f"{first_1000} \n.\n.\n. {last_1000}" 
                        if last_1000 
                        else first_1000
                    )

                    # In case model has done classification of the response
                    classified_labels = resp_status.response.scores
                    # In case model has added a response
                    parsed_response = resp_status.response.response

                    row = Text()
                    row.append("Status: ", style="bold")
                    row.append(status_text, style=("green" if resp_status.success else "red"))
                    row.append("\nReason: ", style="bold")
                    row.append_text(self._safe_text(reason_text))
                    row.append("\nConversation: ", style="bold")
                    row.append_text(self._safe_text(formatted_response))

                    if classified_labels:
                        row.append("\nClassified Labels: ", style="bold")
                        row.append_text(self._safe_text(classified_labels))
                    elif parsed_response:
                        row.append("\nResponse: ", style="bold")
                        row.append_text(self._safe_text(parsed_response))
                    table.add_row(row)

                self.console.print(table)
                progress.update(task, advance=1)
                sleep(0.5) # Simulate processing time

            self.console.print(Text("Final Results Display Complete!", style="bold green"))

