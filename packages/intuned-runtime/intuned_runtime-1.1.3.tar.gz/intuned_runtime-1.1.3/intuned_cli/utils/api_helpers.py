from typing import Literal
from typing import overload

from anyio import Path

from intuned_cli.types import IntunedJson
from intuned_cli.utils.error import CLIError


@overload
async def assert_api_file_exists(dirname: Literal["api"], api_name: str) -> None: ...
@overload
async def assert_api_file_exists(dirname: Literal["auth-sessions"], api_name: Literal["create", "check"]) -> None: ...


async def assert_api_file_exists(dirname: Literal["api", "auth-sessions"], api_name: str) -> None:
    """
    Assert that the API file exists in the specified folder.
    """
    path = (await Path().resolve()) / dirname / f"{api_name}.py"
    if not await path.exists():
        raise CLIError("File does not exist")


async def load_intuned_json() -> IntunedJson:
    intuned_json_path = Path("Intuned.json")
    if not await intuned_json_path.exists():
        raise CLIError("Intuned.json file is missing in the current directory.")
    try:
        return IntunedJson.model_validate_json(await intuned_json_path.read_text())
    except Exception as e:
        raise CLIError(f"Failed to parse Intuned.json: {e}") from e
