import asyncio

from runtime.context.context import IntunedContext

_debounce_time = 60  # seconds


def extend_timeout():
    context = IntunedContext.current()

    if context.extend_timeout is not None:
        call_extend_timeout_api = context.extend_timeout
        asyncio.create_task(asyncio.wait_for(call_extend_timeout_api(), timeout=10))
