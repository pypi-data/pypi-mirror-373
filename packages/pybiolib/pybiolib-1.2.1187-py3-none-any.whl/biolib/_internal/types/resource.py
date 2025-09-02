from .app import AppSlimDict
from .data_record import DataRecordSlimDict
from .experiment import DeprecatedExperimentDict
from .typing import Optional, TypedDict


class ResourceDict(TypedDict):
    uuid: str
    uri: str
    name: str
    created_at: str
    description: str


class ResourceDetailedDict(ResourceDict):
    app: Optional[AppSlimDict]
    data_record: Optional[DataRecordSlimDict]
    experiment: Optional[DeprecatedExperimentDict]
