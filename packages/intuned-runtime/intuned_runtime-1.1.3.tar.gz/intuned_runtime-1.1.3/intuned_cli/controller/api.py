import json
import os
from typing import Any

from anyio import Path
from pydantic import BaseModel

from intuned_cli.controller.authsession import execute_run_validate_auth_session_cli
from intuned_cli.controller.authsession import load_auth_session_instance
from intuned_cli.utils.api_helpers import assert_api_file_exists
from intuned_cli.utils.console import console
from intuned_cli.utils.error import CLIError
from intuned_cli.utils.error import log_automation_error
from intuned_cli.utils.get_auth_parameters import register_get_auth_session_parameters
from intuned_cli.utils.timeout import extendable_timeout
from runtime.errors.run_api_errors import AutomationError
from runtime.run.run_api import import_function_from_api_dir
from runtime.run.run_api import run_api
from runtime.types.run_types import Auth
from runtime.types.run_types import AutomationFunction
from runtime.types.run_types import PayloadToAppend
from runtime.types.run_types import ProxyConfig
from runtime.types.run_types import RunApiParameters
from runtime.types.run_types import StandaloneRunOptions
from runtime.types.run_types import StateSession
from runtime.types.run_types import StorageState


class AuthSessionInput(BaseModel):
    id: str
    auto_recreate: bool
    check_retries: int
    create_retries: int


async def execute_run_api_cli(
    *,
    api_name: str,
    input_data: Any | None,
    retries: int,
    auth_session: AuthSessionInput | None = None,
    output_file: str | None = None,
    headless: bool,
    timeout: float,
    proxy: str | None = None,
):
    """
    Execute API with retries and optional auth session validation.
    """
    await assert_api_file_exists("api", api_name)

    register_get_auth_session_parameters(auth_session.id if auth_session else None)

    console.print(f"[bold]Running API [cyan]{api_name}[/cyan][/bold]")

    for i in range(retries):
        console.print(f"\n[bold]Executing [cyan]{api_name}[/cyan] [italic](Attempt {i + 1})[/italic]...\n")

        auth_session_instance: StorageState | None = None
        if auth_session:
            auth_session_instance = await execute_run_validate_auth_session_cli(
                id=auth_session.id,
                auto_recreate=auth_session.auto_recreate,
                check_retries=auth_session.check_retries,
                create_retries=auth_session.create_retries,
                headless=headless,
                timeout=timeout,
                proxy=proxy,
            )

        try:
            result, extended_payloads = await attempt_api(
                api_name=api_name,
                parameters=input_data,
                auth=auth_session_instance,
                headless=headless,
                timeout=timeout,
                proxy=proxy,
            )

            return await handle_api_result(
                result=result,
                extended_payloads=extended_payloads,
                file_path=Path(output_file) if output_file else None,
            )

        except AutomationError as error:
            log_automation_error(error)
            console.print(f"[bold red]Attempt {i + 1} failed[/bold red]")
            continue

    raise CLIError(
        f"[red][bold]Failed to run API [/bold][bold]{api_name}[/bold]: [bright_red]Exceeded maximum retries of [bold]{retries}[/bold][/bright_red][/red]",
        auto_color=False,
    )


async def execute_attempt_api_cli(
    *,
    api_name: str,
    input_data: Any | None,
    auth_session_id: str | None = None,
    output_file: str | None = None,
    headless: bool,
    timeout: float,
    proxy: str | None = None,
):
    """
    Execute a single API attempt with optional auth session.
    """
    console.print(f"[bold]Execute API attempt for [cyan]{api_name}[/cyan][/bold]")

    await assert_api_file_exists("api", api_name)

    register_get_auth_session_parameters(auth_session_id)

    auth_session_instance: StorageState | None = None
    if auth_session_id:
        auth_session_instance, _ = await load_auth_session_instance(auth_session_id)

    result, extended_payloads = await attempt_api(
        api_name=api_name,
        parameters=input_data,
        auth=auth_session_instance,
        headless=headless,
        timeout=timeout,
        proxy=proxy,
    )

    return await handle_api_result(
        result=result,
        extended_payloads=extended_payloads,
        file_path=Path(output_file) if output_file else None,
    )


async def handle_api_result(
    *,
    result: Any,
    extended_payloads: list[PayloadToAppend] | None = None,
    file_path: Path | None = None,
):
    console.print("[bold][green]API executed successfully[/green][/bold]")

    if not file_path:
        if result is None:
            console.print("[bold][yellow]No result returned from the API[/yellow][/bold]")
        else:
            console.print("[bold][green]Result:[/green][/bold]")
            console.print(f"{json.dumps(result, indent=2)}")

        if extended_payloads and len(extended_payloads) > 0:
            console.print(
                "[bold green]Extended payloads:[/bold green] [italic][bright_green](This will only take effect if this API run was part of a job.)[/bright_green][/italic]"
            )
            console.print(f"{json.dumps([p.model_dump(by_alias=True) for p in extended_payloads], indent=2)}")

        return

    await write_results_to_file(
        file_path=file_path,
        result=result,
        extended_payloads=extended_payloads,
    )


async def write_results_to_file(
    *,
    file_path: Path,
    result: Any,
    extended_payloads: list[PayloadToAppend] | None = None,
):
    output_json = {"result": result}
    if extended_payloads:
        output_json["extendedPayloads"] = [m.model_dump(by_alias=True) for m in extended_payloads]

    try:
        await file_path.write_text(json.dumps(output_json, indent=2), encoding="utf-8")
        console.print(f"[bold green]Results written to[/bold green] [underline]{file_path}[/underline]")
    except Exception as e:
        raise CLIError(f"Failed to write results to file '{file_path}': {e}") from e


async def attempt_api(
    *,
    api_name: str,
    parameters: Any | None,
    auth: StorageState | None = None,
    headless: bool,
    timeout: float,
    proxy: str | None = None,
):
    cwd = await Path().resolve()
    async with extendable_timeout(timeout):
        result = await run_api(
            RunApiParameters(
                automation_function=AutomationFunction(name=f"api/{api_name}", params=parameters),
                auth=Auth(
                    session=StateSession(state=auth),
                    run_check=False,
                )
                if auth
                else None,
                run_options=StandaloneRunOptions(
                    headless=headless, proxy=ProxyConfig.parse_from_str(proxy) if proxy else None
                ),
            ),
            import_function=lambda file_path, name=None: import_function_from_api_dir(
                file_path=file_path, automation_function_name=name, base_dir=os.fspath(cwd)
            ),
        )
    return result.result, result.payload_to_append
