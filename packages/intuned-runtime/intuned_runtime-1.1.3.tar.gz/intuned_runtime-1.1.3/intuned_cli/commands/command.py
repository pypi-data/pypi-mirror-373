import arguably

from intuned_cli.utils.console import console


@arguably.command  # type: ignore
async def __root__(
    *,
    version: bool = False,
):
    """Intuned CLI to initialize, develop and deploy Intuned projects.

    This command is the entry point for the Intuned CLI. It provides various subcommands
    for managing Intuned projects, including initialization, development, and deployment.

    Args:
        version (bool, optional): [-v/--version] Show version information. Defaults to False.
    """

    if version:
        console.print("1.0.0")  # todo: better version handling
        exit(0)

    if arguably.is_target() and not version:
        console.print(" (-h/--help) for usage")
        exit(1)
