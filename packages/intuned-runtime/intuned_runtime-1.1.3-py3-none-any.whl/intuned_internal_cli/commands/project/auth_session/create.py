import json
import os
from typing import Any

import arguably

from runtime.context.context import IntunedContext
from runtime.errors.run_api_errors import RunApiError
from runtime.run.intuned_settings import load_intuned_settings
from runtime.run.run_api import import_function_from_api_dir
from runtime.run.run_api import run_api
from runtime.types.run_types import AutomationFunction
from runtime.types.run_types import CDPRunOptions
from runtime.types.run_types import RunApiParameters
from runtime.types.run_types import StandaloneRunOptions
from runtime.types.run_types import TracingDisabled


@arguably.command  # type: ignore
async def project__auth_session__create(
    *,
    no_headless: bool = False,
    cdp_address: str | None = None,
    input_file: str | None = None,
    input_json: str | None = None,
    output_path: str | None = None,
):
    """
    Run auth session create

    Args:
        cdp_address (str): Browser CDP address
        input_file (str | None, optional): Auth session create input file path.
        input_json (str | None, optional): Auth session create input JSON string.
        output_path (str | None, optional): Path to save the auth session. If not provided, the auth session will not be saved.
    """

    input_data = None
    if input_file:
        with open(input_file) as f:
            input_data = json.load(f)
    elif input_json:
        input_data = json.loads(input_json)

    # Load the intuned settings
    intuned_settings = await load_intuned_settings()
    if not intuned_settings.auth_sessions.enabled:
        raise Exception("Auth sessions are not enabled")

    def import_function(file_path: str, function_name: str | None = None):
        return import_function_from_api_dir(
            file_path=file_path,
            automation_function_name=function_name,
            base_dir=os.path.join(os.getcwd()),
        )

    async def get_auth_session_parameters() -> dict[str, Any]:
        return input_data or dict[str, Any]()

    IntunedContext.current().get_auth_session_parameters = get_auth_session_parameters
    try:
        result = await run_api(
            RunApiParameters(
                automation_function=AutomationFunction(
                    name="auth-sessions/create",
                    params=input_data,
                ),
                tracing=TracingDisabled(),
                run_options=CDPRunOptions(
                    cdp_address=cdp_address,
                )
                if cdp_address is not None
                else StandaloneRunOptions(
                    headless=not no_headless,
                ),
                retrieve_session=True,
            ),
            import_function=import_function,
        )
        session = result.session
        if not session:
            raise Exception("Could not capture auth session")
    except RunApiError as e:
        raise Exception(f"Error running auth session create: {e}") from e

    if not output_path:
        print("Output path not set, discarding auth session")
        return

    full_output_path = (
        os.path.abspath(output_path) if os.path.isabs(output_path) else os.path.join(os.getcwd(), output_path)
    )

    os.makedirs(os.path.dirname(full_output_path), exist_ok=True)
    with open(full_output_path, "w") as f:
        json.dump(session.model_dump(by_alias=True), f, indent=2)
