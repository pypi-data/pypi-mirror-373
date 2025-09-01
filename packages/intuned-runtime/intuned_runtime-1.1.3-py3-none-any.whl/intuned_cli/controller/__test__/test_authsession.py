from dataclasses import dataclass
from typing import Any
from typing import Generator
from unittest.mock import AsyncMock
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from intuned_cli.controller.authsession import execute_attempt_check_auth_session_cli
from intuned_cli.controller.authsession import execute_attempt_create_auth_session_cli
from intuned_cli.controller.authsession import execute_run_create_auth_session_cli
from intuned_cli.controller.authsession import execute_run_update_auth_session_cli
from intuned_cli.controller.authsession import execute_run_validate_auth_session_cli
from intuned_cli.controller.authsession import run_check
from intuned_cli.controller.authsession import run_check_with_retries
from intuned_cli.controller.authsession import run_create
from intuned_cli.controller.authsession import run_create_with_retries
from intuned_cli.utils.error import CLIError
from runtime.errors.run_api_errors import AutomationError
from runtime.types.run_types import ProxyConfig
from runtime.types.run_types import StorageState

from .test_api import AsyncContextManagerMock


def get_mock_console():
    """Create a mock console that tracks calls."""
    mock_console = Mock()
    mock_console.print = Mock()
    return mock_console


def _get_empty_auth_session():
    return StorageState(cookies=[], origins=[], session_storage=[])


# Test data helpers
def _check_passed_result():
    mock_result = Mock()
    mock_result.result = True
    return mock_result


def _check_failed_result():
    mock_result = Mock()
    mock_result.result = False
    return mock_result


def _create_success_result(session_data: Any):
    mock_result = Mock()
    mock_result.session = session_data
    return mock_result


@dataclass
class SharedMocks:
    console: Mock
    assert_api_file_exists: AsyncMock
    register_get_auth_session_parameters: AsyncMock


@pytest.fixture(autouse=True)
def shared_mocks() -> Generator[SharedMocks, Any, None]:
    """Mock dependencies for API controller tests."""
    _mock_console_patch = patch("intuned_cli.controller.authsession.console", get_mock_console())
    _mock_assert_api_patch = patch("intuned_cli.controller.authsession.assert_api_file_exists", new_callable=AsyncMock)
    _mock_register_auth_patch = patch("intuned_cli.controller.authsession.register_get_auth_session_parameters")

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
    _mock_timeout_patch = patch("intuned_cli.controller.authsession.extendable_timeout")
    _mock_run_api_patch = patch("intuned_cli.controller.authsession.run_api", new_callable=AsyncMock)

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
class WithRetriesMocks:
    run_check: AsyncMock
    run_create: AsyncMock
    store_auth_session_instance: AsyncMock


@pytest.fixture
def with_retries_mocks() -> Generator[WithRetriesMocks, Any, None]:
    """Mock dependencies for with_retries tests."""
    _mock_run_check_patch = patch("intuned_cli.controller.authsession.run_check", new_callable=AsyncMock)
    _mock_run_create_patch = patch("intuned_cli.controller.authsession.run_create", new_callable=AsyncMock)
    _mock_store_auth_session_instance_patch = patch(
        "intuned_cli.controller.authsession.store_auth_session_instance", new_callable=AsyncMock
    )

    with (
        _mock_run_check_patch as mock_run_check,
        _mock_run_create_patch as mock_run_create,
        _mock_store_auth_session_instance_patch as mock_store_auth_session_instance,
    ):
        # Setup default return values
        mock_run_check.return_value = True
        mock_run_create.return_value = "test_result"

        yield WithRetriesMocks(
            run_check=mock_run_check,
            run_create=mock_run_create,
            store_auth_session_instance=mock_store_auth_session_instance,
        )


@dataclass
class ExecuteCLIMocks:
    run_create_with_retries: AsyncMock
    run_check_with_retries: AsyncMock
    load_auth_session_instance: AsyncMock


