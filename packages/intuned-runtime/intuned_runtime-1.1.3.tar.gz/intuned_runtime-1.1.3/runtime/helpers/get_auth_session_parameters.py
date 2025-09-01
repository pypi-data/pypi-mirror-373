from typing import Any

from runtime.context.context import IntunedContext


async def get_auth_session_parameters() -> dict[str, Any]:
    """
    Get the auth session parameters from the IntunedContext.
    """
    context = IntunedContext.current()
    if context.get_auth_session_parameters is None:
        raise Exception("get_auth_session_parameters failed due to an internal error (context was not found).")

    return await context.get_auth_session_parameters()
