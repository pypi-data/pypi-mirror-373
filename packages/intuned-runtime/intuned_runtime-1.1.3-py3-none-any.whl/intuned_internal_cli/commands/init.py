import json
import os
from typing import Any

import arguably
import toml
from more_termcolor import bold  # type: ignore
from more_termcolor import green  # type: ignore

from ..utils.code_tree import get_project_name


@arguably.command  # type: ignore
def init(
    *,
    yes_to_all: bool = False,
    no_to_all: bool = False,
    project_name: str | None,
):
    """
    Initializes current app, creating pyproject.toml and Intuned.json files. Will ask for confirmation before overwriting existing files.

    Args:
        yes_to_all (bool): [-y/--yes] Answer yes to all confirmation prompts
        no_to_all (bool): [-n/--no] Answer no to any confirmation prompts
        project_name (str | None): Name of the project. Will automatically resolve if not provided.

    Returns:
        None
    """

    if yes_to_all and no_to_all:
        raise ValueError("Cannot specify both --yes and --no")

    def should_write_file(file: str) -> bool:
        if not os.path.exists(file):
            return True
        if no_to_all:
            return False
        elif yes_to_all:
            print(bold(f"Overwriting {green(file)}"))
            return True
        return input(f"Overwrite {green(file)}? (y/N) ").lower().strip() == "y"

    project_name = project_name or get_project_name(".")
    print(bold("Initializing"), green(project_name))

    def print_created(file: str) -> None:
        print(bold("📦 Created"), green(file))

    pyproject_name = "pyproject.toml"
    if should_write_file(pyproject_name):
        with open(pyproject_name, "w") as f:
            toml.dump(_get_pyproject(project_name), f)
        print_created(pyproject_name)

    intuned_json_name = "Intuned.json"
    if should_write_file(intuned_json_name):
        with open(intuned_json_name, "w") as f:
            json.dump(_get_intuned_json(project_name), f, indent=2)
        print_created(intuned_json_name)

    readme_name = "README.md"
    if should_write_file(readme_name):
        with open(readme_name, "w") as f:
            f.write(_get_readme(project_name))
        print_created(readme_name)

    print(bold("✨ Done!"))


def _get_pyproject(project_name: str) -> dict[str, Any]:
    return {
        "build-system": {"requires": ["poetry-core>=1.2.0"], "build-backend": "poetry.core.masonry.api"},
        "tool": {
            "poetry": {
                "package-mode": False,
                "name": project_name,
                "version": "0.0.1",
                "description": f"Project {project_name}",
                "authors": ["Intuned <service@intunedhq.com>"],
                "readme": "README.md",
                "dependencies": {
                    "python": ">=3.12,<3.13",
                    "intuned-runtime": {
                        "git": "ssh://git@github.com/Intuned/python-packages.git",
                        "tag": "runtime-latest",
                        "subdirectory": "runtime",
                    },
                    "intuned-sdk": {
                        "git": "ssh://git@github.com/Intuned/python-packages.git",
                        "tag": "sdk-latest",
                        "subdirectory": "sdk",
                    },
                },
            }
        },
    }


def _get_intuned_json(_project_name: str) -> dict[str, Any]:
    return {
        "authSessions": {"enabled": False},
        "scale": {"machineCount": 1, "softLimit": 1, "hardLimit": 5, "memory": 2048, "cpus": 6},
        "proxy": {"enabled": False},
    }


def _get_readme(project_name: str) -> str:
    return (
        f"# `{project_name}` Intuned Automation Project\n"
        f"\n"
        f"\n"
        f"## Getting started\n"
        f"- Install dependencies: `poetry install`\n"
        f"- Activate virtual environment: `poetry shell`\n"
        f"- Project commands: `intuned project --help`\n"
        f"  - Run the project:\n"
        f"    - Sample mode: `intuned project run`\n"
        f"    - Full mode: `intuned project run --mode full`\n"
        f"    - Single mode: `intuned project run --mode single`\n"
        f"  - Deploy the project: `intuned project deploy`\n"
        f"  - Use `--help` for full details on each command.\n"
        f"\n"
        f"## SDK\n"
        f"- If you want to use a specific version of the SDK, make sure to change the tag from `sdk-latest` to `sdk-<version>` in **pyproject.toml**.\n"
    )
