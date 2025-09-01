import json
from typing import Any

from anyio import Path

from intuned_cli.utils.api_helpers import load_intuned_json
from intuned_cli.utils.error import CLIError


class CLIAssertionError(CLIError):
    pass


async def is_auth_enabled() -> bool:
    """
    Check if the auth session is enabled in Intuned.json.
    Returns True if enabled, False otherwise.
    """
    intuned_json = await load_intuned_json()
    return intuned_json.auth_sessions.enabled


async def assert_auth_enabled():
    if not await is_auth_enabled():
        raise CLIAssertionError("Auth session is not enabled, enable it in Intuned.json to use it")


async def assert_auth_consistent(auth_session_id: str | None = None):
    _is_auth_enabled = await is_auth_enabled()
    if _is_auth_enabled and auth_session_id is None:
        raise CLIAssertionError(
            "Auth session is enabled, but no auth session is provided. Please provide an auth session ID."
        )
    if not _is_auth_enabled and auth_session_id is not None:
        raise CLIAssertionError("Auth session is not enabled, enable it in Intuned.json to use it")


async def load_parameters(parameters: str) -> dict[str, Any]:
    """
    Load parameters from a JSON file or a JSON string.
    If the input is a file path, it reads the file and returns the parsed JSON.
    If the input is a JSON string, it parses and returns the JSON.
    """

    try:
        # Check if the input is a file path
        path = Path(parameters)
        if await path.exists():
            content = await path.read_text()
            return json.loads(content)
        else:
            # If not a file, treat it as a JSON string
            return json.loads(parameters)
    except json.JSONDecodeError as e:
        raise CLIError(f"Invalid JSON format: {e}") from e
    except Exception as e:
        raise CLIError(f"Failed to load parameters: {e}") from e
