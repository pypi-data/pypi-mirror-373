import asyncio
import functools
import json
import os.path
from importlib import import_module
from importlib.util import module_from_spec
from importlib.util import spec_from_file_location
from inspect import iscoroutinefunction
from typing import Any
from typing import Callable
from typing import Coroutine
from typing import Optional
from typing import Protocol

from tenacity import retry
from tenacity import retry_if_not_result
from tenacity import RetryError
from tenacity import stop_after_attempt

from runtime.browser.storage_state import get_storage_state
from runtime.browser.storage_state import set_storage_state
from runtime.context import IntunedContext
from runtime.errors.run_api_errors import InvalidSessionError
from runtime.errors.run_api_errors import RunApiError
from runtime.types import RunAutomationSuccessResult
from runtime.types.run_types import PayloadToAppend
from runtime.types.run_types import RunApiParameters

from ..errors import ApiNotFoundError
from ..errors import AutomationError
from ..errors import AutomationNotCoroutineError
from ..errors import NoAutomationInApiError
from .playwright_constructs import get_production_playwright_constructs
from .pydantic_encoder import PydanticEncoder


def import_function_from_api_dir(
    *,
    file_path: str,
    base_dir: Optional[str] = None,
    automation_function_name: str | None = None,
) -> Callable[..., Coroutine[Any, Any, Any]]:
    module_path = file_path.replace("/", ".")

    def _import_module():
        if base_dir is None:
            return import_module(module_path)
        else:
            file_location = os.path.join(base_dir, f"{file_path}.py")
            if not os.path.exists(file_location):
                raise ApiNotFoundError(module_path)
            spec = spec_from_file_location(os.path.basename(file_path), file_location)
            if spec is None:
                raise ApiNotFoundError(module_path)
            module = module_from_spec(spec)
            if spec.loader is None:
                raise ApiNotFoundError(module_path)
            spec.loader.exec_module(module)
            return module

    try:
        module = _import_module()

    except ModuleNotFoundError as e:
        # if the top-level module does not exist, it is a 404
        if e.name == module_path:
            raise ApiNotFoundError(module_path) from e

        # otherwise, it is an import error inside the user code
        raise AutomationError(e) from e
    except RunApiError:
        raise
    except BaseException as e:
        raise AutomationError(e) from e

    automation_functions_to_try: list[str] = []
    if automation_function_name is not None:
        automation_functions_to_try.append(automation_function_name)
    else:
        automation_functions_to_try.append("automation")
        automation_functions_to_try.append("create")
        automation_functions_to_try.append("check")

    err: AttributeError | None = None
    automation_coroutine = None

    name = automation_functions_to_try[0]
    for n in automation_functions_to_try:
        name = n
        try:
            automation_coroutine = getattr(module, name)
        except AttributeError as e:
            err = e
        else:
            break

    if automation_coroutine is None:
        raise NoAutomationInApiError(module_path, automation_functions_to_try) from err

    if not iscoroutinefunction(automation_coroutine):
        raise AutomationNotCoroutineError(module_path)

    return automation_coroutine


class ImportFunction(Protocol):
    def __call__(self, file_path: str, name: Optional[str] = None, /) -> Callable[..., Coroutine[Any, Any, Any]]: ...


async def run_api(
    parameters: RunApiParameters,
    *,
    import_function: ImportFunction | None = None,
) -> RunAutomationSuccessResult:
    from playwright.async_api import ProxySettings

    trace_started: bool = False

    headless = False
    proxy = None
    cdp_address = None

    if parameters.run_options.environment == "standalone":
        headless = parameters.run_options.headless
        proxy_config = parameters.run_options.proxy
        if proxy_config is not None:
            proxy = ProxySettings(
                **proxy_config.model_dump(by_alias=True),
            )
    else:
        cdp_address = parameters.run_options.cdp_address

    async with get_production_playwright_constructs(
        headless=headless,
        proxy=proxy,
        cdp_address=cdp_address,
    ) as (context, page):
        if parameters.tracing.enabled:
            await context.tracing.start(screenshots=True, snapshots=True, sources=True)
            trace_started = True

        if parameters.auth is not None and parameters.auth.session.type == "state":
            if parameters.auth.session.state is None:
                raise InvalidSessionError()
            state = parameters.auth.session.state
            await set_storage_state(
                context=context,
                state=state,
            )
        import_function = import_function or (
            lambda file_path, name=None: import_function_from_api_dir(
                file_path=file_path, automation_function_name=name
            )
        )

        async def _run_automation():
            try:
                automation_coroutine = import_function(parameters.automation_function.name)

                if parameters.auth is not None and parameters.auth.run_check:
                    retry_configs = retry(
                        stop=stop_after_attempt(2),
                        retry=retry_if_not_result(lambda result: result is True),
                        reraise=True,
                    )

                    check_fn = import_function("auth-sessions/check")

                    check_fn_with_retries = retry_configs(check_fn)
                    try:
                        check_result = await check_fn_with_retries(page)
                    except RetryError:
                        check_result = False
                    if type(check_result) is not bool:
                        raise AutomationError(TypeError("Check function must return a boolean"))
                    if not check_result:
                        raise InvalidSessionError()

                automation_coroutine_with_page = functools.partial(automation_coroutine, page)
                if parameters.automation_function.params is None:
                    automation_result = await automation_coroutine_with_page()
                else:
                    automation_result = await automation_coroutine_with_page(parameters.automation_function.params)
                try:
                    automation_result = json.loads(json.dumps(automation_result, cls=PydanticEncoder))
                except TypeError as e:
                    raise AutomationError(TypeError("Result is not JSON serializable")) from e

                response = RunAutomationSuccessResult(
                    result=automation_result,
                )
                extended_payloads = IntunedContext.current().extended_payloads
                if extended_payloads:
                    response.payload_to_append = [
                        PayloadToAppend(
                            api_name=payload["api"],
                            parameters=payload["parameters"],
                        )
                        for payload in extended_payloads
                    ]
                if parameters.retrieve_session:
                    response.session = await get_storage_state(context)
                return response
            except RunApiError as e:
                raise e
            except Exception as e:
                # Get all public attributes of the exception
                raise AutomationError(e) from e

        automation_task = None
        try:
            automation_task = asyncio.create_task(_run_automation())

            # Shield will make the CancelledError get thrown directly here instead of inside `automation_task`
            result = await asyncio.shield(automation_task)
            return result
        except asyncio.CancelledError:
            # Manually cancel the automation task
            if automation_task and not automation_task.done():
                automation_task.cancel()
                try:
                    # Wait for the automation task to be cancelled for a brief moment
                    await asyncio.wait_for(automation_task, timeout=0.1)
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    pass
            raise  # Re-raise the cancellation
        finally:
            if parameters.tracing.enabled is True and trace_started:
                try:
                    await context.tracing.stop(path=parameters.tracing.file_path)
                except Exception as e:
                    print("Error stopping tracing:", e)
                    os.remove(parameters.tracing.file_path)
            await context.close()
