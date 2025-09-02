import os
from datetime import datetime, timedelta
from urllib.parse import urlparse

from biolib.api import client as api_client
from biolib.biolib_api_client.lfs_types import DataRecordVersion
from biolib.biolib_binary_format.utils import RemoteEndpoint
from biolib.biolib_logging import logger
from biolib.typing_utils import Optional


class DataRecordRemoteStorageEndpoint(RemoteEndpoint):
    def __init__(self, resource_version_uuid: str):
        self._resource_version_uuid: str = resource_version_uuid
        self._expires_at: Optional[datetime] = None
        self._presigned_url: Optional[str] = None

    def get_remote_url(self) -> str:
        if not self._presigned_url or not self._expires_at or datetime.utcnow() > self._expires_at:
            lfs_version: DataRecordVersion = api_client.get(
                path=f'/lfs/versions/{self._resource_version_uuid}/',
            ).json()

            app_caller_proxy_job_storage_base_url = os.getenv('BIOLIB_CLOUD_JOB_STORAGE_BASE_URL', '')
            if app_caller_proxy_job_storage_base_url:
                # Done to hit App Caller Proxy when downloading from inside an app
                parsed_url = urlparse(lfs_version['presigned_download_url'])
                self._presigned_url = f'{app_caller_proxy_job_storage_base_url}{parsed_url.path}?{parsed_url.query}'
            else:
                self._presigned_url = lfs_version['presigned_download_url']

            self._expires_at = datetime.utcnow() + timedelta(minutes=8)
            logger.debug(
                f'DataRecord "{self._resource_version_uuid}" fetched presigned URL '
                f'with expiry at {self._expires_at.isoformat()}'
            )

        return self._presigned_url
