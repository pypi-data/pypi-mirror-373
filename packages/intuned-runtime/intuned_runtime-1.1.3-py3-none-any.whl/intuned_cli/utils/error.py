import traceback

from intuned_cli.utils.console import console
from runtime.errors.run_api_errors import AutomationError


class CLIError(Exception):
    """Base class for CLI errors."""

    def __init__(self, message: str, auto_color: bool = True):
        """
        Initialize the CLIError.

        Args:
            message (str): The error message.
            auto_color (bool): Whether to automatically color the error message.
        """
        super().__init__(message)
        self.message = message
        self.auto_color = auto_color


def log_automation_error(e: AutomationError):
    console.print("[bold red]An error occurred while running the API:[/bold red]")

    stack_trace = traceback.format_exception(type(e.error), value=e.error, tb=e.error.__traceback__)
    console.print(f"[red]{''.join(stack_trace)}[/red]")
