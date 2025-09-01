from dataclasses import dataclass
from typing import Any
from typing import Generator
from unittest.mock import AsyncMock
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from runtime.types.run_types import PayloadToAppend
from runtime.types.run_types import StorageState


def get_mock_console():
    """Create a mock console that tracks calls."""
    mock_console = Mock()
    mock_console.print = Mock()
    return mock_console


class AsyncContextManagerMock:
    def __init__(self):
        self.aenter_called = False
        self.aexit_called = False
        self.exception_info = None

    async def __aenter__(self):
        self.aenter_called = True
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        self.aexit_called = True
        self.exception_info = (exc_type, exc_val, exc_tb)
        # Return False/None to propagate exceptions
        return False


@dataclass
class SharedMocks:
    console: Mock
    assert_api_file_exists: AsyncMock
    register_get_auth_session_parameters: AsyncMock


@pytest.fixture(autouse=True)
def shared_mocks() -> Generator[SharedMocks, Any, None]:
    """Mock dependencies for API controller tests."""
    _mock_console_patch = patch("intuned_cli.controller.api.console", get_mock_console())
    _mock_assert_api_patch = patch("intuned_cli.controller.api.assert_api_file_exists", new_callable=AsyncMock)
    _mock_register_auth_patch = patch("intuned_cli.controller.api.register_get_auth_session_parameters")

    with (
        _mock_console_patch,
        _mock_assert_api_patch as mock_assert_api,
        _mock_register_auth_patch as mock_register_auth,
    ):
        # Setup default return values
        mock_assert_api.return_value = None
        mock_register_auth.return_value = None

        yield SharedMocks(
            console=get_mock_console(),
            assert_api_file_exists=mock_assert_api,
            register_get_auth_session_parameters=mock_register_auth,
        )


@dataclass
class AttemptApiMocks:
    extendable_timeout: AsyncMock
    run_api: AsyncMock


@pytest.fixture
def attempt_api_mocks() -> Generator[AttemptApiMocks, Any, None]:
    """Mock dependencies for attempt_api tests."""
    _mock_timeout_patch = patch("intuned_cli.controller.api.extendable_timeout")
    _mock_run_api_patch = patch("intuned_cli.controller.api.run_api", new_callable=AsyncMock)

    with (
        _mock_timeout_patch as mock_timeout,
        _mock_run_api_patch as mock_run_api,
    ):
        # Setup default return values
        mock_timeout.return_value = AsyncContextManagerMock()

        # Mock run_api to return success by default
        mock_result = Mock()
        mock_result.result = "test_result"
        mock_result.payload_to_append = []
        mock_run_api.return_value = mock_result

        yield AttemptApiMocks(
            extendable_timeout=mock_timeout,
            run_api=mock_run_api,
        )


@dataclass
class ExecuteCLIMocks:
    attempt_api: AsyncMock
    execute_run_validate_auth_session_cli: AsyncMock
    write_results_to_file: AsyncMock


@pytest.fixture
def execute_cli_mocks() -> Generator[ExecuteCLIMocks, Any, None]:
    """Mock dependencies for execute_*_cli tests."""
    _mock_validate_auth_patch = patch(
        "intuned_cli.controller.api.execute_run_validate_auth_session_cli", new_callable=AsyncMock
    )
    _mock_run_api_patch = patch("intuned_cli.controller.api.attempt_api", new_callable=AsyncMock)
    _mock_write_results_to_file_patch = patch(
        "intuned_cli.controller.api.write_results_to_file", new_callable=AsyncMock
    )

    with (
        _mock_validate_auth_patch as mock_validate_auth,
        _mock_run_api_patch as mock_attempt_api,
        _mock_write_results_to_file_patch as mock_write_results_to_file,
    ):
        # Setup default return values
        mock_validate_auth.return_value = {"cookies": [], "storageState": {}}

        # Mock run_api to return success by default
        mock_attempt_api.return_value = ("test_result", [])

        yield ExecuteCLIMocks(
            execute_run_validate_auth_session_cli=mock_validate_auth,
            attempt_api=mock_attempt_api,
            write_results_to_file=mock_write_results_to_file,
        )


