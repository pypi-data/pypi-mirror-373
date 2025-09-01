import arguably
import pytimeparse  # type: ignore

from intuned_cli.controller.api import AuthSessionInput
from intuned_cli.controller.api import execute_run_api_cli
from intuned_cli.utils.auth_session_helpers import assert_auth_consistent
from intuned_cli.utils.auth_session_helpers import load_parameters


@arguably.command  # type: ignore
async def run__api(
    api_name: str,
    parameters: str,
    /,
    *,
    auth_session: str | None = None,
    retries: int = 1,
    proxy: str | None = None,
    no_auth_session_auto_recreate: bool = False,
    auth_session_check_attempts: int = 1,
    auth_session_create_attempts: int = 1,
    timeout: str = "10 min",
    headless: bool = False,
    output_file: str | None = None,
):
    """Execute san Intuned API run with parameters

    Args:
        api_name (str): Name of the API to run.
        parameters (str): Path to the JSON file containing API parameters OR the parameters as a JSON string.
        auth_session (str | None, optional): [-a/--auth-session]. ID of the auth session to use for the API. This is expected to be in ./auth-session-instances/<id>.
        retries (int, optional): [--retries]. Number of retries for the API call. Defaults to 1.
        proxy (str | None, optional): [--proxy]. Proxy URL to use. Defaults to None.
        no_auth_session_auto_recreate (bool, optional): [--no-auth-session-auto-recreate]. Disable auto recreate for auth session. Defaults to False.
        auth_session_check_attempts (int, optional): [--auth-session-check-attempts]. Auth session check attempts. Defaults to 1.
        auth_session_create_attempts (int, optional): [--auth-session-create-attempts]. Auth session create attempts. Defaults to 1.
        timeout (str, optional): [--timeout]. Timeout - milliseconds or pytimeparse-formatted string. Defaults to "10 min".
        headless (bool, optional): [--headless]. Run the API in headless mode (default: False). This will not open a browser window.
        output_file (str | None, optional): [-o/--output-file]. Output file path. Defaults to None.
    """
    auth_session_auto_recreate = not no_auth_session_auto_recreate

    await assert_auth_consistent(auth_session)

    input_data = await load_parameters(parameters)

    timeout_value = pytimeparse.parse(timeout)  # type: ignore
    if timeout_value is None:
        raise ValueError(
            f"Invalid timeout format: {timeout}. Please use a valid time format like '10 min' or '600 seconds'."
        )

    await execute_run_api_cli(
        api_name=api_name,
        input_data=input_data,
        retries=retries,
        proxy=proxy,
        auth_session=AuthSessionInput(
            id=auth_session,
            auto_recreate=auth_session_auto_recreate,
            check_retries=auth_session_check_attempts,
            create_retries=auth_session_create_attempts,
        )
        if auth_session
        else None,
        timeout=timeout_value,
        headless=headless,
        output_file=output_file,
    )
