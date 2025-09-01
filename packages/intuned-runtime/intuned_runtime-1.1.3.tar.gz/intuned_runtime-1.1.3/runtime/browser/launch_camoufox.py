import logging
import os
from contextlib import asynccontextmanager
from typing import Any
from typing import AsyncGenerator
from typing import Tuple

import anyio
from playwright.async_api import Browser
from playwright.async_api import BrowserContext
from playwright.async_api import Page

from .helpers import get_proxy_env

logger = logging.getLogger(__name__)


async def create_user_dir():
    # Create a temporary directory
    playwright_temp_dir = anyio.Path(await anyio.mkdtemp(prefix="pw-"))
    user_dir = playwright_temp_dir / "userdir"

    return await user_dir.absolute()


@asynccontextmanager
async def launch_camoufox(
    headless: bool = True,
    timeout: int = 10,
    **kwargs: Any,
) -> AsyncGenerator[Tuple[BrowserContext, Page], None]:
    from camoufox.async_api import AsyncCamoufox

    dir = await create_user_dir()
    if kwargs.get("proxy") is None:
        proxy_env = get_proxy_env()
    else:
        proxy_env = kwargs.get("proxy")
    kwargs.pop("proxy", None)
    async with AsyncCamoufox(
        main_world_eval=True,
        headless=headless,
        config={"forceScopeAccess": True},  # required
        disable_coop=True,
        geoip=True,
        proxy=proxy_env,
        persistent_context=True,
        user_data_dir=dir,
        i_know_what_im_doing=True,
    ) as camoufox:
        if isinstance(camoufox, Browser):
            context = await camoufox.new_context()
        else:
            context = camoufox
        context.set_default_timeout(timeout * 1000)

        async def remove_dir_after_close(*_: Any, **__: Any) -> None:
            if not dir:
                return
            os.system(f"rm -rf {os.path.realpath(dir)}")

        context.once("close", remove_dir_after_close)
        yield context, context.pages[0]