@pytest.fixture
def execute_cli_mocks() -> Generator[ExecuteCLIMocks, Any, None]:
    """Mock dependencies for execute_*_cli tests."""
    _mock_run_create_with_retries_patch = patch(
        "intuned_cli.controller.authsession.run_create_with_retries", new_callable=AsyncMock
    )
    _mock_run_check_with_retries_patch = patch(
        "intuned_cli.controller.authsession.run_check_with_retries", new_callable=AsyncMock
    )
    _mock_load_auth_session_instance_patch = patch(
        "intuned_cli.controller.authsession.load_auth_session_instance", new_callable=AsyncMock
    )

    with (
        _mock_run_create_with_retries_patch as mock_run_create_with_retries,
        _mock_run_check_with_retries_patch as mock_run_check_with_retries,
        _mock_load_auth_session_instance_patch as mock_load_auth_session_instance,
    ):
        # Setup default return values
        mock_run_check_with_retries.return_value = True
        mock_run_create_with_retries.return_value = "test_result"
        mock_load_auth_session_instance.return_value = ({}, {})

        yield ExecuteCLIMocks(
            run_create_with_retries=mock_run_create_with_retries,
            run_check_with_retries=mock_run_check_with_retries,
            load_auth_session_instance=mock_load_auth_session_instance,
        )


class TestRunCheck:
    """Test suite for Auth Session controller functions."""

    @pytest.mark.asyncio
    async def test_calls_timeout_middleware_with_timeout(self, attempt_api_mocks: AttemptApiMocks):
        """Test that run_check calls timeout middleware with the correct timeout."""
        await run_check(
            auth=_get_empty_auth_session(),
            headless=False,
            timeout=6000,
        )

        attempt_api_mocks.extendable_timeout.assert_called_once_with(6000)

    @pytest.mark.asyncio
    async def test_calls_run_api_with_correct_parameters_and_parses_proxy(self, attempt_api_mocks: AttemptApiMocks):
        """Test that run_check calls run_api with correct parameters and parses proxy."""
        with patch("intuned_cli.controller.authsession.ProxyConfig.parse_from_str") as mock_parse_proxy:
            proxy_config = ProxyConfig(
                username="user",
                password="pass",
                server="proxy-server",
            )
            mock_parse_proxy.return_value = proxy_config

            auth = _get_empty_auth_session()

            await run_check(
                auth=auth,
                headless=False,
                timeout=999999999,
                proxy="proxy",
            )

            mock_parse_proxy.assert_called_once_with("proxy")
            attempt_api_mocks.run_api.assert_called_once()

            # Verify the call arguments
            call_args = attempt_api_mocks.run_api.call_args[0][0]
            assert call_args.automation_function.name == "auth-sessions/check"
            assert call_args.run_options.headless is False
            assert call_args.run_options.proxy is proxy_config
            assert call_args.auth.session.state is auth

    @pytest.mark.asyncio
    async def test_returns_if_check_returns(self, attempt_api_mocks: AttemptApiMocks):
        """Test that run_check returns the correct boolean values."""
        attempt_api_mocks.run_api.return_value = _check_passed_result()

        result_true = await run_check(
            auth=StorageState(cookies=[], origins=[], session_storage=[]),
            headless=False,
            timeout=999999999,
        )

        assert result_true is True

        attempt_api_mocks.run_api.return_value = _check_failed_result()

        result_false = await run_check(
            auth=_get_empty_auth_session(),
            headless=False,
            timeout=999999999,
        )

        assert result_false is False

    @pytest.mark.asyncio
    async def test_throws_error_when_check_fails_with_error(self, attempt_api_mocks: AttemptApiMocks):
        """Test that run_check handles errors correctly."""
        error = Exception("runApi failed")
        attempt_api_mocks.run_api.side_effect = error

        with pytest.raises(Exception, match="runApi failed"):
            await run_check(
                auth=StorageState(cookies=[], origins=[], session_storage=[]),
                headless=False,
                timeout=999999999,
            )

        # Test with AutomationError - should return False, not throw
        attempt_api_mocks.run_api.side_effect = AutomationError(Exception("failed"))

        with pytest.raises(Exception, match="failed"):
            await run_check(
                auth=StorageState(cookies=[], origins=[], session_storage=[]),
                headless=False,
                timeout=999999999,
            )


