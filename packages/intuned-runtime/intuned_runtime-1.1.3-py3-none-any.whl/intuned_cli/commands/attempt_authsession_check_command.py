import arguably
import pytimeparse  # type: ignore

from intuned_cli.controller.authsession import execute_attempt_check_auth_session_cli
from intuned_cli.utils.auth_session_helpers import assert_auth_enabled


@arguably.command  # type: ignore
async def attempt__authsession__check(
    id: str,
    /,
    *,
    proxy: str | None = None,
    timeout: str = "10 min",
    headless: bool = False,
):
    """Check an existing auth session

    Args:
        id (str): ID of the auth session to check
        proxy (str | None, optional): [--proxy]. Proxy URL to use for the auth session command. Defaults to None.
        timeout (str, optional): [--timeout]. Timeout for the auth session command - milliseconds or pytimeparse-formatted string. Defaults to "10 min".
        headless (bool, optional): [--headless]. Run the API in headless mode (default: False). This will not open a browser window.
    """
    await assert_auth_enabled()

    timeout_value = pytimeparse.parse(timeout)  # type: ignore
    if timeout_value is None:
        raise ValueError(
            f"Invalid timeout format: {timeout}. Please use a valid time format like '10 min' or '600 seconds'."
        )

    await execute_attempt_check_auth_session_cli(
        id=id,
        headless=headless,
        timeout=timeout_value,
        proxy=proxy,
    )
