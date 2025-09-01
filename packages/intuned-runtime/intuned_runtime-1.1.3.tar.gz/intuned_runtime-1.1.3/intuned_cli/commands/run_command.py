import arguably

from intuned_cli.utils.console import console


@arguably.command  # type: ignore
async def run():
    """Executes an Intuned run."""

    if arguably.is_target():
        console.print(" (-h/--help) for usage")
        exit(1)
