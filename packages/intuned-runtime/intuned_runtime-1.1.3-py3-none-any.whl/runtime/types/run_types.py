from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional
from typing import Union
from urllib.parse import urlparse

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic.alias_generators import to_camel


class CamelBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class ProxyConfig(CamelBaseModel):
    server: str
    username: str
    password: str

    @classmethod
    def parse_from_str(cls, proxy_str: str) -> "ProxyConfig":
        parts = urlparse(proxy_str)
        username = parts.username or ""
        password = parts.password or ""
        hostname = parts.hostname or ""
        port = f":{parts.port}" if parts.port else ""
        domain = f"{parts.scheme}://{hostname}{port}"

        return ProxyConfig(
            server=domain,
            username=username,
            password=password,
        )


class SameSite(str, Enum):
    STRICT = "Strict"
    LAX = "Lax"
    NONE = "None"


class Cookie(CamelBaseModel):
    name: str
    value: str
    domain: str
    path: str
    expires: float
    http_only: bool
    secure: bool
    same_site: SameSite


class StorageItem(CamelBaseModel):
    name: str
    value: str


class Origin(CamelBaseModel):
    origin: str
    local_storage: List[StorageItem]


class SessionStorageOrigin(CamelBaseModel):
    origin: str
    session_storage: List[StorageItem]


class StorageState(CamelBaseModel):
    cookies: List[Cookie]
    origins: List[Origin]
    session_storage: Optional[List[SessionStorageOrigin]]


class FileSession(CamelBaseModel):
    type: Literal["file"] = "file"
    path: str


class StateSession(CamelBaseModel):
    type: Literal["state"] = "state"
    state: Optional[Optional[StorageState]]


RunApiSession = Union[FileSession, StateSession]


class RunBody(CamelBaseModel):
    params: dict[str, Any] | None = None
    functions_token: str | None = None
    proxy: Optional[ProxyConfig] = None
    session: Optional[StorageState] = None


class StandaloneRunOptions(CamelBaseModel):
    environment: Literal["standalone"] = "standalone"
    headless: bool = True
    proxy: Optional[ProxyConfig] = None


class CDPRunOptions(CamelBaseModel):
    environment: Literal["cdp"] = "cdp"
    cdp_address: str


class AutomationFunction(CamelBaseModel):
    name: str
    params: Optional[Any] = None


class TracingEnabled(CamelBaseModel):
    enabled: Literal[True] = True
    file_path: str


class TracingDisabled(CamelBaseModel):
    enabled: Literal[False] = False


class Auth(CamelBaseModel):
    session: RunApiSession
    run_check: bool = False


class IntunedRunContext(CamelBaseModel):
    job_id: str | None = None
    job_run_id: str | None = None
    run_id: str | None = None
    auth_session_id: str | None = None


class RunApiParameters(CamelBaseModel):
    automation_function: AutomationFunction
    tracing: Union[TracingEnabled, TracingDisabled] = Field(default_factory=TracingDisabled)
    auth: Optional[Auth] = None
    run_options: Union[StandaloneRunOptions, CDPRunOptions] = Field(default_factory=StandaloneRunOptions)
    retrieve_session: bool = False
    functions_token: str | None = None
    context: Optional[IntunedRunContext] = None


class RunApiResultOk(CamelBaseModel):
    result: Any
    extended_payloads: Optional[List[Any]]  # Payload type


class RunApiResultWithSessionOk(RunApiResultOk):
    session: Dict[str, Any]  # IntunedStorageState type


class PayloadToAppend(CamelBaseModel):
    api_name: str
    parameters: Dict[str, Any]


class RunAutomationSuccessResult(CamelBaseModel):
    result: Any
    payload_to_append: Optional[list[PayloadToAppend]] = Field(default_factory=list[PayloadToAppend])
    session: Optional[StorageState] = None


class RunAutomationErrorResult(CamelBaseModel):
    error: str
    message: str
    status: Optional[int]
    details: Optional[Any]
    additional_fields: Dict[str, Any] = Field(default_factory=dict)


RunAutomationResult = Union[RunAutomationSuccessResult, RunAutomationErrorResult]


class RunAutomationResponse(CamelBaseModel):
    status: int
    body: RunAutomationResult


class JobPayload(CamelBaseModel):
    headers: Dict[str, str] = Field(default_factory=dict)
    original_payload: dict[Any, Any]
    payload: RunBody
    start_time: int
    function_name: str
    receipt_handle: str
    trace_signed_url: str | None = None
    session: StorageState | None = None
