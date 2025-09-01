import json
import os

import arguably

from runtime.browser import launch_browser
from runtime.browser.storage_state import get_storage_state


@arguably.command  # type: ignore
async def browser__save_state(
    *,
    cdp_address: str,
    output_path: str,
):
    """
    Load an auth session to a browser.

    Args:
        cdp_address (str): The CDP address of the browser to save the state from.
        output_path (str): Path to save browser state to.
    """

    async with launch_browser(
        cdp_address=cdp_address,
    ) as (context, _):
        storage_state = await get_storage_state(context)

        path = os.path.join(os.getcwd(), output_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(storage_state.model_dump(by_alias=True), f, indent=2)
