import json
import os
from typing import Any

import arguably
import pydantic  # type: ignore
from more_termcolor import bold  # type: ignore
from more_termcolor import green  # type: ignore
from more_termcolor import red  # type: ignore
from tenacity import retry
from tenacity import retry_if_not_result
from tenacity import RetryError
from tenacity import stop_after_attempt

from runtime.context.context import IntunedContext
from runtime.errors.run_api_errors import RunApiError
from runtime.run.intuned_settings import load_intuned_settings
from runtime.run.run_api import import_function_from_api_dir
from runtime.run.run_api import run_api
from runtime.types.run_types import Auth
from runtime.types.run_types import AutomationFunction
from runtime.types.run_types import CDPRunOptions
from runtime.types.run_types import RunApiParameters
from runtime.types.run_types import StandaloneRunOptions
from runtime.types.run_types import StateSession
from runtime.types.run_types import StorageState
from runtime.types.run_types import TracingDisabled


@arguably.command  # type: ignore
async def project__auth_session__check(
    *,
    no_headless: bool = False,
    cdp_address: str | None = None,
    auth_session_path: str,
    auth_session_parameters: str | None = None,
):
    """
    Check the auth session.

    Args:
        cdp_address (str): The CDP address of the browser to load the auth session to.
        auth_session_path (str): Path to the auth session file.
        no_headless (bool): Whether to run the browser in headless mode.
        auth_session_parameters (str | None): JSON string with auth session parameters.
    """
    intuned_settings = await load_intuned_settings()
    if not intuned_settings.auth_sessions.enabled:
        raise Exception("Auth sessions are not enabled")

    if not os.path.exists(auth_session_path):
        raise Exception("Auth session file does not exist")

    with open(auth_session_path) as f:
        try:
            auth_session = StorageState(**json.load(f))
        except (json.JSONDecodeError, TypeError) as e:
            raise Exception("Auth session file is not a valid JSON file") from e
        except pydantic.ValidationError as e:
            raise Exception(f"Auth session file is not valid: {e}") from e

    retry_configs = retry(stop=stop_after_attempt(2), retry=retry_if_not_result(lambda result: result is True))

    def import_function(file_path: str, function_name: str | None = None):
        return import_function_from_api_dir(
            file_path=file_path,
            automation_function_name=function_name,
            base_dir=os.path.join(os.getcwd()),
        )

    async def get_auth_session_parameters() -> dict[str, Any]:
        assert auth_session_parameters is not None
        try:
            return json.loads(auth_session_parameters)
        except json.JSONDecodeError as e:
            raise Exception("Auth session parameters are not a valid JSON string") from e

    if auth_session_parameters is not None:
        IntunedContext.current().get_auth_session_parameters = get_auth_session_parameters

    try:

        async def check_fn():
            result = await run_api(
                RunApiParameters(
                    automation_function=AutomationFunction(
                        name="auth-sessions/check",
                        params=None,
                    ),
                    tracing=TracingDisabled(),
                    run_options=CDPRunOptions(
                        cdp_address=cdp_address,
                    )
                    if cdp_address is not None
                    else StandaloneRunOptions(headless=not no_headless),
                    auth=Auth(
                        run_check=False,
                        session=StateSession(
                            state=auth_session,
                        ),
                    ),
                ),
                import_function=import_function,
            )
            check_result = result.result
            return check_result is True

        check_fn_with_retries = retry_configs(check_fn)
        try:
            result = await check_fn_with_retries()
        except RetryError:
            result = False
        success = type(result) is bool and result
        print(bold("Check result is"), bold(red(result)) if not success else bold(green(result)))
        if not success:
            raise Exception("Auth session check failed")
    except RunApiError as e:
        raise Exception(f"Error running auth session check: {e}") from e
