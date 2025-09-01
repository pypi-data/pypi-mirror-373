import arguably

from intuned_cli.utils.console import console


@arguably.command  # type: ignore
async def attempt():
    """Executes an Intuned attempt."""

    if arguably.is_target():
        console.print(" (-h/--help) for usage")
        exit(1)
