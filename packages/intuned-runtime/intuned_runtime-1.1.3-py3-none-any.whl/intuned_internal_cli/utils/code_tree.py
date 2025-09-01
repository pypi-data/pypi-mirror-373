import os
from datetime import datetime
from typing import Dict
from typing import Union

from more_termcolor import bold  # type: ignore
from more_termcolor import cyan  # type: ignore
from more_termcolor import yellow  # type: ignore
from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern
from typing_extensions import TypedDict


class FileContents(TypedDict):
    contents: str


class FileNode(TypedDict):
    file: FileContents


class DirectoryNode(TypedDict):
    directory: "FileSystemTree"


FileSystemTree = Dict[str, Union[DirectoryNode, FileNode]]


def convert_project_to_code_tree(project_path: str, wait_for_confirm: bool = True) -> FileSystemTree:
    ignore: list[str] | None = None
    cwd = os.path.normpath(project_path)
    while ignore is None and cwd != "/":
        gitignore_path = os.path.join(cwd, ".gitignore")
        if os.path.exists(gitignore_path):
            with open(gitignore_path) as gitignore_file:
                ignore = gitignore_file.read().splitlines()
                print(f"Found .gitignore file: {bold(cyan(gitignore_path))}")
        else:
            cwd = os.path.abspath(os.path.dirname(cwd))
    if ignore is None:
        print(yellow(".gitignore file not found. Deploying all files."))
        ignore = []

    ignore_spec = PathSpec.from_lines(GitWildMatchPattern, ignore)

    files_to_deploy_text = "\n  ".join(["", *ignore_spec.match_tree(project_path, negate=True), ""])
    print("The following files will be deployed:", files_to_deploy_text)
    if wait_for_confirm and input("Continue? (y/N): ").lower().strip() != "y":
        raise ValueError("Deployment cancelled")

    def read_directory(path: str) -> FileSystemTree:
        tree: FileSystemTree = {}
        files_or_dirs = os.listdir(path)

        for item in files_or_dirs:
            item_path = os.path.join(path, item)
            if ignore_spec.match_file(item_path):
                continue
            if os.path.isfile(item_path):
                try:
                    with open(item_path) as file:
                        content = file.read()
                    tree[item] = {"file": {"contents": content}}
                except:
                    pass
            elif os.path.isdir(item_path):
                tree[item] = {"directory": read_directory(item_path)}
        return tree

    tree: FileSystemTree = read_directory(project_path)
    return tree


def get_project_name(path: str):
    path = os.path.abspath(path)
    while path != "/":
        dirname = os.path.basename(path)
        try:
            datetime.strptime(dirname, "%Y-%m-%d_%H:%M")
            path = os.path.dirname(path)
        except ValueError:
            return dirname
    raise ValueError("Could not find project name")