class TestRunCheckWithRetries:
    @pytest.mark.asyncio
    async def test_retries_the_check_if_it_fails(self, with_retries_mocks: WithRetriesMocks):
        """Test that run_check_with_retries retries the check if it fails."""
        with_retries_mocks.run_check.side_effect = [False, True]

        result = await run_check_with_retries(
            auth=_get_empty_auth_session(),
            retries=10,
            headless=False,
            timeout=999999999,
        )

        assert result is True
        assert with_retries_mocks.run_check.call_count == 2

    @pytest.mark.asyncio
    async def test_returns_false_if_all_retries_fail(self, with_retries_mocks: WithRetriesMocks):
        """Test that run_check_with_retries returns false if all retries fail."""
        with_retries_mocks.run_check.return_value = False

        result = await run_check_with_retries(
            auth=_get_empty_auth_session(),
            retries=10,
            headless=False,
            timeout=999999999,
        )

        assert result is False
        assert with_retries_mocks.run_check.call_count == 10

    @pytest.mark.asyncio
    async def test_continues_retrying_if_check_fails_due_to_automation_error(
        self, with_retries_mocks: WithRetriesMocks
    ):
        """Test that run_check_with_retries continues retrying if check fails due to an automation error."""
        with_retries_mocks.run_check.side_effect = [AutomationError(Exception("failed")), True]

        result = await run_check_with_retries(
            auth=_get_empty_auth_session(),
            retries=10,
            headless=False,
            timeout=999999999,
        )

        assert result is True
        assert with_retries_mocks.run_check.call_count == 2

    @pytest.mark.asyncio
    async def test_throws_error_if_check_fails_with_non_automation_error(self, with_retries_mocks: WithRetriesMocks):
        """Test that run_check_with_retries throws the error if check fails with a non-automation error."""
        error = Exception("runCheck failed")
        with_retries_mocks.run_check.side_effect = error

        with pytest.raises(Exception, match="runCheck failed"):
            await run_check_with_retries(
                auth=_get_empty_auth_session(),
                retries=10,
                headless=False,
                timeout=999999999,
            )

        with_retries_mocks.run_check.assert_called_once()


class TestRunCreate:
    @pytest.mark.asyncio
    async def test_calls_timeout_middleware_with_timeout(self, attempt_api_mocks: AttemptApiMocks):
        """Test that run_create calls timeout middleware with the correct timeout."""
        attempt_api_mocks.run_api.return_value = _create_success_result("session")

        await run_create(
            auth_session_input={},
            headless=False,
            timeout=6000,
        )

        attempt_api_mocks.extendable_timeout.assert_called_once_with(6000)

    @pytest.mark.asyncio
    async def test_calls_run_api_with_correct_parameters_and_parses_proxy(self, attempt_api_mocks: AttemptApiMocks):
        """Test that run_create calls run_api with correct parameters and parses proxy."""
        with patch("intuned_cli.controller.authsession.ProxyConfig.parse_from_str") as mock_parse_proxy:
            proxy_config = ProxyConfig(
                username="user",
                password="pass",
                server="proxy-server",
            )
            mock_parse_proxy.return_value = proxy_config
            attempt_api_mocks.run_api.return_value = _create_success_result("session")

            auth_session_input = {"some": "input"}
            await run_create(
                auth_session_input=auth_session_input,
                headless=False,
                timeout=999999999,
                proxy="proxy",
            )

            mock_parse_proxy.assert_called_once_with("proxy")
            attempt_api_mocks.run_api.assert_called_once()

            # Verify the call arguments
            call_args = attempt_api_mocks.run_api.call_args[0][0]
            assert call_args.automation_function.name == "auth-sessions/create"
            assert call_args.automation_function.params is auth_session_input
            assert call_args.run_options.headless is False
            assert call_args.run_options.proxy is proxy_config
            assert call_args.retrieve_session is True

    @pytest.mark.asyncio
    async def test_returns_if_create_returns(self, attempt_api_mocks: AttemptApiMocks):
        """Test that run_create returns the session."""
        attempt_api_mocks.run_api.return_value = _create_success_result("session")

        storage_state = await run_create(
            auth_session_input={},
            headless=False,
            timeout=999999999,
        )

        assert storage_state == "session"

    @pytest.mark.asyncio
    async def test_throws_error_when_create_fails_with_error(self, attempt_api_mocks: AttemptApiMocks):
        """Test that run_create throws the error when create fails."""
        error = Exception("runApi failed")
        attempt_api_mocks.run_api.side_effect = error

        with pytest.raises(Exception, match="runApi failed"):
            await run_create(
                auth_session_input={},
                headless=False,
                timeout=999999999,
            )


