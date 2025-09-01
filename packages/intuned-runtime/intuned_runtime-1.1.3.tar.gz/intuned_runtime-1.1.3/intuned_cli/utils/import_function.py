from anyio import Path

from runtime.run.run_api import import_function_from_api_dir
from runtime.run.run_api import ImportFunction


async def get_cli_import_function() -> ImportFunction:
    """
    Import a function from the API directory for CLI usage.
    """
    cwd = await Path().resolve()

    return lambda file_path, name=None: import_function_from_api_dir(
        file_path=file_path, automation_function_name=name, base_dir=str(cwd)
    )
