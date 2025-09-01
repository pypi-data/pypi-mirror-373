import arguably

from intuned_cli.utils.console import console


@arguably.command  # type: ignore
async def run__authsession():
    """Executes an Intuned authsession run"""

    if arguably.is_target():
        console.print(" (-h/--help) for usage")
        exit(1)