class TestRunCreateWithRetries:
    @pytest.mark.asyncio
    async def test_saves_the_auth_session_instance(self, with_retries_mocks: WithRetriesMocks):
        """Test that run_create_with_retries saves the auth session instance."""
        with_retries_mocks.run_create.return_value = "session"

        input: Any = dict()  # type: ignore
        metadata: Any = dict()  # type: ignore
        await run_create_with_retries(
            auth_session_id="testId",
            auth_session_input=input,
            metadata=metadata,
            retries=1,
            headless=False,
            timeout=30,
        )

        assert with_retries_mocks.run_create.call_count == 1
        with_retries_mocks.store_auth_session_instance.assert_called_once()
        call_args = with_retries_mocks.store_auth_session_instance.call_args.args
        assert call_args[0] == "session"
        assert call_args[1] == "testId"
        assert call_args[2] is input
        call_kwargs = with_retries_mocks.store_auth_session_instance.call_args.kwargs
        assert call_kwargs["metadata"] is metadata

    @pytest.mark.asyncio
    async def test_retries_if_it_fails_with_automation_error(self, with_retries_mocks: WithRetriesMocks):
        """Test that run_create_with_retries retries if it fails with automation error."""
        with_retries_mocks.run_create.side_effect = [AutomationError(Exception("failed")), "session"]

        await run_create_with_retries(
            auth_session_id="testId",
            auth_session_input={},
            retries=10,
            headless=False,
            timeout=30,
        )

        assert with_retries_mocks.run_create.call_count == 2

    @pytest.mark.asyncio
    async def test_throws_if_all_retries_fail(self, with_retries_mocks: WithRetriesMocks):
        """Test that run_create_with_retries throws if all retries fail."""
        with_retries_mocks.run_create.side_effect = AutomationError(Exception("failed"))

        with pytest.raises(CLIError):
            await run_create_with_retries(
                auth_session_id="testId",
                auth_session_input={},
                retries=3,
                headless=False,
                timeout=30,
            )

        assert with_retries_mocks.run_create.call_count == 3

    @pytest.mark.asyncio
    async def test_throws_error_if_create_fails_with_non_automation_error(self, with_retries_mocks: WithRetriesMocks):
        """Test that run_create_with_retries throws the error if create fails with a non-automation error."""
        error = Exception("create failed")
        with_retries_mocks.run_create.side_effect = error

        with pytest.raises(Exception, match="create failed"):
            await run_create_with_retries(
                auth_session_id="testId",
                auth_session_input={},
                retries=10,
                headless=False,
                timeout=30,
            )

        with_retries_mocks.run_create.assert_called_once()


