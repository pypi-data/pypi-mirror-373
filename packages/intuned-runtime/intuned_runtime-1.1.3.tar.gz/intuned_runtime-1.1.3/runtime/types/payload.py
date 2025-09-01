from typing import Any
from typing import TypedDict


class Payload(TypedDict):
    api: str
    parameters: dict[str, Any]