class TestAttemptApi:
    """Test suite for attempt_api function."""

    @pytest.mark.asyncio
    async def test_attempt_api_calls_timeout_middleware_with_timeout(self, attempt_api_mocks: AttemptApiMocks):
        """Test that attempt_api calls timeout middleware with the correct timeout."""
        # Import inside test to avoid circular import issues
        from intuned_cli.controller.api import attempt_api

        await attempt_api(
            api_name="testApi",
            parameters={},
            headless=False,
            timeout=6000,
        )

        attempt_api_mocks.extendable_timeout.assert_called_once_with(6000)

    @pytest.mark.asyncio
    async def test_attempt_api_calls_run_api_with_correct_parameters_and_parses_proxy(
        self, attempt_api_mocks: AttemptApiMocks
    ):
        """Test that attempt_api calls run_api with correct parameters and parses proxy."""
        from intuned_cli.controller.api import attempt_api
        from runtime.types.run_types import ProxyConfig

        with patch("intuned_cli.controller.api.ProxyConfig.parse_from_str") as mock_parse_proxy:
            proxy_config = ProxyConfig(
                username="user",
                password="pass",
                server="proxy-server",
            )
            mock_parse_proxy.return_value = proxy_config

            parameters: dict[Any, Any] = {}
            auth = StorageState(cookies=[], origins=[], session_storage=[])
            await attempt_api(
                api_name="testApi",
                parameters=parameters,
                headless=False,
                auth=auth,
                proxy="proxy",
                timeout=999999999,
            )

            # mock_parse_proxy.assert_called_once_with("proxy")
            attempt_api_mocks.run_api.assert_called_once()

            # Verify the call arguments
            call_args = attempt_api_mocks.run_api.call_args[0][0]
            assert call_args.automation_function.name == "api/testApi"
            assert call_args.automation_function.params is parameters
            assert call_args.run_options.headless is False
            assert call_args.run_options.proxy == proxy_config
            assert call_args.auth.session.state is auth
            assert call_args.auth.run_check is False

    @pytest.mark.asyncio
    async def test_attempt_api_returns_result_and_extended_payloads_if_run_api_succeeds(
        self, attempt_api_mocks: AttemptApiMocks
    ):
        """Test that attempt_api returns the result and extended payloads when run_api succeeds."""
        from intuned_cli.controller.api import attempt_api

        expected_result = {}
        expected_payload_to_append = []

        mock_result = Mock()
        mock_result.result = expected_result
        mock_result.payload_to_append = expected_payload_to_append
        attempt_api_mocks.run_api.return_value = mock_result

        result, payloads = await attempt_api(
            api_name="testApi",
            parameters="inputData",
            headless=False,
            timeout=999999999,
        )

        assert result is expected_result
        assert payloads is expected_payload_to_append

    @pytest.mark.asyncio
    async def test_attempt_api_throws_error_when_run_api_fails_with_error(self, attempt_api_mocks: AttemptApiMocks):
        """Test that attempt_api throws the error when run_api fails."""
        from intuned_cli.controller.api import attempt_api

        error = Exception("runApi failed")
        attempt_api_mocks.run_api.side_effect = error

        with pytest.raises(Exception, match="runApi failed"):
            await attempt_api(
                api_name="testApi",
                parameters={},
                headless=False,
                timeout=999999999,
            )


