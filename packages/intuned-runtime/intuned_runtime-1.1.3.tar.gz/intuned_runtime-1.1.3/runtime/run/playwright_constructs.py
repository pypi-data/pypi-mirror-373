from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.async_api import ProxySettings
from ..browser import launch_browser


@asynccontextmanager
async def get_production_playwright_constructs(
    proxy: "ProxySettings | None" = None,
    headless: bool = False,
    *,
    cdp_address: str | None = None,
):
    async with launch_browser(headless=headless, cdp_address=cdp_address, proxy=proxy) as (context, page):
        try:
            yield context, page
        finally:
            await context.close()
