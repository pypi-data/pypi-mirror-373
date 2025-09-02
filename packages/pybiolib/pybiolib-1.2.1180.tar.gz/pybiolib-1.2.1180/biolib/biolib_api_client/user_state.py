from biolib.utils.cache_state import CacheState
from biolib.typing_utils import TypedDict, Optional


# TODO: Save job keys in the user state instead of a separate state file
# UuidStr = str
# class JobStateType(TypedDict):
#     job_uuid: UuidStr
#     aes_key: Optional[str]


class UserStateType(TypedDict):
    refresh_token: Optional[str]
    # jobs: Dict[UuidStr, JobStateType]


class UserState(CacheState[UserStateType]):

    @property
    def _state_path(self) -> str:
        return f'{self._user_cache_dir}/user-state.json'

    def _get_default_state(self) -> UserStateType:
        return UserStateType(refresh_token=None)
