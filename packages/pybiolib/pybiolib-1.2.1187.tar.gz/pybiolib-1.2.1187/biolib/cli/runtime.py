import click

import biolib.runtime


@click.group(help='Commands available within a BioLib runtime')
def runtime() -> None:
    pass


@runtime.command(help='Set the name prefix of the main result')
@click.argument('result-prefix', required=True)
def set_main_result_prefix(result_prefix: str) -> None:
    biolib.runtime.set_main_result_prefix(result_prefix)
