from contextlib import asynccontextmanager

from playwright.async_api import ProxySettings

from runtime.env import get_browser_type

from .launch_camoufox import launch_camoufox
from .launch_chromium import launch_chromium


@asynccontextmanager
async def launch_browser(
    proxy: ProxySettings | None = None,
    headless: bool = False,
    *,
    cdp_address: str | None = None,
):
    browser_type = get_browser_type()
    match browser_type:
        case "camoufox":
            async with launch_camoufox(headless=headless, proxy=proxy) as (context, page):
                try:
                    yield context, page
                finally:
                    await context.close()
        case "chromium" | _:
            async with launch_chromium(headless=headless, cdp_address=cdp_address, proxy=proxy) as (context, page):
                try:
                    yield context, page
                finally:
                    await context.close()