class TestExecuteAuthSessionValidateCLI:
    @pytest.mark.asyncio
    async def test_asserts_check_api_file_exists(self, execute_cli_mocks: ExecuteCLIMocks, shared_mocks: SharedMocks):
        """Test that executeRunValidateAuthSessionCLI asserts check API file exists."""
        await execute_run_validate_auth_session_cli(
            id="testId",
            auto_recreate=False,
            check_retries=1,
            create_retries=1,
            headless=False,
            timeout=30,
        )

        shared_mocks.assert_api_file_exists.assert_called_once_with("auth-sessions", "check")

    @pytest.mark.asyncio
    async def test_succeeds_if_check_succeeds(self, execute_cli_mocks: ExecuteCLIMocks):
        """Test that executeRunValidateAuthSessionCLI succeeds if check succeeds."""

        auth = _get_empty_auth_session()
        execute_cli_mocks.load_auth_session_instance.return_value = (auth, {})

        result = await execute_run_validate_auth_session_cli(
            id="testId",
            auto_recreate=False,
            check_retries=1,
            create_retries=1,
            headless=False,
            timeout=30,
        )

        assert execute_cli_mocks.run_check_with_retries.call_count == 1
        assert execute_cli_mocks.run_create_with_retries.call_count == 0
        assert result == auth

    @pytest.mark.asyncio
    async def test_throws_if_check_fails_with_auto_recreate_disabled(self, execute_cli_mocks: ExecuteCLIMocks):
        """Test that executeRunValidateAuthSessionCLI throws if check fails with auto recreate disabled."""
        execute_cli_mocks.run_check_with_retries.return_value = False

        with pytest.raises(CLIError, match="Auto recreate is disabled"):
            await execute_run_validate_auth_session_cli(
                id="testId",
                auto_recreate=False,
                check_retries=1,
                create_retries=1,
                headless=False,
                timeout=30,
            )

    @pytest.mark.asyncio
    async def test_asserts_create_exists_if_check_fails_with_auto_recreate_enabled(
        self, execute_cli_mocks: ExecuteCLIMocks, shared_mocks: SharedMocks
    ):
        """Test that executeRunValidateAuthSessionCLI recreates if check fails with auto recreate enabled."""
        # First check fails, create succeeds, second check succeeds
        execute_cli_mocks.run_check_with_retries.side_effect = [False, True]
        auth = _get_empty_auth_session()
        execute_cli_mocks.run_create_with_retries.return_value = auth

        await execute_run_validate_auth_session_cli(
            id="testId",
            auto_recreate=True,
            check_retries=1,
            create_retries=1,
            headless=False,
            timeout=30,
        )

        # Should call assert for both check and create APIs
        shared_mocks.assert_api_file_exists.assert_any_call("auth-sessions", "create")

    @pytest.mark.asyncio
    async def test_raises_if_auth_session_is_manual_if_check_fails_with_auto_recreate_enabled(
        self, execute_cli_mocks: ExecuteCLIMocks
    ):
        """Test that executeRunValidateAuthSessionCLI raises if auth session is manual."""

        mock_metadata = Mock()
        mock_metadata.auth_session_type = "MANUAL"
        execute_cli_mocks.load_auth_session_instance.return_value = ({}, mock_metadata)
        execute_cli_mocks.run_check_with_retries.return_value = False

        with pytest.raises(CLIError):
            await execute_run_validate_auth_session_cli(
                id="testId",
                auto_recreate=True,
                check_retries=1,
                create_retries=1,
                headless=False,
                timeout=30,
            )

    @pytest.mark.asyncio
    async def test_raises_if_check_fails_then_create_fails_with_auto_recreate_enabled(
        self, execute_cli_mocks: ExecuteCLIMocks
    ):
        """Test that executeRunValidateAuthSessionCLI raises if create fails after check fails."""
        execute_cli_mocks.run_check_with_retries.return_value = False
        execute_cli_mocks.run_create_with_retries.side_effect = CLIError("create failed")

        with pytest.raises(
            CLIError,
        ):
            await execute_run_validate_auth_session_cli(
                id="testId",
                auto_recreate=True,
                check_retries=1,
                create_retries=1,
                headless=False,
                timeout=30,
            )

    @pytest.mark.asyncio
    async def test_raises_if_check_fails_then_create_succeeds_then_check_fails_with_auto_recreate_enabled(
        self, execute_cli_mocks: ExecuteCLIMocks
    ):
        """Test that executeRunValidateAuthSessionCLI raises if create fails after check fails."""
        execute_cli_mocks.run_check_with_retries.return_value = False
        execute_cli_mocks.run_create_with_retries.return_value = _get_empty_auth_session()

        with pytest.raises(
            CLIError,
        ):
            await execute_run_validate_auth_session_cli(
                id="testId",
                auto_recreate=True,
                check_retries=1,
                create_retries=1,
                headless=False,
                timeout=30,
            )

    @pytest.mark.asyncio
    async def test_succeeds_if_check_fails_then_create_succeeds_then_check_succeeds_with_auto_recreate_enabled(
        self, execute_cli_mocks: ExecuteCLIMocks
    ):
        """Test that executeRunValidateAuthSessionCLI raises if create fails after check fails."""
        auth = _get_empty_auth_session()
        execute_cli_mocks.run_check_with_retries.side_effect = [False, True]
        execute_cli_mocks.run_create_with_retries.return_value = auth

        result = await execute_run_validate_auth_session_cli(
            id="testId",
            auto_recreate=True,
            check_retries=1,
            create_retries=1,
            headless=False,
            timeout=30,
        )

        assert result == auth


