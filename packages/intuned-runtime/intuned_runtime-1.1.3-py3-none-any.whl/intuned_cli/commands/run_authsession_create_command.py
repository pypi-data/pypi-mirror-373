import arguably
import pytimeparse  # type: ignore

from intuned_cli.controller.authsession import execute_run_create_auth_session_cli
from intuned_cli.utils.auth_session_helpers import assert_auth_enabled
from intuned_cli.utils.auth_session_helpers import load_parameters


@arguably.command  # type: ignore
async def run__authsession__create(
    parameters: str,
    /,
    *,
    id: str | None = None,
    check_attempts: int = 1,
    create_attempts: int = 1,
    proxy: str | None = None,
    timeout: str = "10 min",
    headless: bool = False,
):
    """Create a new auth session

    Args:
        parameters (str): Parameters for the auth session command
        id (str | None, optional): [--id]. ID of the auth session to use for the command. Defaults to auth-session-[current timestamp].
        check_attempts (int, optional): [--check-attempts]. Number of attempts to check the auth session validity. Defaults to 1.
        create_attempts (int, optional): [--create-attempts]. Number of attempts to create a new auth session if it is invalid. Defaults to 1.
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

    await execute_run_create_auth_session_cli(
        id=id,
        input_data=auth_session_input,
        check_retries=check_attempts,
        create_retries=create_attempts,
        headless=headless,
        proxy=proxy,
        timeout=timeout_value,
    )
