from pydantic import BaseModel
from pydantic import Field
from pydantic import RootModel


class FileSystemTree(RootModel[dict[str, "DirectoryNode | FileNode"]]):
    root: dict[str, "DirectoryNode | FileNode"]


class DirectoryNode(BaseModel):
    directory: "FileSystemTree"


class FileNodeContent(BaseModel):
    contents: str


class FileNode(BaseModel):
    file: "FileNodeContent"


FileSystemTree.model_rebuild()


class IntunedJson(BaseModel):
    model_config = {"populate_by_name": True}

    class _AuthSessions(BaseModel):
        enabled: bool

    auth_sessions: _AuthSessions = Field(alias="authSessions")
    project_name: str | None = Field(alias="projectName", default=None)
    workspace_id: str | None = Field(alias="workspaceId", default=None)
