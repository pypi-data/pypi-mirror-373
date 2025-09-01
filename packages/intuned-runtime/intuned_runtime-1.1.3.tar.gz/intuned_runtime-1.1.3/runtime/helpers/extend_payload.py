from runtime.context.context import IntunedContext

from ..types import Payload
from .extend_timeout import extend_timeout


def extend_payload(*payload: Payload):
    IntunedContext.current().extended_payloads += [*payload]
    extend_timeout()
