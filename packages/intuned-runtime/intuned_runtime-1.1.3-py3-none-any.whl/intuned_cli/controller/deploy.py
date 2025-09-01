import asyncio
import json
import os
import re
import time
import uuid
from itertools import cycle
from typing import Any
from typing import Literal

import httpx
import pathspec
import toml
from anyio import Path
from pydantic import BaseModel

from intuned_cli.types import DirectoryNode
from intuned_cli.types import FileNode
from intuned_cli.types import FileNodeContent
from intuned_cli.types import FileSystemTree
from intuned_cli.types import IntunedJson
from intuned_cli.utils.api_helpers import load_intuned_json
from intuned_cli.utils.backend import get_base_url
from intuned_cli.utils.console import console
from intuned_cli.utils.error import CLIError
from intuned_cli.utils.exclusions import exclusions

supported_playwright_versions = ["1.46.0", "1.52.0"]

project_deploy_timeout = 10 * 60
project_deploy_check_period = 5


class IntunedPyprojectToml(BaseModel):
    class _Tool(BaseModel):
        class _Poetry(BaseModel):
            dependencies: dict[str, Any]

        poetry: _Poetry

    tool: _Tool


async def validate_intuned_project():
    cwd = await Path().resolve()

    pyproject_toml_path = cwd / "pyproject.toml"

    if not await pyproject_toml_path.exists():
        raise CLIError("pyproject.toml file is missing in the current directory.")

    content = await pyproject_toml_path.read_text()
    json_content = toml.loads(content)
    try:
        pyproject_toml = IntunedPyprojectToml.model_validate(json_content)
    except Exception as e:
        raise CLIError(f"Failed to parse pyproject.toml: {e}") from e

    playwright_version = pyproject_toml.tool.poetry.dependencies.get("playwright")

    if playwright_version not in supported_playwright_versions:
        raise CLIError(
            f"Unsupported Playwright version '{playwright_version}'. "
            f"Supported versions are: {', '.join(supported_playwright_versions)}."
        )

    intuned_json = await load_intuned_json()

    api_folder = cwd / "api"
    if not await api_folder.exists() or not await api_folder.is_dir():
        raise CLIError("api directory does not exist in the current directory.")

    if intuned_json.auth_sessions.enabled:
        auth_sessions_folder = cwd / "auth-sessions"
        if not await auth_sessions_folder.exists() or not await auth_sessions_folder.is_dir():
            raise CLIError("auth-sessions directory does not exist in the api directory.")

    return intuned_json


def validate_project_name(project_name: str):
    if len(project_name) > 50:
        raise CLIError("Project name must be 50 characters or less.")

    project_name_regex = r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$"
    if not re.match(project_name_regex, project_name):
        raise CLIError("Project name can only contain lowercase letters, numbers, hyphens, and underscores in between.")

    try:
        import uuid

        uuid.UUID(project_name)
        raise CLIError("Project name cannot be a UUID.")
    except ValueError:
        # Not a valid UUID, continue
        pass


async def get_intuned_api_auth_credentials(
    *, intuned_json: IntunedJson, workspace_id: str | None, api_key: str | None
) -> tuple[str, str]:
    """
    Retrieves the Intuned API authentication credentials from environment variables.

    Returns:
        tuple: A tuple containing the workspace ID and API key.
    """
    workspace_id = workspace_id or intuned_json.workspace_id
    api_key = api_key or os.environ.get("INTUNED_API_KEY")

    if not workspace_id:
        raise CLIError("Workspace ID is required. Please provide it via command line options or Intuned.json")

    if not api_key:
        raise CLIError(
            "API key is required. Please provide it via command line options or INTUNED_API_KEY environment variable."
        )

    return workspace_id, api_key


async def get_file_tree_from_project(path: Path, *, exclude: list[str] | None = None):
    # Create pathspec object for gitignore-style pattern matching
    spec = None
    if exclude:
        spec = pathspec.PathSpec.from_lines("gitwildmatch", exclude)

    async def traverse(current_path: Path, tree: FileSystemTree):
        async for entry in current_path.iterdir():
            relative_path_name = entry.relative_to(path).as_posix()
            basename = entry.name

            # Check if this path should be excluded
            if spec and spec.match_file(relative_path_name):
                continue

            if await entry.is_dir():
                subtree = FileSystemTree(root={})
                tree.root[basename] = DirectoryNode(directory=subtree)
                # For directories, check if the directory itself is excluded
                # If not excluded, traverse into it
                await traverse(entry, subtree)
            elif await entry.is_file():
                tree.root[basename] = FileNode(file=FileNodeContent(contents=await entry.read_text()))

    results = FileSystemTree(root={})
    await traverse(path, results)
    return results


