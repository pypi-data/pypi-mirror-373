import sys

import arguably
from dotenv import find_dotenv
from dotenv import load_dotenv

from intuned_cli.utils.console import console
from intuned_cli.utils.error import CLIError
from intuned_cli.utils.error import log_automation_error
from runtime.context.context import IntunedContext
from runtime.errors.run_api_errors import AutomationError

from . import commands


def run():
    dotenv = find_dotenv(usecwd=True)
    if dotenv:
        load_dotenv(dotenv, override=True)
    try:
        with IntunedContext():
            arguably.run(name="intuned")
            sys.exit(0)
    except CLIError as e:
        if e.auto_color:
            console.print(f"[bold red]{e.message}[/bold red]")
        else:
            console.print(e.message)
    except AutomationError as e:
        log_automation_error(e)
    except KeyboardInterrupt:
        console.print("[bold red]Aborted[/bold red]")
    except Exception as e:
        console.print(
            f"[red][bold]An error occurred: [/bold]{e}\n[bold]Please report this issue to the Intuned team.[/bold]"
        )
    sys.exit(1)


__all__ = ["commands", "run"]
