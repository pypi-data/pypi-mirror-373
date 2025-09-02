import logging
import platform
import sys

import click

from biolib.biolib_logging import logger, logger_no_user_data
from biolib.typing_utils import Optional


@click.command(help='Start a local compute node', hidden=True)
@click.option('--host', default='127.0.0.1', required=False)  # TODO: Validate host
@click.option('--port', default=5000, type=click.IntRange(1, 65_535), required=False)
@click.option('--tls-certificate', type=click.Path(exists=True), required=False, hidden=True)
@click.option('--tls-key', type=click.Path(exists=True), required=False, hidden=True)
def start(host: str, port: int, tls_certificate: Optional[str], tls_key: Optional[str]) -> None:
    logger.configure(default_log_level=logging.INFO)
    logger_no_user_data.configure(default_log_level=logging.INFO)
    if platform.system() == 'Windows':
        raise Exception('Starting a compute node is currently not supported on Windows')

    if tls_certificate and not tls_key or tls_key and not tls_certificate:
        raise Exception('Options --tls-certificate and --tls-key must be specified together')

    try:
        from biolib.compute_node.webserver import webserver  # pylint: disable=import-outside-toplevel

        webserver.start_webserver(
            host=host,
            port=port,
            tls_pem_key_path=tls_key,
            tls_pem_certificate_path=tls_certificate,
        )
    except ModuleNotFoundError as error:
        if error.name in ('flask', 'gunicorn'):
            print(
                'To use this command, please install the compute-node extras with '
                '"pip3 install --upgrade pybiolib[compute-node]"',
                file=sys.stderr,
            )
            sys.exit(1)

        raise error
