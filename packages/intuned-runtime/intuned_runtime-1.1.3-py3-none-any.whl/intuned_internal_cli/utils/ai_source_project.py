from dataclasses import dataclass
from typing import Any

from requests import post

from .code_tree import FileSystemTree


@dataclass
class AiSourceInfo:
    workspace_id: str
    api_key: str
    id: str
    version_id: str
    environment_url: str | None

    @classmethod
    def from_json(cls, json_data: dict[str, Any]):
        return cls(**json_data)


def deploy_ai_source(code_tree: FileSystemTree, ai_source_info: AiSourceInfo):
    result = post(
        f"{ai_source_info.environment_url}/api/v1/workspace/{ai_source_info.workspace_id}/ai-source/{ai_source_info.id}/version/{ai_source_info.version_id}/deploy",
        headers={"Content-Type": "application/json", "x-api-key": ai_source_info.api_key},
        json={"codeTree": code_tree},
    )

    if not result.ok:
        print(result.text)
    return result.ok