def mapFileTreeToIdeFileTree(file_tree: FileSystemTree):
    """
    Maps the file tree to IDE parameters format by processing parameters directory
    and converting it to ____testParameters structure.
    """

    if not file_tree:
        return

    parameters_node = file_tree.root.get("parameters")
    if parameters_node is None:
        return

    if not isinstance(parameters_node, DirectoryNode):
        return

    api_parameters_map: dict[str, list[dict[str, Any]]] = {}
    cli_parameters = list(parameters_node.directory.root.keys())
    test_parameters = DirectoryNode(directory=FileSystemTree(root={}))

    for parameter_key in cli_parameters:
        # If parameter of type directory, discard it and continue
        parameter = parameters_node.directory.root[parameter_key]

        if isinstance(parameter, DirectoryNode):
            continue

        if not parameter.file.contents.strip():
            continue

        try:
            parameter_payload = json.loads(parameter.file.contents)
        except json.JSONDecodeError:
            continue

        if "__api-name" not in parameter_payload:
            continue

        api = parameter_payload["__api-name"]
        # Create parameter value by excluding __api-name
        parameter_value = {k: v for k, v in parameter_payload.items() if k != "__api-name"}

        test_parameter: dict[str, Any] = {
            "name": parameter_key.replace(".json", ""),
            "lastUsed": False,
            "id": str(uuid.uuid4()),
            "value": json.dumps(parameter_value),
        }

        if api not in api_parameters_map:
            api_parameters_map[api] = []
        api_parameters_map[api].append(test_parameter)

    for api, parameters in api_parameters_map.items():
        # By default, last one used is the last one in the map
        if len(parameters) > 0:
            parameters[-1]["lastUsed"] = True

        test_parameters.directory.root[f"{api}.json"] = FileNode(
            file=FileNodeContent(contents=json.dumps(parameters, indent=2))
        )

    del file_tree.root["parameters"]
    file_tree.root["____testParameters"] = test_parameters


class DeployStatus(BaseModel):
    status: Literal["completed", "failed", "pending"]
    message: str | None = None
    reason: str | None = None


async def check_deploy_status(
    *,
    project_name: str,
    workspace_id: str,
    api_key: str,
):
    base_url = get_base_url()
    url = f"{base_url}/api/v1/workspace/{workspace_id}/projects/create/{project_name}/result"

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code < 200 or response.status_code >= 300:
            if response.status_code == 401:
                raise CLIError("Invalid API key. Please check your API key and try again.")
            if response.status_code == 404:
                raise CLIError(f"Project '{project_name}' not found in workspace '{workspace_id}'.")
            raise CLIError(f"Failed to check deploy status for project '{project_name}': {response.text}")

    data = response.json()
    try:
        deploy_status = DeployStatus.model_validate(data)
    except Exception as e:
        raise CLIError(f"Failed to parse deploy status response: {e}") from e

    return deploy_status


async def deploy_project(
    *,
    project_name: str,
    workspace_id: str,
    api_key: str,
):
    base_url = get_base_url()
    url = f"{base_url}/api/v1/workspace/{workspace_id}/projects/create"
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }
    cwd = await Path().resolve()
    file_tree = await get_file_tree_from_project(cwd, exclude=exclusions)
    mapFileTreeToIdeFileTree(file_tree)

    payload: dict[str, Any] = {
        "name": project_name,
        "codeTree": file_tree.model_dump(mode="json"),
        "isCli": True,
        "language": "python",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code < 200 or response.status_code >= 300:
            if response.status_code == 401:
                raise CLIError("Invalid API key. Please check your API key and try again.")

            raise CLIError(
                f"[red bold]Invalid response from server:[/red bold]\n [bright_red]{response.status_code} {response.text}[/bright_red][red bold]\nProject deployment failed.[/red bold]"
            )

    start_time = time.time()

    async def update_console():
        for spinner in cycle("⠙⠹⠸⠼⠴⠦⠧⠇"):
            await asyncio.sleep(0.05)

            time_elapsed_text = f"{time.time() - start_time:.1f}"
            print("\r", end="", flush=True)
            console.print(
                f"{spinner} [cyan]Deploying[/cyan] [bright_black]({time_elapsed_text}s)[/bright_black] ", end=""
            )

    if console.is_terminal:
        update_console_task = asyncio.create_task(update_console())
    else:
        update_console_task = None
        console.print("[cyan]Deploying[/cyan]")

    try:
        while True:
            await asyncio.sleep(project_deploy_check_period)
            if not console.is_terminal:
                time_elapsed_text = f"{time.time() - start_time:.1f}"
                console.print(f"[cyan]Deploying[/cyan] [bright_black]({time_elapsed_text}s)[/bright_black]")

            try:
                deploy_status = await check_deploy_status(
                    project_name=project_name,
                    workspace_id=workspace_id,
                    api_key=api_key,
                )

                if deploy_status.status == "pending":
                    elapsed_time = time.time() - start_time
                    if elapsed_time > project_deploy_timeout:
                        raise CLIError(f"Deployment timed out after {project_deploy_timeout//60} minutes.")
                    continue

                if deploy_status.status == "completed":
                    if update_console_task:
                        update_console_task.cancel()
                    if console.is_terminal:
                        print("\r", " " * 100)
                    console.print("[green][bold]Project deployed successfully![/bold][/green]")
                    console.print(
                        f"[bold]You can check your project on the platform:[/bold] [cyan underline]{get_base_url()}/projects/{project_name}/details[/cyan underline]"
                    )
                    return

                error_message = (
                    f"[red bold]Project deployment failed:[/bold red]\n{deploy_status.message or 'Unknown error'}\n"
                )
                if deploy_status.reason:
                    error_message += f"Reason: {deploy_status.reason}\n"
                error_message += "[red bold]Project deployment failed[/red bold]"
                raise CLIError(
                    error_message,
                    auto_color=False,
                )
            except Exception:
                if console.is_terminal:
                    print("\r", " " * 100)
                raise
    finally:
        if update_console_task:
            update_console_task.cancel()
