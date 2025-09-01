import json
from typing import Any
from typing import override

from pydantic import BaseModel


class PydanticEncoder(json.JSONEncoder):
    @override
    def default(self, o: Any):
        if isinstance(o, BaseModel):
            return o.model_dump(
                by_alias=True,
            )
        return super().default(o)
