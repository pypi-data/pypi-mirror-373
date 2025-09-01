from typing import Literal

import httpx
from anyio import Path

from intuned_cli.constants import readme
from intuned_cli.types import DirectoryNode
from intuned_cli.types import FileNode
from intuned_cli.types import FileNodeContent
from intuned_cli.types import FileSystemTree
from intuned_cli.utils.backend import get_base_url
from intuned_cli.utils.console import console
from intuned_cli.utils.error import CLIError
from intuned_cli.utils.exclusions import exclusions as default_excludes

PythonTemplateName = Literal["python-empty"]

python_template_name: PythonTemplateName = "python-empty"


async def check_empty_directory() -> bool:
    cwd = await Path().resolve()
    try:
        if not await cwd.is_dir():
            raise CLIError("The current path is not a directory.")

        files = [f async for f in cwd.iterdir() if await f.is_file()]
        significant_files = [f for f in files if f.name not in default_excludes]

        return len(significant_files) == 0
    except FileNotFoundError as e:
        raise CLIError("The specified directory does not exist.") from e


async def fetch_project_template(template_name: PythonTemplateName) -> FileSystemTree:
    """
    Fetch the project template from the templates directory.

    Args:
        template_name (PythonTemplateName): The name of the template to fetch.

    Returns:
        FileSystemTree: The fetched template.
    """
    base_url = get_base_url()
    url = f"{base_url}/api/templates/{template_name}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise CLIError(f"Failed to fetch template '{template_name}': {response.text}")
        template_data = response.json()
    return FileSystemTree.model_validate(template_data["template"])


def prepare_cli_template(file_tree: FileSystemTree):
    file_tree.root["parameters"] = DirectoryNode(directory=FileSystemTree(root={}))

    file_tree.root["README.md"] = FileNode(file=FileNodeContent(contents=readme))


async def mount_file_tree(file_tree: FileSystemTree, working_directory: Path | None = None):
    working_directory = working_directory or await Path().resolve()
    if not await working_directory.is_dir():
        raise CLIError(f"The specified working directory '{working_directory}' is not a directory.")
    for name, node in file_tree.root.items():
        node_path = working_directory / name
        if isinstance(node, DirectoryNode):
            await node_path.mkdir(parents=True, exist_ok=True)
            await mount_file_tree(node.directory, working_directory=node_path)
        else:
            await node_path.write_text(node.file.contents)


async def write_project_from_file_tree(template_name: PythonTemplateName, is_target_directory_empty: bool):
    if not is_target_directory_empty:
        response = (
            console.input(
                "[bold]The current directory is not empty. Do you want to proceed and override files?[/bold] (y/N)"
            )
            .strip()
            .lower()
        )
        confirmed = response in ["y", "yes"]
        if not confirmed:
            raise CLIError("Project initialization cancelled")

    console.print(f"[cyan]🚀 Initializing[/cyan] [bold]{template_name}[/bold] [cyan]project...[/cyan]")

    project_template = await fetch_project_template(template_name)
    console.print("[cyan]🔨 Creating project files...[/cyan]")

    prepare_cli_template(project_template)
    await mount_file_tree(project_template)

    console.print(
        "[green][bold]🎉 Project initialized successfully![/bold][/green] [bright_green]Run[/bright_green] [bold]poetry install[/bold] [bright_green]to install dependencies and start coding![/bright_green]"
    )
