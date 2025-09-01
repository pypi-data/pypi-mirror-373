from typing import Any
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.async_api import BrowserContext

import logging

from ..types.run_types import Cookie
from ..types.run_types import Origin
from ..types.run_types import SessionStorageOrigin
from ..types.run_types import StorageState

logger = logging.getLogger(__name__)


async def set_storage_state(context: "BrowserContext", state: StorageState):
    # Add cookies if they exist
    await context.add_cookies([cookie.model_dump(by_alias=True) for cookie in state.cookies])  # type: ignore

    # Apply localStorage for each origin
    page = await context.new_page()
    for origin_data in state.origins or []:
        origin = origin_data.origin
        await page.route(
            f"{origin}/*",
            lambda route: route.fulfill(
                body="<html><head><title>Set Storage</title></head><body><h1>Set Storage</h1></body></html>",
                content_type="text/html",
                status=200,
            ),
        )
        try:
            await page.goto(origin)

            # Set localStorage items
            for item in origin_data.local_storage:
                await page.evaluate(
                    """
                    ([key, value]) => {
                        window.localStorage.setItem(key, value)
                    }
                """,
                    [item.name, item.value],
                )
        finally:
            await page.unroute(origin)

    # Apply sessionStorage if available
    if state.session_storage is not None:
        await context.add_init_script(f"""
        const storage = {[s.model_dump(by_alias=True) for s in state.session_storage]};
        for (const {{ origin, sessionStorage }} of storage) {{
            if (window.location.origin === origin) {{
                for (const item of sessionStorage){{
                    const value = window.sessionStorage.getItem(item.name);
                    console.log("value", value);
                    if (!value) {{
                        window.sessionStorage.setItem(item.name, item.value);
                    }}
                    }}
            }}
        }}
    """)

    await page.close()


async def get_storage_state(context: "BrowserContext") -> StorageState:
    from playwright.async_api import Error as PlaywrightError

    storage_state = await context.storage_state()
    cookies = storage_state.get("cookies") or []
    origins = storage_state.get("origins") or []

    session_storage: list[SessionStorageOrigin] = []
    for page in context.pages:
        try:
            session_data: dict[str, Any] = await page.evaluate(
                """
() => {
    const items = { ...window.sessionStorage };
    return {
        origin: window.location.origin,
        sessionStorage: Object.entries(items).map(([name, value]) => ({
        name,
        value,
        })),
    };
}
    """
            )
            session_storage.append(SessionStorageOrigin(**session_data))
        except PlaywrightError as e:
            if "SecurityError" in e.message:
                logger.warning(f"Could not get storage state for page due '{page.url}' to security error.")
                continue
            raise e

    # Ignoring types here because it expects snake case from constructors, but we have alias configured to accept any case correctly
    return StorageState(
        cookies=[Cookie(**cookie) for cookie in cookies],  # type: ignore
        origins=[Origin(**origin) for origin in origins],  # type: ignore
        session_storage=session_storage,
    )