class TestExecuteAuthSessionCreateCLI:
    @pytest.mark.asyncio
    async def test_asserts_create_and_check_api_files_exist(
        self, execute_cli_mocks: ExecuteCLIMocks, shared_mocks: SharedMocks
    ):
        """Test that executeRunCreateAuthSessionCLI asserts create and check API files exist."""
        execute_cli_mocks.run_create_with_retries.return_value = _get_empty_auth_session()

        await execute_run_create_auth_session_cli(
            input_data={},
            check_retries=1,
            create_retries=1,
            headless=False,
            timeout=30,
        )

        # Should assert both create and check API files exist
        assert shared_mocks.assert_api_file_exists.call_count == 2
        shared_mocks.assert_api_file_exists.assert_any_call("auth-sessions", "create")
        shared_mocks.assert_api_file_exists.assert_any_call("auth-sessions", "check")

    @pytest.mark.asyncio
    async def test_throws_if_create_fails(self, execute_cli_mocks: ExecuteCLIMocks):
        """Test that executeRunCreateAuthSessionCLI throws if create fails."""
        execute_cli_mocks.run_create_with_retries.side_effect = CLIError("create failed")

        with pytest.raises(CLIError):
            await execute_run_create_auth_session_cli(
                input_data={},
                check_retries=1,
                create_retries=1,
                headless=False,
                timeout=30,
            )

    @pytest.mark.asyncio
    async def test_throws_if_check_fails_after_create_succeeds(
        self,
        execute_cli_mocks: ExecuteCLIMocks,
    ):
        """Test that executeRunCreateAuthSessionCLI throws if check fails after create succeeds."""
        execute_cli_mocks.run_create_with_retries.return_value = _get_empty_auth_session()
        execute_cli_mocks.run_check_with_retries.return_value = False

        with pytest.raises(CLIError, match="Failed to create auth session"):
            await execute_run_create_auth_session_cli(
                input_data={},
                check_retries=1,
                create_retries=1,
                headless=False,
                timeout=30,
            )

    @pytest.mark.asyncio
    async def test_saves_to_auth_session_instance_path_if_create_and_check_succeed(
        self, execute_cli_mocks: ExecuteCLIMocks
    ):
        """Test that executeRunCreateAuthSessionCLI saves to auth session instance path if create and check succeed."""
        execute_cli_mocks.run_create_with_retries.return_value = _get_empty_auth_session()
        execute_cli_mocks.run_check_with_retries.return_value = True

        input: Any = dict()  # type: ignore
        await execute_run_create_auth_session_cli(
            input_data=input,
            check_retries=1,
            create_retries=1,
            headless=False,
            timeout=30,
        )

        # run_create_with_retries is tested to save in its own tests, so just verify it was called here
        assert execute_cli_mocks.run_create_with_retries.call_count == 1
        call_args = execute_cli_mocks.run_create_with_retries.call_args.kwargs
        assert call_args["auth_session_input"] is input

    @pytest.mark.asyncio
    async def test_uses_auth_session_id_to_save_if_provided(self, execute_cli_mocks: ExecuteCLIMocks):
        """Test that executeRunCreateAuthSessionCLI uses auth session id to save if provided."""
        execute_cli_mocks.run_create_with_retries.side_effect = [
            _create_success_result("session"),
            _check_passed_result(),
        ]

        await execute_run_create_auth_session_cli(
            id="customId",
            input_data={},
            check_retries=1,
            create_retries=1,
            headless=False,
            timeout=30,
        )

        # Verify that store was called with the provided id
        assert execute_cli_mocks.run_create_with_retries.call_count == 1
        call_args = execute_cli_mocks.run_create_with_retries.call_args.kwargs
        assert call_args["auth_session_id"] == "customId"


