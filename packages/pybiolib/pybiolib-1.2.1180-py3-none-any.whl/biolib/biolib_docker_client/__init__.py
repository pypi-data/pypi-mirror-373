import os

import docker  # type: ignore


class BiolibDockerClient:
    docker_client = None

    @staticmethod
    def get_docker_client():
        if BiolibDockerClient.docker_client is None:
            try:
                # Fixes: https://github.com/docker/docker-py/issues/2433
                if os.environ.get('DOCKER_CERT_PATH'):
                    request_ca_bundle_env = os.environ.pop('REQUESTS_CA_BUNDLE', None)

                # the final step of docker push can take a long time,
                # so set a long timeout for operations performed by the docker client
                # ~66 min (4000s) is the maximum supported by AWS load balancers
                BiolibDockerClient.docker_client = docker.from_env(timeout=4000)

                if os.environ.get('DOCKER_CERT_PATH'):
                    os.environ['REQUESTS_CA_BUNDLE'] = request_ca_bundle_env
                # Run a docker command to see if docker engine is running
                BiolibDockerClient.docker_client.info()
            except Exception as exception:
                raise Exception(
                    'Failed to connect to Docker, please make sure it is installed and running'
                ) from exception
        return BiolibDockerClient.docker_client

    @staticmethod
    def is_docker_running():
        try:
            BiolibDockerClient.get_docker_client()
            return True
        except Exception:  # pylint: disable=broad-except
            return False
