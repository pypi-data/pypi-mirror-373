# Intuned Python Runtime

Runtime commands for Intuned platform Python automations.

## Dependencies

- Requires Python 3.12 or higher.
- Install poetry: `pip install poetry`
- Install dependencies: `poetry install`
- Activate virtual environment: `poetry shell`
- Now you have access to `intuned` cli from within project.

## Install globally

- This project can be installed globally on the system to use `intuned` cli anywhere
- Make sure you are not in a virtual environment. `which python` should point to system python.
  - If you are, `deactivate` to exit virtual environment. Or open in an external terminal (from outside vscode if it doesn't work)
- Run `pip install -e .` from the root of the project.

## Commands

All commands have `-h` flag to show help.

### `intuned init`

- Initializes a project. Creates `pyproject.toml`, `Intuned.json` and `README.md` files.
- Prompts for confirmation for each file that already exists.
- Options:
  - `--yes/-y` flag to overwrite all files.
  - `--no/-n` flag to not overwrite any files.

### `intuned publish-packages`

- Publishes packages to `python-packages` repository.
- Options:
  - `--sdk` flag to publish SDK package. Creates `sdk-<version>` and `sdk-latest` tags for the published version.
  - `--runtime` flag to publish runtime package. Creates `runtime-<version>` and `runtime-latest` tags for the published version.
  - `--overwrite` flag to overwrite the existing version if it exists.
  - `--show-diff` flag to show the diff of the package before publishing. You need to configure a diff tool to be used for `git difftool` command in your git config. [How to configure VS Code as a diff tool](https://www.roboleary.net/vscode/2020/09/15/vscode-git.html#tldr).
  - `--no-latest` flag to not release `latest` tag for the published version.
- Uses the version specified in `pyproject.toml` of each package respectively.
- Uses WebApp directory specified in `WEBAPP_REPO` environment variable or tries to resolve it (only works if installed globally with `-e` flag).
- Uses `python-packages` directory to be sister to WebApp directory `<webapp path>/../python-packages`.
- These packages are used on deployed apps.

### `intuned project run`

- Runs the project.
  - `--mode` to specify the mode to run. Default is `sample`.
    - `--mode sample` extends a sample of payloads to run.
    - `--mode full` runs all extended payloads.
    - `--mode single` runs the initial API only.
  - `--api-name <name>` to specify the initial API to run. Defaults to `default`
  - `--params <params json>` to specify the parameters to the initial API.
  - `--sample-config-str '{<api name>: <sample size>, ...}` to specify the sample config. Only used with `--mode sample`.
  - `--no-headless` to disable headless mode.

### `intuned project deploy`

- Deploys a project and starts a default job.
- Options:
  - `--workspace-info '{"environment_url": <>, "workspace_id": <>, "api_key": <>}'` to specify the workspace info.
  - `--workspace-info-path` to specify the path to a JSON file containing workspace info.
  - `-y/--yes` to skip confirmation.
  - `--project-name` to specify the project name. Resolves the name if not provided.
- Resolves `.gitignore` from current/parent directories to decide what to deploy.
- Resolves `.env` from current/parent directories to get environment variables to deploy.
- Resolves project name from the current/parent directory name if not provided.

### `intuned project serve`

- Serves the project as an HTTP server.
- Options:
  - `--env development/production` to specify the environment to run the server.
    - Development runs using Flask's development server.
    - Production runs using Waitress.
  - `--debug` to run the development server in debug mode. Not supported in production.
- This is used on deployed apps.
