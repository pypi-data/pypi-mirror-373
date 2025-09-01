import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager
from typing import Any

import anyio

from .helpers import get_proxy_env

logger = logging.getLogger(__name__)


chromium_launch_args_to_ignore = [
    "--disable-field-trial-config",
    "--disable-background-networking",
    "--enable-features=NetworkService,NetworkServiceInProcess",
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-back-forward-cache",
    "--disable-breakpad",
    "--disable-client-side-phishing-detection",
    "--disable-component-extensions-with-background-pages",
    "--disable-component-update",
    "--no-default-browser-check",
    "--disable-default-apps",
    "--disable-dev-shm-usage",
    "--disable-extensions",
    "--disable-features=ImprovedCookieControls,LazyFrameLoading,GlobalMediaControls,DestroyProfileOnBrowserClose,MediaRouter,DialMediaRouteProvider,AcceptCHFrame,AutoExpandDetailsElement,CertificateTransparencyComponentUpdater,AvoidUnnecessaryBeforeUnloadCheckSync,Translate,TranslateUI",
    "--allow-pre-commit-input",
    "--disable-hang-monitor",
    "--disable-ipc-flooding-protection",
    "--disable-prompt-on-repost",
    "--disable-renderer-backgrounding",
    "--force-color-profile=srgb",
    "--metrics-recording-only",
    "--no-first-run",
    "--enable-automation",
    "--password-store=basic",
    "--use-mock-keychain",
    "--no-service-autorun",
    "--export-tagged-pdf",
    "--enable-use-zoom-for-dsf=false",
    "--disable-popup-blocking",
]


async def create_user_dir_with_preferences():
    # Create a temporary directory
    playwright_temp_dir = anyio.Path(await anyio.mkdtemp(prefix="pw-"))
    user_dir = playwright_temp_dir / "userdir"
    default_dir = user_dir / "Default"

    # Create the default directory recursively
    await default_dir.mkdir(parents=True, exist_ok=True)

    # Preferences data
    preferences = {
        "plugins": {
            "always_open_pdf_externally": True,
        }
    }

    # Write preferences to file
    async with await (default_dir / "Preferences").open("w") as f:
        await f.write(json.dumps(preferences))

    return await user_dir.absolute(), await playwright_temp_dir.absolute()


default_user_agent = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
)


@asynccontextmanager
async def launch_chromium(
    headless: bool = True,
    timeout: int = 10,
    cdp_address: str | None = None,
    **kwargs: Any,
):
    from playwright.async_api import async_playwright
    from playwright.async_api import Browser

    extra_args = [
        "--no-first-run",
        "--disable-sync",
        "--disable-translate",
        "--disable-features=TranslateUI",
        "--disable-features=NetworkService",
        "--lang=en",
        "--disable-blink-features=AutomationControlled",
    ]
    async with async_playwright() as playwright:
        if cdp_address is not None:
            browser: Browser = await playwright.chromium.connect_over_cdp(cdp_address)
            context = browser.contexts[0]
            user_preferences_dir = None
            dir_to_clean = None
        else:
            (
                user_preferences_dir,
                dir_to_clean,
            ) = await create_user_dir_with_preferences()
            if kwargs.get("proxy") is None:
                proxy_env = get_proxy_env()
            else:
                proxy_env = kwargs.get("proxy")
            # Remove proxy from kwargs if it exists
            kwargs.pop("proxy", None)
            viewport = kwargs.get("viewport", {"width": 1280, "height": 800})
            kwargs.pop("viewport", None)

            if headless:
                chromium_launch_args_to_ignore.append("--headless")
                extra_args.append("--headless=new")

            context = await playwright.chromium.launch_persistent_context(
                os.fspath(user_preferences_dir),
                headless=headless,
                viewport=viewport,
                proxy=proxy_env,
                # ignore_default_args=chromium_launch_args_to_ignore,
                user_agent=os.environ.get("USER_AGENT", default_user_agent),
                # args=extra_args,
                **kwargs,
            )
        context.set_default_timeout(timeout * 1000)

        async def remove_dir_after_close(*_: Any, **__: Any) -> None:
            if not dir_to_clean:
                return
            if not await dir_to_clean.exists():
                return

            process = await asyncio.create_subprocess_exec(
                "rm",
                "-rf",
                os.fspath(dir_to_clean),  # Using subprocess to remove the directory
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await process.wait()

        context.once("close", remove_dir_after_close)
        yield context, context.pages[0]


async def dangerous_launch_chromium(
    headless: bool = True,
    timeout: int = 10,
    cdp_url: str | None = None,
    port: int | None = None,
    **kwargs: Any,
):
    from playwright.async_api import async_playwright
    from playwright.async_api import Browser

    extra_args = [
        "--no-first-run",
        "--disable-sync",
        "--disable-translate",
        "--disable-features=TranslateUI",
        "--disable-features=NetworkService",
        "--lang=en",
        "--disable-blink-features=AutomationControlled",
    ]
    playwright = await async_playwright().start()
    if cdp_url is not None:
        logging.info(f"Connecting to cdp: {cdp_url}")
        browser: Browser = await playwright.chromium.connect_over_cdp(cdp_url)
        browser.on("disconnected", lambda _: logging.info("Browser Session disconnected"))
        context = browser.contexts[0]
        user_preferences_dir = None
        dir_to_clean = None
    else:
        logging.info("Launching local browser")
        user_preferences_dir, dir_to_clean = await create_user_dir_with_preferences()
        logging.info(f"Using user data directory: {user_preferences_dir}")
        if kwargs.get("proxy") is None:
            proxy_env = get_proxy_env()
        else:
            proxy_env = kwargs.get("proxy")
        # Remove proxy from kwargs if it exists
        kwargs.pop("proxy", None)
        viewport = kwargs.get("viewport", {"width": 1280, "height": 800})
        kwargs.pop("viewport", None)

        if headless:
            chromium_launch_args_to_ignore.append("--headless")
            extra_args.append("--headless=new")

        if port:
            extra_args.append(f"--remote-debugging-port={port}")

        context = await playwright.chromium.launch_persistent_context(
            os.fspath(user_preferences_dir),
            headless=headless,
            viewport=viewport,
            proxy=proxy_env,
            ignore_default_args=chromium_launch_args_to_ignore,
            user_agent=os.environ.get("USER_AGENT", default_user_agent),
            args=extra_args,
            **kwargs,
        )
        context.set_default_timeout(timeout * 1000)

        async def remove_dir_after_close(*_: Any, **__: Any) -> None:
            if not dir_to_clean:
                return
            if not await dir_to_clean.exists():
                return

            process = await asyncio.create_subprocess_exec(
                "rm",
                "-rf",
                os.fspath(dir_to_clean),  # Using subprocess to remove the directory
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await process.wait()

        context.once("close", remove_dir_after_close)
    return playwright, context
