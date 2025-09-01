from abc import ABC
from typing import Any
from typing import Iterable
from typing import Literal

RunErrorCode = Literal[
    "APINotFoundError",
    "InvalidAPIError",
    "InvalidCheckError",
    "AbortedError",
    "AuthRequiredError",
    "AuthCheckNotFoundError",
    "AuthCheckFailedError",
    "MaxLevelsExceededError",
    "AutomationError",
    "InternalInvalidInputError",
]


class RunApiError(Exception, ABC):
    def __init__(self, message: str, code: RunErrorCode):
        super().__init__(message)
        self.code = code
        self.details: Any = None

    @property
    def json(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "details": self.details,
        }


class RunIdNotProvidedError(RunApiError):
    def __init__(self):
        super().__init__(
            "runId header not provided",
            "InvalidAPIError",
        )


class ApiNotFoundError(RunApiError):
    def __init__(self, module: str):
        super().__init__(
            f"Module {module} not found",
            "APINotFoundError",
        )


class NoAutomationInApiError(RunApiError):
    def __init__(self, module: str, automation_function_names: str | Iterable[str] = "automation"):
        if isinstance(automation_function_names, str):
            automation_function_names = [automation_function_names]
        super().__init__(
            f"Module {module} does not have {" or ".join([f"`{fn}`" for fn in automation_function_names])} function defined",
            "APINotFoundError",
        )


class AutomationNotCoroutineError(RunApiError):
    def __init__(self, module: str, automation_function_name: str = "automation"):
        super().__init__(
            f"`{automation_function_name}` function in module {module} is not a coroutine function",
            "InvalidAPIError",
        )


class AutomationError(RunApiError):
    _error: BaseException

    def __init__(self, error: BaseException):
        # Get all public attributes of the exception
        error_props = {key: str(value) for key, value in error.__dict__.items() if not key.startswith("_")}

        super().__init__(
            str(error),
            "AutomationError",
        )

        self._error = error

        self.details = {
            "error_props": error_props,
            "error_type": error.__class__.__name__,
            "name": error.__class__.__name__,
            "message": str(error),
        }

    @property
    def error(self) -> BaseException:
        return self._error


class AutomationTimeoutError(RunApiError):
    def __init__(self):
        super().__init__(
            "Run timed out",
            "AbortedError",
        )


class SessionMissingError(RunApiError):
    def __init__(self):
        super().__init__(
            "Session missing",
            "AuthRequiredError",
        )


class InvalidSessionError(RunApiError):
    def __init__(self):
        super().__init__(
            "Invalid auth session",
            "AuthCheckFailedError",
        )


class InternalInvalidInputError(RunApiError):
    def __init__(self, message: str, details: Any | None = None):
        super().__init__(
            f"Internal error: {message}. Please report this issue to the Intuned team.",
            "InternalInvalidInputError",
        )
        self.details = details
