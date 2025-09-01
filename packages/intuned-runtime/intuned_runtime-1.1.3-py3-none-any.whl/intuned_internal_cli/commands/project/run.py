import asyncio
import functools
import json
import os
import sys
from collections import Counter
from datetime import datetime
from enum import StrEnum
from importlib import import_module
from typing import Any
from typing import cast

import arguably
from dotenv import find_dotenv
from dotenv import load_dotenv
from more_termcolor import bold  # type: ignore
from more_termcolor import cyan  # type: ignore
from more_termcolor import green  # type: ignore
from more_termcolor import italic  # type: ignore
from more_termcolor import on_blue  # type: ignore
from more_termcolor import underline  # type: ignore
from more_termcolor import yellow  # type: ignore

from runtime.run.intuned_settings import load_intuned_settings
from runtime.types import Payload
from runtime.types.run_types import Auth
from runtime.types.run_types import StateSession
from runtime.types.run_types import StorageState

from ...utils.run_apis import run_api_for_cli
from ...utils.run_apis import RunResultData


class Mode(StrEnum):
    full = "full"
    single = "single"
    sample = "sample"
    ide = "ide"


@arguably.command  # type: ignore
async def project__run(
    *,
    api_name: str = "default",
    mode: Mode = Mode.sample,
    params: str | None = None,
    params_path: str | None = None,
    sample_config_str: str | None = None,
    concurrent: int = 1,
    no_headless: bool | None = False,
    cdp_address: str | None = None,
    output_file_id: str | None = None,
    auth_session_path: str | None = None,
    auth_session_parameters: str | None = None,
):
    """
    Runs the current project. Project must contain an "api" directory with API functions.

    Args:
        api_name (str): The name of the API to run.
        mode (Mode): The mode in which to run the app.
            Defaults to "sample".
            Sample will run a sample of the extended payloads.
            Full will also run all extended payloads.
            Single will only run the specified API.
            IDE will only run the specified API with changes to the outputs and files to fit running in the IDE.
        params (str | None): Parameters to pass to the API as a JSON string.
        params_path (str | None): Path to a JSON file containing parameters to pass to the API.
        sample_config_str (str | None): [--sample-config] A JSON string where keys are API names and values are the number of times to run the API in sample mode.
        no_headless (bool): Disable headless mode.
        concurrent (int | None): [-c/--concurrent] Number of concurrent runs to allow.
        cdp_address (str | None): Chrome DevTools Protocol address to connect to.
        output_file_id (str | None): (IDE mode only) The output file id to save the result in
        auth_session_path (str | None): Path to the auth session file.
        auth_session_parameters (str | None): JSON string containing auth session parameters.
    Returns:
        None

    """

    if sample_config_str and mode != Mode.sample:
        raise ValueError("Cannot provide sample_config in non-sample mode")
    if params and params_path:
        raise ValueError("Cannot provide both params and params_path")
    if params_path and not os.path.exists(params_path):
        raise ValueError(f"params_path does not exist: {params_path}")

    try:
        if params:
            params_json = json.loads(params) if params else None
        elif params_path:
            with open(params_path) as f:
                params_json = json.load(f)
        else:
            params_json = None
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in params: {e}") from e
    except FileNotFoundError as e:
        raise ValueError(f"Invalid params_path: {e}") from e

    auth_session: StorageState | None = None
    try:
        if auth_session_path:
            with open(auth_session_path) as f:
                auth_session = StorageState(**json.load(f))
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in auth session: {e}") from e
    except FileNotFoundError as e:
        raise ValueError(f"Invalid auth-session-path: {e}") from e

    if concurrent <= 0:
        raise ValueError("Concurrent must be greater than 0")

    dotenv = find_dotenv(usecwd=True)
    if dotenv:
        load_dotenv(dotenv, override=True)

    headless = not no_headless

    api_to_run: Payload = {
        "api": api_name,
        "parameters": params_json or {},
    }

    timestamp: str = datetime.now().strftime("%Y-%m-%d_%H:%M")
    run_results_dir = os.path.join("run_results", f"run_{mode}_{timestamp}")
    n = 1
    while os.path.exists(run_results_dir):
        run_results_dir = os.path.join("run_results", f"run_{mode}_{timestamp}_{n}")
        n += 1
    os.makedirs(run_results_dir, exist_ok=True)

    sys.path.append(os.path.join(os.getcwd()))

    if auth_session_parameters:
        try:
            auth_session_parameters_json = json.loads(auth_session_parameters)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in auth session parameters: {e}") from e
    else:
        auth_session_parameters_json = None

    if mode == Mode.ide:
        await run_api_for_ide_mode(
            api_name=api_name,
            params=params_json,
            headless=headless,
            cdp_address=cdp_address,
            output_file_id=output_file_id,
            session=auth_session,
            auth_session_parameters=auth_session_parameters_json,
        )
        return

    settings = await load_intuned_settings()
    if auth_session is None and settings.auth_sessions.enabled:
        raise ValueError("Auth session is required when auth sessions are enabled")

    run_payloads_and_extend_with_configs = functools.partial(
        _run_payloads_and_extend,
        payload=api_to_run,
        headless=headless,
        concurrent=concurrent,
        cdp_address=cdp_address,
        session=auth_session,
        auth_session_parameters=auth_session_parameters_json,
    )

    if mode == Mode.single:
        print(bold("Running in single mode"))
        api_runs = run_payloads_and_extend_with_configs(extend_config={api_name: 1})
    elif mode == Mode.full:
        print(bold("Running in full mode"))
        api_runs = run_payloads_and_extend_with_configs(concurrent=concurrent)
    elif mode == Mode.sample:
        sample_config: dict[str, int] = (
            json.loads(sample_config_str)
            if sample_config_str
            else {
                "default": 1,
                "list": 3,
                "details": 15,
            }
        )
        print(
            bold("Running in sample mode with config:"),
            ", ".join([f"{cyan(k)}: {v}" for k, v in sample_config.items()]),
        )
        api_runs = run_payloads_and_extend_with_configs(extend_config=sample_config)

    print(italic(f"Results will be saved in {cyan(os.path.abspath(run_results_dir))}"))

    _check_intuned_sdk()

    iteration = 1
    async for result_data in api_runs:
        prefix = f"{iteration}_" if mode != Mode.single else ""
        success = result_data["output"]["success"]
        run_api_name = result_data["input"]["api"]
        with open(
            os.path.join(run_results_dir, f"{prefix}{run_api_name}_{"success" if success else "fail"}.json"), "w"
        ) as f:
            json.dump(result_data, f, indent=2)
        iteration += 1

    print(green(bold("🏁 Done")))
    print(italic(f"Results saved in {cyan(os.path.abspath(run_results_dir))}"), flush=True)


