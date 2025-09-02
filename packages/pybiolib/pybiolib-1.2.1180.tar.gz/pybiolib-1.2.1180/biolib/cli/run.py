import sys

import click

from biolib import biolib_errors, utils
from biolib.app import BioLibApp
from biolib.experiments.experiment import Experiment
from biolib.typing_utils import Optional, Tuple


@click.command(
    context_settings=dict(ignore_unknown_options=True, allow_interspersed_args=False),
    help='Run an application on BioLib.',
)
@click.option('--experiment', type=str, required=False, help='Experiment name or URI to add the run to.')
@click.option('--local', is_flag=True, required=False, help='Run the application locally.')
@click.option('--non-blocking', is_flag=True, required=False, help='Run the application non blocking.')
@click.argument('uri', required=True)
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def run(experiment: Optional[str], local: bool, non_blocking: bool, uri: str, args: Tuple[str]) -> None:
    if experiment:
        with Experiment(uri=experiment):
            _run(local=local, non_blocking=non_blocking, uri=uri, args=args)
    else:
        _run(local=local, non_blocking=non_blocking, uri=uri, args=args)


def _run(local: bool, non_blocking: bool, uri: str, args: Tuple[str]) -> None:
    try:
        app = BioLibApp(uri=uri)
    except biolib_errors.BioLibError as error:
        print(f'An error occurred:\n {error.message}', file=sys.stderr)
        exit(1)

    def _get_stdin():
        stdin = None
        if not sys.stdin.isatty() and not utils.IS_DEV:
            stdin = sys.stdin.read()
        return stdin

    blocking = not non_blocking
    job = app.cli(
        args=list(args),
        stdin=_get_stdin(),
        files=None,
        machine=('local' if local else ''),
        blocking=blocking,
    )

    if blocking:
        job.save_files('biolib_results', overwrite=True)

        # Write stdout and stderr if it has not been streamed (Markdown is not streamed)
        if app.version.get('stdout_render_type') == 'markdown' or not sys.stdout.isatty():
            sys.stdout.buffer.write(job.get_stdout())
            sys.stderr.buffer.write(job.get_stderr())

        exit(job.get_exit_code())
    else:
        print('{"job_id": "' + str(job.id) + '"}')
