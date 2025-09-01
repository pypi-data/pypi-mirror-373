import arguably

from intuned_cli.controller.init import check_empty_directory
from intuned_cli.controller.init import python_template_name
from intuned_cli.controller.init import write_project_from_file_tree


@arguably.command  # type: ignore
async def init():
    """
    Initializes current app, creating pyproject.toml and Intuned.json files. Will ask for confirmation before overwriting existing files.

    Args:
        template_name (str | None): Name of the template to use.

    Returns:
        None
    """
    is_target_directory_empty = await check_empty_directory()

    await write_project_from_file_tree(python_template_name, is_target_directory_empty)
