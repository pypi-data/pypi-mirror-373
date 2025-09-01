from contextvars import ContextVar
from contextvars import Token
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import ClassVar
from typing import Optional

from pydantic import BaseModel
from pydantic import Field

from ..types import Payload
from ..types.run_types import IntunedRunContext


class IntunedContext(BaseModel):
    _current: ClassVar[ContextVar["IntunedContext"]] = ContextVar("_current")

    functions_token: str | None = None
    extend_timeout: Callable[[], Awaitable[Any]] | None = None
    extended_payloads: list[Payload] = Field(default_factory=lambda: list[Payload]())
    run_context: IntunedRunContext | None = None
    get_auth_session_parameters: Callable[[], Awaitable[dict[str, Any]]] | None = None

    _token: Token["IntunedContext"] | None = None

    @classmethod
    def current(cls) -> "IntunedContext":
        try:
            current_context = cls._current.get()
        except LookupError as e:
            raise LookupError("No context found. Please use `IntunedContext.use()` to create a new context.") from e
        return current_context

    def __enter__(self) -> "IntunedContext":
        """
        Enter the context.
        """
        if self._token:
            raise RuntimeError("Context was already entered with `__enter__`.")
        self._token = self._current.set(self)
        return self

    def __exit__(self, exc_type: Optional[type], exc_value: Optional[BaseException], traceback: Optional[Any]) -> None:
        """
        Exit the context.
        """
        if not self._token:
            raise RuntimeError("Context was not entered with `__enter__`.")
        self._current.reset(self._token)
        self._token = None