def _check_intuned_sdk():
    try:
        import_module("intuned_sdk")
    except:
        print(yellow(f"Warning: {bold('intuned_sdk')} could not be imported!"))


async def _run_payloads_and_extend(
    payload: Payload,
    headless: bool,
    extend_config: dict[str, int] | None = None,
    concurrent: int = 1,
    cdp_address: str | None = None,
    session: StorageState | None = None,
    auth_session_parameters: dict[str, Any] | None = None,
):
    counter = Counter(extend_config)
    payloads_lists = [[payload]]

    tasks: set[asyncio.Task[RunResultData]] = set()

    while len(payloads_lists) > 0 or len(tasks) > 0:
        if len(payloads_lists) == 0 or len(tasks) >= concurrent:
            done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                result_data = task.result()

                payloads_lists.append(result_data["output"].get("extended_payloads", []))
                yield task.result()
        payloads = payloads_lists.pop(0)
        if len(payloads) == 0:
            continue
        payload_to_run = payloads.pop(0)
        print(payload_to_run)
        payloads_lists.append(payloads)
        if extend_config:
            if counter[payload_to_run["api"]] <= 0:
                if payload_to_run["api"] in extend_config:
                    print(
                        italic(
                            f"Skipping {green(payload_to_run['api'])} " f"(> {extend_config[payload_to_run['api']]})"
                        )
                    )
                continue
            counter[payload_to_run["api"]] -= 1
        task = asyncio.create_task(
            run_api_for_cli(
                payload_to_run,
                headless=headless,
                cdp_address=cdp_address,
                auth=Auth(
                    run_check=True,
                    session=StateSession(state=session),
                )
                if session is not None
                else None,
                auth_session_parameters=auth_session_parameters,
            )
        )
        tasks.add(task)


async def run_api_for_ide_mode(
    *,
    api_name: str,
    params: Any,
    headless: bool,
    cdp_address: str | None,
    output_file_id: str | None,
    session: StorageState | None = None,
    auth_session_parameters: dict[str, Any] | None = None,
):
    print(bold(f"Running {green(api_name)}"))
    result_data = await run_api_for_cli(
        {
            "api": api_name,
            "parameters": params,
        },
        headless=headless,
        cdp_address=cdp_address,
        print_output=False,
        auth=Auth(
            session=StateSession(
                state=session,
            ),
            run_check=False,
        )
        if session is not None
        else None,
        auth_session_parameters=auth_session_parameters,
    )

    if not result_data["output"]["success"]:
        error = cast(list[str], result_data["output"].get("error", []))
        print("\n".join(error[1:]))
        sys.exit(1)

    result = result_data["output"].get("result")

    is_response_json = isinstance(result, dict)
    if is_response_json:
        result = cast(dict[Any, Any], result)
        has_more_than_5_keys = len(result) > 5
        has_nested_json = any(isinstance(v, dict) for v in result.values())
        should_write_to_file = has_more_than_5_keys or has_nested_json
    elif isinstance(result, list):
        should_write_to_file = True
    else:
        should_write_to_file = False

    results_dir = "/tmp/run-results"
    if should_write_to_file and output_file_id is not None:
        print(underline(on_blue(f"Click to Open: Results saved (Run: {output_file_id})")))

        os.makedirs(results_dir, exist_ok=True)
        with open(os.path.join(results_dir, f"{output_file_id}.json"), "w") as f:
            json.dump(result_data, f, indent=2)
    else:
        print(bold("📦 Result:"), green(json.dumps(result) if isinstance(result, (dict, list)) else str(result)))

    extended_payloads = result_data["output"].get("extended_payloads", [])
    has_payloads_to_append = len(extended_payloads) > 0

    if has_payloads_to_append and output_file_id is not None:
        os.makedirs(results_dir, exist_ok=True)
        print(underline(on_blue(f"Click to Open: payloads to append (Run: {output_file_id})")))
        with open(os.path.join(results_dir, f"{output_file_id}-payloads-to-append.json"), "w") as f:
            json.dump(extended_payloads, f, indent=2)
    elif has_payloads_to_append:
        print(bold("➕ Extended payloads:"), green(str(extended_payloads)))
        print("This will only take effect if you run within a job or queue.")
