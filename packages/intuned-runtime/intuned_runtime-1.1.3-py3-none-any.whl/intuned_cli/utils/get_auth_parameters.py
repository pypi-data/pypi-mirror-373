from typing import Any

from runtime.context.context import IntunedContext


def register_get_auth_session_parameters(auth_session_id: str | None = None):
    async def get_auth_session_parameters() -> dict[str, Any]:
        if auth_session_id is None:
            raise ValueError("get_auth_session_parameters cannot be called without using an auth session")

        from intuned_cli.controller.authsession import load_auth_session_instance

        _, metadata = await load_auth_session_instance(auth_session_id)
        if metadata.auth_session_type == "MANUAL":
            raise ValueError("Auth session is recorder-based, it does not have parameters.")
        return metadata.auth_session_input or {}

    IntunedContext.current().get_auth_session_parameters = get_auth_session_parameters