class TestExecuteAuthSessionUpdateCLI:
    @pytest.mark.asyncio
    async def test_throws_if_auth_session_is_manual(self, execute_cli_mocks: ExecuteCLIMocks):
        """Test that executeRunUpdateAuthSessionCLI throws if auth session is manual."""
        mock_metadata = Mock()
        mock_metadata.auth_session_type = "MANUAL"
        execute_cli_mocks.load_auth_session_instance.return_value = ({}, mock_metadata)

        with pytest.raises(CLIError):
            await execute_run_update_auth_session_cli(
                id="testId",
                check_retries=1,
                create_retries=1,
                headless=False,
                timeout=30,
            )

    @pytest.mark.asyncio
    async def test_calls_create_with_existing_input_if_no_input_provided(self, execute_cli_mocks: ExecuteCLIMocks):
        """Test that executeRunUpdateAuthSessionCLI calls create with existing input if no input provided."""
        mock_metadata = Mock()
        mock_metadata.auth_session_input = {"existing": "data"}
        execute_cli_mocks.load_auth_session_instance.return_value = ({}, mock_metadata)

        with patch("intuned_cli.controller.authsession.execute_run_create_auth_session_cli") as mock_create_cli:
            await execute_run_update_auth_session_cli(
                id="testId",
                check_retries=1,
                create_retries=1,
                headless=False,
                timeout=30,
            )

            # Should use the provided input data
            mock_create_cli.assert_called_once_with(
                id="testId",
                input_data={"existing": "data"},
                check_retries=1,
                create_retries=1,
                headless=False,
                timeout=30,
                proxy=None,
                metadata=mock_metadata,
                log=False,
            )

    @pytest.mark.asyncio
    async def test_calls_create_with_new_input_if_provided(self, execute_cli_mocks: ExecuteCLIMocks):
        """Test that executeRunUpdateAuthSessionCLI calls create with new input if provided."""
        execute_cli_mocks.load_auth_session_instance.return_value = ({}, {})

        with patch("intuned_cli.controller.authsession.execute_run_create_auth_session_cli") as mock_create_cli:
            await execute_run_update_auth_session_cli(
                id="testId",
                input_data={"new": "data"},
                check_retries=1,
                create_retries=1,
                headless=False,
                timeout=30,
            )

            # Should use the provided input data
            call_args = mock_create_cli.call_args.kwargs
            assert call_args["input_data"] == {"new": "data"}


