from typing import Any

from pydantic import BaseModel

from runtime.context.context import IntunedContext

from ._call_backend_function import call_backend_function


class AuthSessionParameters(BaseModel):
    parameters: dict[str, Any]


async def get_auth_session_parameters() -> dict[str, Any]:
    """
    Get the auth session parameters from backend.
    """

    context = IntunedContext.current()
    if context.run_context is None:
        raise Exception("get_auth_session_parameters failed due to an internal error (context was not found).")
    if context.run_context.auth_session_id is None:
        raise Exception("Auth sessions are not enabled")

    result = await call_backend_function(
        name=f"auth-session/{context.run_context.auth_session_id}/parameters",
        validation_model=AuthSessionParameters,
    )

    return result.parameters
