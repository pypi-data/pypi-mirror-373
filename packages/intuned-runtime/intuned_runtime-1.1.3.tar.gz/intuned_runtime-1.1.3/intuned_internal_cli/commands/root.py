import arguably


@arguably.command  # type: ignore
async def __root__():
    """Internal Intuned CLI.

    This command is intended for internal use by Intuned and is not intended for general users.
    Breaking changes and experimental features may be present.

    If you are not an Intuned developer, please use the main Intuned CLI instead.
    """
    if arguably.is_target():
        print("-h/--help")
        exit(1)
