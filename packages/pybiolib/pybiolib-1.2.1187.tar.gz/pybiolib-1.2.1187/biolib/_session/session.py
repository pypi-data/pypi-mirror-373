from biolib import utils
from biolib._internal.types import Optional
from biolib.api.client import ApiClient, ApiClientInitDict
from biolib.app import BioLibApp


class Session:
    def __init__(self, _init_dict: ApiClientInitDict) -> None:
        self._api = ApiClient(_init_dict=_init_dict)

    @staticmethod
    def get_session(refresh_token: str, base_url: Optional[str] = None, client_type: Optional[str] = None) -> 'Session':
        return Session(
            _init_dict=ApiClientInitDict(
                refresh_token=refresh_token,
                base_url=base_url or utils.load_base_url_from_env(),
                client_type=client_type,
            )
        )

    def load(self, uri: str, suppress_version_warning: bool = False) -> BioLibApp:
        r"""Load a BioLib application by its URI or website URL.

        Args:
            uri (str): The URI or website URL of the application to load. Can be either:
                - App URI (e.g., 'biolib/myapp:1.0.0')
                - Website URL (e.g., 'https://biolib.com/biolib/myapp/')
            suppress_version_warning (bool): If True, don't print a warning when no version is specified.
                Defaults to False.

        Returns:
            BioLibApp: The loaded application object

        Example::

            >>> # Load by URI
            >>> app = biolib.load('biolib/myapp:1.0.0')
            >>> # Load by website URL
            >>> app = biolib.load('https://biolib.com/biolib/myapp/')
            >>> result = app.cli('--help')
        """
        return BioLibApp(uri=uri, _api_client=self._api, suppress_version_warning=suppress_version_warning)
