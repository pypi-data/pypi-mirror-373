import builtins
import json
import os
import sys
import traceback
from collections import Counter
from functools import wraps
from typing import Any
from typing import Literal
from typing import NotRequired
from typing import TypedDict

from more_termcolor import bold  # type: ignore
from more_termcolor import cyan  # type: ignore
from more_termcolor import green  # type: ignore
from more_termcolor import italic  # type: ignore
from more_termcolor import yellow  # type: ignore

from runtime.context.context import IntunedContext
from runtime.errors.run_api_errors import RunApiError
from runtime.run import run_api
from runtime.types import Payload
from runtime.types.run_types import Auth
from runtime.types.run_types import AutomationFunction
from runtime.types.run_types import CDPRunOptions
from runtime.types.run_types import RunApiParameters
from runtime.types.run_types import StandaloneRunOptions


class _RunInput(TypedDict):
    api: str
    parameters: dict[str, Any]
    headless: bool


class _RunSuccessOutput(TypedDict):
    success: Literal[True]
    result: Any
    extended_payloads: NotRequired[list[Payload]]


class _RunErrorOutput(TypedDict):
    success: Literal[False]
    error: list[str]


_RunOutput = _RunSuccessOutput | _RunErrorOutput


class RunResultData(TypedDict):
    input: _RunInput
    output: _RunOutput


async def run_api_for_cli(
    initial_api_to_run: Payload,
    headless: bool = True,
    cdp_address: str | None = None,
    *,
    auth: Auth | None = None,
    print_output: bool = True,
    auth_session_parameters: dict[str, Any] | None = None,
) -> RunResultData:
    sys.path.append(os.path.join(os.getcwd()))

    @wraps(builtins.print)
    def print(*args: ..., **kwargs: ...):
        if print_output:
            return builtins.print(*args, **kwargs)

    to_run: Payload | None = initial_api_to_run
    extended_payloads: list[Payload] = []
    try:
        IntunedContext.current().extend_timeout = extend_timeout
        if auth_session_parameters:

            async def get_auth_session_parameters() -> dict[str, Any]:
                return auth_session_parameters

            IntunedContext.current().get_auth_session_parameters = get_auth_session_parameters
        print(bold(f"\n🏃 Running {green(to_run["api"])}"))
        run_input: _RunInput = {
            "api": to_run["api"],
            "parameters": to_run["parameters"],
            "headless": headless,
        }
        try:
            result = await run_api(
                RunApiParameters(
                    automation_function=AutomationFunction(
                        name=f"api/{to_run["api"]}",
                        params=to_run["parameters"] or {},
                    ),
                    run_options=CDPRunOptions(
                        cdp_address=cdp_address,
                    )
                    if cdp_address is not None
                    else StandaloneRunOptions(
                        headless=headless,
                    ),
                    auth=auth,
                ),
            )

            result_to_print = result.result
            if result_to_print is None:
                result_to_print = italic("None")
            elif result_to_print == "":
                result_to_print = italic("Empty string")
            else:
                result_to_print = bold(str(json.dumps(result_to_print, indent=2)))
            print(f"{bold("📦 Result: ")}{green(result_to_print)}")
            extended_payloads = [
                {"api": p.api_name, "parameters": p.parameters} for p in (result.payload_to_append or [])
            ]
            extended_payload_name_counter = Counter([p["api"] for p in extended_payloads])
            if sum(extended_payload_name_counter.values()) > 0:
                print(
                    bold("➕ Extended payloads:"),
                    ", ".join([f"{cyan(k)}: {v}" for k, v in extended_payload_name_counter.items()]),
                )
            _run_output: _RunOutput = {
                "success": True,
                "result": result.result,
                "extended_payloads": extended_payloads,
            }

        except RunApiError as e:
            print("❗️", yellow(e))
            _run_output: _RunOutput = {
                "success": False,
                "error": traceback.format_exc().split("\n"),
            }
        return {
            "input": run_input,
            "output": _run_output,
        }

    except Exception:
        traceback.print_exc()
        raise
    finally:
        sys.path.remove(os.path.join(os.getcwd()))


async def extend_timeout():
    print(green(italic("⏱️ Extending timeout")))
