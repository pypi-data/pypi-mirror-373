import os
import subprocess
from typing import List
from typing import Tuple

import arguably
import git
import git.cmd
import semver


@arguably.command  # type: ignore
def project__upgrade():
    """
    Upgrade the project's Intuned runtime and Intuned SDK to the latest version.
    """
    runtime_version, sdk_version = resolve_packages_versions()
    print(f"Upgrading to runtime version {runtime_version} and SDK version {sdk_version}")

    # Upgrade runtime and SDK using poetry
    repo_url = "git+ssh://git@github.com/intuned/python-packages.git"
    cwd = os.getcwd()

    try:
        # Upgrade runtime
        subprocess.run(
            ["poetry", "add", f"{repo_url}@runtime-{runtime_version}#subdirectory=runtime"], check=True, cwd=cwd
        )

        # Upgrade SDK
        subprocess.run(["poetry", "add", f"{repo_url}@sdk-{sdk_version}#subdirectory=sdk"], check=True, cwd=cwd)

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to upgrade packages: {e.stderr}") from e


def get_latest_version(versions: List[str], prefix: str) -> str:
    """
    Get the latest version from a list of versioned tags.
    Filters out dev versions and returns the highest semver version.
    """
    valid_versions: list[str] = []
    for version in versions:
        version_str = version.replace(f"{prefix}-", "")
        try:
            # Skip dev versions
            if "dev" not in version_str:
                semver.VersionInfo.parse(version_str)
                valid_versions.append(version_str)
        except ValueError:
            continue

    if not valid_versions:
        raise ValueError(f"No valid versions found for {prefix}")

    # Sort versions and get the latest
    latest = str(max(map(semver.VersionInfo.parse, valid_versions)))
    return latest


def resolve_packages_versions() -> Tuple[str, str]:
    """
    Resolves the latest versions of runtime and SDK packages using git ls-remote.
    Returns a tuple of (runtime_version, sdk_version)
    """
    try:
        # Use GitPython to get remote tags
        repo = git.cmd.Git()
        refs = repo.ls_remote("--tags", "git@github.com:intuned/python-packages.git").split("\n")

        # Parse the output which looks like:
        # hash    refs/tags/runtime-1.0.1
        # hash    refs/tags/sdk-0.1.1
        tags: list[str] = []
        for line in refs:
            if not line.strip():
                continue
            _, ref = line.split(None, 1)
            tag = ref.replace("refs/tags/", "")
            tags.append(tag)

        # Split into runtime and sdk versions
        runtime_versions = [tag for tag in tags if tag.startswith("runtime-")]
        sdk_versions = [tag for tag in tags if tag.startswith("sdk-")]

        latest_runtime = get_latest_version(runtime_versions, "runtime")
        latest_sdk = get_latest_version(sdk_versions, "sdk")

        return latest_runtime, latest_sdk

    except git.GitCommandError as e:
        raise RuntimeError(f"Failed to fetch tags from git repository: {e.stderr}") from e