class TestExecuteRunApiCli:
    """Test suite for API controller functions."""

    @pytest.mark.asyncio
    async def test_execute_run_api_cli_calls_attempt_api_once_if_success(self, execute_cli_mocks: ExecuteCLIMocks):
        """Test that execute_run_api_cli calls attemptApi once if successful."""
        from intuned_cli.controller.api import execute_run_api_cli

        await execute_run_api_cli(
            api_name="testApi",
            input_data={},
            retries=3,
            headless=False,
            timeout=30,
        )

        execute_cli_mocks.attempt_api.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_run_api_cli_stops_retrying_after_max_retries(self, execute_cli_mocks: ExecuteCLIMocks):
        """Test that execute_run_api_cli stops retrying after max retries."""
        from intuned_cli.controller.api import execute_run_api_cli
        from intuned_cli.utils.error import CLIError
        from runtime.errors.run_api_errors import AutomationError

        execute_cli_mocks.attempt_api.side_effect = AutomationError(Exception("runApi failed"))

        with pytest.raises(CLIError):
            await execute_run_api_cli(
                api_name="testApi",
                input_data={},
                retries=10,
                headless=False,
                timeout=30,
            )

        assert execute_cli_mocks.attempt_api.call_count == 10

    @pytest.mark.asyncio
    async def test_execute_run_api_cli_stops_retrying_on_non_automation_errors(
        self, execute_cli_mocks: ExecuteCLIMocks
    ):
        """Test that execute_run_api_cli stops retrying on non-automation errors."""
        from intuned_cli.controller.api import execute_run_api_cli

        execute_cli_mocks.attempt_api.side_effect = Exception("runApi failed")

        with pytest.raises(Exception, match="runApi failed"):
            await execute_run_api_cli(
                api_name="testApi",
                input_data={},
                retries=3,
                headless=False,
                timeout=30,
            )

        execute_cli_mocks.attempt_api.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_run_api_cli_stops_retrying_on_success(self, execute_cli_mocks: ExecuteCLIMocks):
        """Test that execute_run_api_cli stops retrying on success."""
        from intuned_cli.controller.api import execute_run_api_cli
        from runtime.errors.run_api_errors import AutomationError

        execute_cli_mocks.attempt_api.side_effect = [
            AutomationError(Exception("runApi failed")),
            ("success", []),
        ]

        await execute_run_api_cli(
            api_name="testApi",
            input_data={},
            retries=10,
            headless=False,
            timeout=30,
        )

        assert execute_cli_mocks.attempt_api.call_count == 2

    @pytest.mark.asyncio
    async def test_execute_run_api_cli_validates_auth_session_before_each_attempt_if_provided(
        self, execute_cli_mocks: ExecuteCLIMocks
    ):
        """Test that execute_run_api_cli validates auth session before each attempt if provided."""
        with patch(
            "intuned_cli.controller.api.execute_run_validate_auth_session_cli", new_callable=AsyncMock
        ) as mock_validate_auth:
            from intuned_cli.controller.api import AuthSessionInput
            from intuned_cli.controller.api import execute_run_api_cli
            from runtime.errors.run_api_errors import AutomationError

            execute_cli_mocks.attempt_api.side_effect = [
                AutomationError(Exception("runApi failed")),
                ("success", []),
            ]

            auth_session = AuthSessionInput(
                id="authSessionId",
                auto_recreate=False,
                check_retries=1,
                create_retries=2,
            )

            await execute_run_api_cli(
                api_name="testApi",
                input_data={},
                auth_session=auth_session,
                retries=10,
                headless=False,
                timeout=30,
            )

            assert mock_validate_auth.call_count == 2
            # Verify the call arguments
            call_args = mock_validate_auth.call_args
            assert call_args[1]["id"] == "authSessionId"
            assert call_args[1]["auto_recreate"] is False
            assert call_args[1]["check_retries"] == 1
            assert call_args[1]["create_retries"] == 2

    @pytest.mark.asyncio
    async def test_execute_run_api_cli_doesnt_validate_auth_session_if_not_provided(
        self, execute_cli_mocks: ExecuteCLIMocks
    ):
        """Test that execute_run_api_cli doesn't validate auth session if not provided."""
        from intuned_cli.controller.api import execute_run_api_cli

        await execute_run_api_cli(
            api_name="testApi",
            input_data={},
            retries=1,
            headless=False,
            timeout=30,
        )

        execute_cli_mocks.execute_run_validate_auth_session_cli.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_run_api_cli_fails_if_auth_session_is_provided_but_not_valid(
        self, execute_cli_mocks: ExecuteCLIMocks
    ):
        """Test that execute_run_api_cli fails if auth session is provided but not valid."""
        from intuned_cli.controller.api import AuthSessionInput
        from intuned_cli.controller.api import execute_run_api_cli
        from intuned_cli.utils.error import CLIError

        execute_cli_mocks.execute_run_validate_auth_session_cli.side_effect = CLIError("Auth session validation failed")

        auth_session = AuthSessionInput(
            id="authSessionId",
            auto_recreate=False,
            check_retries=1,
            create_retries=2,
        )

        with pytest.raises(CLIError, match="Auth session validation failed"):
            await execute_run_api_cli(
                api_name="testApi",
                input_data={},
                auth_session=auth_session,
                retries=10,
                headless=False,
                timeout=30,
            )

        # Verify auth validation was called
        call_args = execute_cli_mocks.execute_run_validate_auth_session_cli.call_args
        assert call_args[1]["id"] == "authSessionId"
        assert call_args[1]["auto_recreate"] is False
        assert call_args[1]["check_retries"] == 1
        assert call_args[1]["create_retries"] == 2

        execute_cli_mocks.attempt_api.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_run_api_cli_writes_result_to_file_if_output_file_is_provided(
        self, shared_mocks: SharedMocks, execute_cli_mocks: ExecuteCLIMocks
    ):
        """Test that execute_run_api_cli writes result to file if outputFile is provided."""

        from intuned_cli.controller.api import execute_run_api_cli
        from runtime.types.run_types import PayloadToAppend

        execute_cli_mocks.attempt_api.return_value = (
            "test_result",
            [PayloadToAppend(api_name="test_api", parameters={"key": "value"})],
        )

        await execute_run_api_cli(
            api_name="testApi",
            input_data={},
            output_file="output.json",
            retries=1,
            headless=False,
            timeout=30,
        )

        execute_cli_mocks.write_results_to_file.assert_called_once()
        call_args = execute_cli_mocks.write_results_to_file.call_args.kwargs
        assert str(call_args["file_path"]) == "output.json"
        assert call_args["result"] == "test_result"
        assert call_args["extended_payloads"] == [PayloadToAppend(api_name="test_api", parameters={"key": "value"})]

    @pytest.mark.asyncio
    async def test_execute_run_api_cli_asserts_api_file_exists(
        self, shared_mocks: SharedMocks, execute_cli_mocks: ExecuteCLIMocks
    ):
        """Test that execute_run_api_cli asserts API file exists."""
        from intuned_cli.controller.api import execute_run_api_cli

        await execute_run_api_cli(
            api_name="testApi",
            input_data={},
            retries=1,
            headless=False,
            timeout=30,
        )

        shared_mocks.assert_api_file_exists.assert_called_once_with("api", "testApi")


