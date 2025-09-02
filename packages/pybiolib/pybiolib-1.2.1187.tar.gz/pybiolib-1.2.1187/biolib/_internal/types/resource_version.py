from .typing import Literal, NotRequired, TypedDict


class ResourceVersionDict(TypedDict):
    uuid: str
    semantic_version: str
    state: Literal['published', 'unpublished']
    created_at: str
    git_branch_name: NotRequired[str]


class ResourceVersionDetailedDict(ResourceVersionDict):
    pass
