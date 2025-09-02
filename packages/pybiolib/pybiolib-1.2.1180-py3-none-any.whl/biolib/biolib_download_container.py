from typing import Iterable
from biolib.app import BioLibApp
from biolib.biolib_api_client import JobState
from biolib.biolib_docker_client import BiolibDockerClient
from biolib.biolib_logging import logger
from biolib._internal.push_application import DockerStatusUpdate, process_docker_status_updates
from biolib.biolib_api_client.biolib_job_api import BiolibJobApi


def download_container_from_uri(uri: str) -> None:
    docker_client = BiolibDockerClient.get_docker_client()
    app = BioLibApp(uri=uri)
    job_response = BiolibJobApi.create(app_version_id=app.version["public_id"])
    job_uuid = job_response["uuid"]
    auth_config = {'username': 'biolib', 'password': f',{job_uuid}'}
    try:
        docker_image_uri = job_response["app_version"]["modules"][0]["absolute_image_uri"]

        logger.info(msg=f"Pulling Docker image for {uri}...")

        repo, tag = docker_image_uri.split(':')
        pull_status_updates: Iterable[DockerStatusUpdate] = docker_client.api.pull(
            decode=True,
            repository=repo,
            stream=True,
            tag=tag,
            auth_config=auth_config
        )
        process_docker_status_updates(status_updates=pull_status_updates, action='Pulling')
        image = docker_client.images.get(docker_image_uri)
        app_uri_repo, app_uri_tag = app.uri.lower().split(':')
        image.tag(repository=app_uri_repo, tag=app_uri_tag)
        docker_client.images.remove(docker_image_uri, force=True)
        BiolibJobApi.update_state(job_uuid=job_response["public_id"], state=JobState.COMPLETED)

    except Exception as error:
        logger.error(msg=f"Could not pull Docker image for {uri} due to {error}")
        BiolibJobApi.update_state(job_uuid=job_response["public_id"], state=JobState.FAILED)
