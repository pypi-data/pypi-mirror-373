import functools
import subprocess
from os import environ
from os import path

import arguably
import toml
from more_termcolor import bold  # type: ignore
from more_termcolor import cyan  # type: ignore
from more_termcolor import green  # type: ignore
from more_termcolor import italic  # type: ignore
from more_termcolor import underline  # type: ignore
from more_termcolor import yellow  # type: ignore


@arguably.command  # type: ignore
def publish_packages(
    *,
    sdk: bool = False,
    runtime: bool = False,
    show_diff: bool = False,
    update_template: bool = False,
):
    """
    Publishes the SDK and Runtime packages to `python-packages` repository. Uses the version defined in the pyproject.toml file.
    Args:
        sdk (bool): Publish the SDK package.
        runtime (bool): Publish the Runtime package.
        show_diff (bool): Show the diff of the files that will be copied to the package repo. Configure your git difftool to use your preferred diff tool (VSCode recommended).
        update_template (bool): [-u/--update-template] Update the template versions in the WebApp repo.
    """

    sdk_source_path = None
    sdk_runtime_path = None

    webapp_path = environ.get("WEBAPP_PATH")
    if not webapp_path:
        webapp_resolved_path = path.join(path.dirname(__file__), "..", "..", "..", "..")
        if path.exists(path.join(webapp_resolved_path, ".git")):
            webapp_path = webapp_resolved_path
        else:
            raise ValueError(
                "WebApp repo could not be found. Maybe you are not running the globally-installed CLI. Set WEBAPP_PATH environment variable."
            )
    print(bold("WebApp path"), underline(cyan(path.abspath(webapp_path))))

    sdk_source_path = path.join(webapp_path, "apps", "python-sdk")
    sdk_runtime_path = path.join(webapp_path, "apps", "python-runtime")

    if True not in [sdk, runtime]:
        raise ValueError("You should select at least one package to release")

    _release_package = functools.partial(release_package, webapp_path=webapp_path, show_diff=show_diff)

    if sdk:
        _release_package(
            package_human_name="SDK",
            package_name="intuned-sdk",
            packages_repo_dirname="sdk",
            package_source_path=sdk_source_path,
        )

    if runtime:
        _release_package(
            package_human_name="Runtime",
            package_name="intuned-runtime",
            packages_repo_dirname="runtime",
            package_source_path=sdk_runtime_path,
        )

    runtime_version = check_package_version(sdk_runtime_path, "intuned-runtime")
    sdk_version = check_package_version(sdk_source_path, "intuned-sdk")

    # Only run template generation in production environment
    if update_template:
        update_template_version(webapp_path, runtime_version, sdk_version)
        generate_authoring_template_files(webapp_path)
    else:
        print(bold(f"\n🔍 {yellow('Skipping authoring template generation - only runs in production environment')}"))


def generate_authoring_template_files(webapp_path: str):
    """
    Generates the authoring template files by running the `yarn generate:build-authoring-template-files` command.
    """
    web_app_dir = path.join(webapp_path, "apps", "web")
    if not path.exists(web_app_dir):
        raise ValueError(f"Web app directory not found at {web_app_dir}")

    print(bold("\n📝 Generating authoring template files..."))

    # Run the command to generate the authoring template files
    subprocess.run(
        ["yarn", "generate:build-authoring-template-files"],
        cwd=web_app_dir,
        check=True,
    )
    print(bold(f"\n✨ {green('Authoring template files generated successfully!')}"))


def update_template_version(webapp_path: str, runtime_version: str, sdk_version: str):
    template_path = path.join(
        webapp_path, "apps", "web", "packagerWorkerAssets", "packagerTemplates", "playwright_v1_python", "default"
    )
    pyproject_path = path.join(template_path, "pyproject.toml")
    if not path.exists(pyproject_path):
        raise ValueError(f"pyproject.toml not found at {pyproject_path}")

    with open(pyproject_path) as f:
        pyproject = toml.load(f)

    # Update the runtime and sdk versions
    pyproject["tool"]["poetry"]["dependencies"]["intuned-runtime"]["tag"] = f"runtime-{runtime_version}"
    pyproject["tool"]["poetry"]["dependencies"]["intuned-sdk"]["tag"] = f"sdk-{sdk_version}"

    with open(pyproject_path, "w") as f:
        toml.dump(pyproject, f)

    print(bold(f"\n✨ {green('Updated template versions successfully!')}"))


