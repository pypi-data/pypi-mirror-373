import arguably
import pytimeparse  # type: ignore

from intuned_cli.controller.authsession import execute_attempt_create_auth_session_cli
from intuned_cli.utils.auth_session_helpers import assert_auth_enabled
from intuned_cli.utils.auth_session_helpers import load_parameters


@arguably.command  # type: ignore
async def attempt__authsession__create(
    parameters: str,
    /,
    *,
    id: str | None = None,
    proxy: str | None = None,
    timeout: str = "10 min",
    headless: bool = False,
):
    """Create a new auth session

    Args:
        parameters (str): Parameters for the auth session command
        id (str | None, optional): [--id]. ID of the auth session to use for the command. Defaults to ./auth-session-instances/[current timestamp].json.
        proxy (str | None, optional): [--proxy]. Proxy URL to use for the auth session command. Defaults to None.
        timeout (str, optional): [--timeout]. Timeout for the auth session command - milliseconds or pytimeparse-formatted string. Defaults to "10 min".
        headless (bool, optional): [--headless]. Run the API in headless mode (default: False). This will not open a browser window.
    """
    await assert_auth_enabled()

    auth_session_input = await load_parameters(parameters) or {}

    timeout_value = pytimeparse.parse(timeout)  # type: ignore
    if timeout_value is None:
        raise ValueError(
            f"Invalid timeout format: {timeout}. Please use a valid time format like '10 min' or '600 seconds'."
        )

    await execute_attempt_create_auth_session_cli(
        id=id,
        input_data=auth_session_input,
        headless=headless,
        timeout=timeout_value,
        proxy=proxy,
    )
