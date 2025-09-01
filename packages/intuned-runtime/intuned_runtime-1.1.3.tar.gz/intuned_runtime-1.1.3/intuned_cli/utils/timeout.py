import asyncio
from contextlib import asynccontextmanager

from runtime.context.context import IntunedContext
from runtime.errors.run_api_errors import AutomationError


@asynccontextmanager
async def extendable_timeout(timeout: float):
    try:
        async with asyncio.timeout(timeout) as tm:
            existing_extend_timeout = IntunedContext.current().extend_timeout

            async def extend_timeout():
                tm.reschedule(asyncio.timeout(timeout).when())
                if existing_extend_timeout:
                    await existing_extend_timeout()

            IntunedContext.current().extend_timeout = extend_timeout
            try:
                yield
            finally:
                IntunedContext.current().extend_timeout = existing_extend_timeout
    except asyncio.TimeoutError as e:
        raise AutomationError(Exception("Timed out")) from e
