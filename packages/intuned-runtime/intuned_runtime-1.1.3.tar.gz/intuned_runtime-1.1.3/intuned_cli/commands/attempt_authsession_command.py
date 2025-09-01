import arguably

from intuned_cli.utils.console import console


@arguably.command  # type: ignore
async def attempt__authsession():
    """Execute san Intuned authsession attempt"""

    if arguably.is_target():
        console.print(" (-h/--help) for usage")
        exit(1)