def release_package(
    *,
    package_human_name: str,
    package_name: str,
    package_source_path: str | None,
    webapp_path: str,
    packages_repo_dirname: str,
    show_diff: bool = False,
):
    print(bold(f"🚀 Releasing {green(package_human_name)}"))
    if not package_source_path:
        package_source_path_input = input(bold(f" Enter {green(package_human_name)} path:"))
        package_source_path = package_source_path_input
    else:
        print(bold(f" {green(package_human_name)} Source Path"), underline(cyan(path.abspath(package_source_path))))
    package_version = check_package_version(package_source_path, package_name)

    print(bold(f" Using package version {green(package_version)} to release:"))

    package_repo_path = path.join(webapp_path, "..", "python-packages", packages_repo_dirname)
    if not path.exists(package_repo_path):
        raise ValueError(
            f"Package path does not exist. The {underline("python-packages")} repo is expected to be next to the {underline("WebApp")} (expected package at {underline(path.abspath(package_repo_path))})"
        )

    package_tag = f"{packages_repo_dirname}-{package_version}"

    # Check if a tag with the sdk_version exists
    result = subprocess.run(
        ["git", "tag", "--list", package_tag], capture_output=True, text=True, cwd=package_repo_path
    )
    should_delete_tag = False
    if package_tag in result.stdout.split():
        raise ValueError(f"Tag {package_version} already exists. Please update the version in the pyproject.toml file.")

    # fetch and pull main branch
    print(bold("\n📡 Fetching main branch..."))
    subprocess.run(["git", "fetch", "origin", "main"], cwd=package_repo_path, check=True)
    print(bold("🔃 Pulling main branch..."))
    subprocess.run(["git", "reset", "--hard", "origin/main"], cwd=package_repo_path, check=True)

    # switch to main branch
    print(bold("🔄 Switching to main branch..."))
    subprocess.run(["git", "checkout", "main"], cwd=package_repo_path, check=True)

    print(bold("📑 Writing source to repo path..."))
    print(
        yellow(
            f"This will delete all files in {underline(path.realpath(package_repo_path))} and copy the source from {underline(path.realpath(package_source_path))}"
        )
    )
    if input("Continue? (y, N) ").lower().strip() != "y":
        raise ValueError("Publish cancelled")

    # delete all files in the repo path except .git
    subprocess.run(
        [
            "find",
            package_repo_path,
            "-mindepth",
            "1",
            "-maxdepth",
            "1",
            "-not",
            "-name",
            ".git",
            "-exec",
            "rm",
            "-rf",
            "{}",
            "+",
        ]
    )
    yes_process = subprocess.Popen(["yes"], stdout=subprocess.PIPE)
    try:
        subprocess.run(
            ["cp", "-rf", f"{path.realpath(package_source_path)}/", path.realpath(package_repo_path)],
            stdin=yes_process.stdout,
            check=True,
        )
    finally:
        yes_process.kill()

    # Commit and push copied changes to main, force with lease
    print(bold("\n📄 Committing changes..."))
    subprocess.run(["git", "add", "."], cwd=package_repo_path, check=True)
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", f"Release {package_human_name} version {package_version}"],
        cwd=package_repo_path,
        check=True,
    )

    try:
        if show_diff:
            print(bold("\n🔍 Showing diff..."))
            print(italic("Close the diff tool to continue. You will be prompted to confirm the release."))
            subprocess.run(["git", "difftool", "HEAD^", "-t", "vscode", "-y"], cwd=package_repo_path, check=True)

        if input("Push? (y, N) ").lower().strip() != "y":
            raise ValueError("Publish cancelled")

        print(bold("\n📝 Pushing changes..."))
        subprocess.run(["git", "push", "origin", "main", "--force-with-lease"], cwd=package_repo_path, check=True)

    except (KeyboardInterrupt, ValueError):
        print(bold("Resetting commit..."))
        # drop the current commit and go back to the previous state
        subprocess.run(["git", "reset", "--hard", "HEAD^"], cwd=package_repo_path, check=True)
        raise

    # Create a tag with the version to the current HEAD and push it
    print(bold(f"\n📝 Creating tag {green(package_tag)}..."))
    if should_delete_tag:
        subprocess.run(["git", "tag", "-d", package_tag], cwd=package_repo_path, check=True)
    subprocess.run(["git", "tag", package_tag], cwd=package_repo_path, check=True)
    subprocess.run(
        ["git", "push", "origin", package_tag, *(["--force"] if should_delete_tag else [])],
        cwd=package_repo_path,
        check=True,
    )

    print(bold(f"\n✨ {green(package_human_name)} released successfully!\n\n"))


def check_package_version(package_path: str, package_expected_name: str):
    if not path.exists(package_path):
        raise ValueError("Invalid package path")
    pyproject_path = path.join(package_path, "pyproject.toml")
    if not path.exists(pyproject_path):
        raise ValueError("pyproject.toml not found in package path")
    with open(pyproject_path) as f:
        pyproject = toml.load(f)
    if not pyproject:
        raise ValueError("Invalid pyproject.toml")
    if not pyproject.get("tool"):
        raise ValueError("Invalid pyproject.toml")
    if not pyproject["tool"].get("poetry"):
        raise ValueError("Invalid pyproject.toml")
    if pyproject["tool"]["poetry"].get("name") != package_expected_name:
        raise ValueError(f"Invalid package name - expected {package_expected_name}")
    if not pyproject["tool"]["poetry"].get("version"):
        raise ValueError("Invalid package version")
    return pyproject["tool"]["poetry"]["version"]