class TestExecuteAttemptAuthSessionCLI:
    @pytest.mark.asyncio
    async def test_asserts_check_api_file_exists(self, execute_cli_mocks: ExecuteCLIMocks, shared_mocks: SharedMocks):
        """Test that executeAttemptCheckAuthSessionCLI asserts check API file exists."""

        await execute_attempt_check_auth_session_cli(
            id="testId",
            headless=False,
            timeout=30,
        )

        shared_mocks.assert_api_file_exists.assert_called_once_with("auth-sessions", "check")

    @pytest.mark.asyncio
    async def test_succeeds_if_check_succeeds(self, execute_cli_mocks: ExecuteCLIMocks):
        """Test that executeAttemptCheckAuthSessionCLI succeeds if check succeeds."""
        execute_cli_mocks.run_check_with_retries.return_value = True

        await execute_attempt_check_auth_session_cli(
            id="testId",
            headless=False,
            timeout=30,
        )

    @pytest.mark.asyncio
    async def test_throws_if_check_fails(self, execute_cli_mocks: ExecuteCLIMocks):
        """Test that executeAttemptCheckAuthSessionCLI throws if check fails."""
        execute_cli_mocks.run_check_with_retries.return_value = False

        with pytest.raises(CLIError):
            await execute_attempt_check_auth_session_cli(
                id="testId",
                headless=False,
                timeout=30,
            )


class TestExecuteAttemptCreateAuthSessionCLI:
    @pytest.mark.asyncio
    async def test_asserts_create_api_file_exists(self, execute_cli_mocks: ExecuteCLIMocks, shared_mocks: SharedMocks):
        """Test that executeAttemptCreateAuthSessionCLI asserts create API file exists."""

        await execute_attempt_create_auth_session_cli(
            input_data={},
            headless=False,
            timeout=30,
        )

        shared_mocks.assert_api_file_exists.assert_called_once_with("auth-sessions", "create")

    @pytest.mark.asyncio
    async def test_throws_if_create_fails(
        self,
        execute_cli_mocks: ExecuteCLIMocks,
    ):
        """Test that executeAttemptCreateAuthSessionCLI throws if create fails."""
        execute_cli_mocks.run_create_with_retries.side_effect = CLIError("create failed")

        with pytest.raises(CLIError):
            await execute_attempt_create_auth_session_cli(
                input_data={},
                headless=False,
                timeout=30,
            )

    @pytest.mark.asyncio
    async def test_saves_to_auth_session_instance_path_if_create_succeeds(self, execute_cli_mocks: ExecuteCLIMocks):
        """Test that executeAttemptCreateAuthSessionCLI saves to auth session instance path if create succeeds."""
        execute_cli_mocks.run_create_with_retries.return_value = _get_empty_auth_session()

        await execute_attempt_create_auth_session_cli(
            input_data={},
            headless=False,
            timeout=30,
        )

        execute_cli_mocks.run_create_with_retries.assert_called_once()
        call_args = execute_cli_mocks.run_create_with_retries.call_args.kwargs
        assert call_args["auth_session_input"] == {}
        assert call_args["retries"] == 1
        assert call_args["headless"] is False
        assert call_args["timeout"] == 30
        assert call_args["proxy"] is None

    @pytest.mark.asyncio
    async def test_uses_auth_session_id_to_save_if_provided(self, execute_cli_mocks: ExecuteCLIMocks):
        """Test that executeAttemptCreateAuthSessionCLI uses auth session id to save if provided."""
        execute_cli_mocks.run_create_with_retries.return_value = _get_empty_auth_session()

        await execute_attempt_create_auth_session_cli(
            id="customId",
            input_data={},
            headless=False,
            timeout=30,
        )

        # Verify that store was called with the provided id
        execute_cli_mocks.run_create_with_retries.assert_called_once()
        call_args = execute_cli_mocks.run_create_with_retries.call_args.kwargs
        assert call_args["auth_session_id"] == "customId"