class TestExecuteAttemptApiCli:
    """Test suite for execute_attempt_api_cli function."""

    @pytest.mark.asyncio
    async def test_execute_attempt_api_cli_calls_attempt_api_once(self, execute_cli_mocks: ExecuteCLIMocks):
        """Test that executeAttemptApiCLI calls attemptApi once."""
        from intuned_cli.controller.api import execute_attempt_api_cli
        from runtime.errors.run_api_errors import AutomationError

        await execute_attempt_api_cli(
            api_name="testApi",
            input_data={},
            headless=False,
            timeout=30,
        )

        execute_cli_mocks.attempt_api.assert_called_once()

        # Test that it throws AutomationError when run_api fails
        execute_cli_mocks.attempt_api.reset_mock()
        execute_cli_mocks.attempt_api.side_effect = AutomationError(Exception("runApi failed"))

        with pytest.raises(AutomationError):
            await execute_attempt_api_cli(
                api_name="testApi",
                input_data={},
                headless=False,
                timeout=30,
            )

        execute_cli_mocks.attempt_api.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_attempt_api_cli_writes_result_to_file_if_output_file_is_provided(
        self, shared_mocks: SharedMocks, execute_cli_mocks: ExecuteCLIMocks
    ):
        """Test that executeAttemptApiCLI writes result to file if outputFile is provided."""

        from intuned_cli.controller.api import execute_attempt_api_cli

        execute_cli_mocks.attempt_api.return_value = (
            "test_result",
            [PayloadToAppend(api_name="test_api", parameters={"key": "value"})],
        )

        await execute_attempt_api_cli(
            api_name="testApi",
            input_data={},
            output_file="output.json",
            headless=False,
            timeout=30,
        )

        # Verify file was written
        execute_cli_mocks.write_results_to_file.assert_called_once()
        call_args = execute_cli_mocks.write_results_to_file.call_args.kwargs
        assert str(call_args["file_path"]) == "output.json"
        assert call_args["result"] == "test_result"
        assert call_args["extended_payloads"] == [PayloadToAppend(api_name="test_api", parameters={"key": "value"})]

    @pytest.mark.asyncio
    async def test_execute_attempt_api_cli_asserts_api_file_exists(
        self, shared_mocks: SharedMocks, execute_cli_mocks: ExecuteCLIMocks
    ):
        """Test that executeAttemptApiCLI asserts API file exists."""
        from intuned_cli.controller.api import execute_attempt_api_cli

        await execute_attempt_api_cli(
            api_name="testApi",
            input_data={},
            headless=False,
            timeout=30,
        )

        shared_mocks.assert_api_file_exists.assert_called_once_with("api", "testApi")
