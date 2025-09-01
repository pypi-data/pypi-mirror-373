import json
import os

import arguably

from runtime.browser import launch_browser
from runtime.browser.storage_state import set_storage_state
from runtime.run.intuned_settings import load_intuned_settings
from runtime.types.run_types import StorageState


@arguably.command  # type: ignore
async def project__auth_session__load(
    *,
    cdp_address: str,
    auth_session_path: str,
):
    """
    Load an auth session to a browser.

    Args:
        cdp_address (str): The CDP address of the browser to load the auth session to.
        auth_session_path (str): Path to the auth session file.
    """
    intuned_settings = await load_intuned_settings()
    if not intuned_settings.auth_sessions.enabled:
        raise Exception("Auth sessions are not enabled")

    async with launch_browser(
        cdp_address=cdp_address,
    ) as (context, _):
        auth_session_path = os.path.join(os.getcwd(), auth_session_path)
        if not os.path.exists(auth_session_path):
            raise Exception("Auth session file does not exist")

        with open(auth_session_path) as f:
            auth_session = StorageState(**json.load(f))

        await set_storage_state(context, auth_session)
