"""SpeeDBeeSynapse custom component development environment tool."""
from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any, Callable, Final, Optional

import click
from watchfiles import BaseFilter, Change, watch

from .errors import SccdeError
from .main import Sccde

PACKAGE_SUFFIX = '.sccpkg'


def _handle_sccde_errors(func: Callable) -> Callable:
    """Handle SCCDE errors."""
    def new_func(*args: Any, **kwargs: Any) -> Any: # noqa: ANN401
        try:
            return func(*args, **kwargs)
        except SccdeError as exc:
            click.echo(str(exc), err=True)
            sys.exit(1)

    new_func.__name__ = func.__name__
    return new_func


@click.group()
def cli() -> None:
    """Make subcommand group."""


@cli.command()
@click.argument('target_dir', required=False, type=click.Path(file_okay=False, dir_okay=True, path_type=Path))
@_handle_sccde_errors
def init(target_dir: Optional[Path]) -> None:
    """Initialize directory."""
    target_dir = target_dir if target_dir else Path()
    sccde = Sccde(target_dir)

    sccde.init('Custom component package example')
    click.echo(f'The directory `{target_dir.absolute()}` is configured for SCCDE.')

    sccde.add_sample('python', 'collector', 'json')
    click.echo('Sample custom component is created.')


@cli.command()
@click.option('-C', default=Path(), type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.option('-l', '--sample-language', default='python', type=click.Choice(['c', 'python']))
@click.option('-t', '--sample-type', default='collector', type=click.Choice(['collector', 'serializer', 'emitter']))
@click.option('-u', '--ui_type', default='json', type=click.Choice(['none', 'json', 'html']))
@_handle_sccde_errors
def add(c: Path, sample_language: str, sample_type: str, ui_type: str) -> None:
    """Add sample component."""
    sccde = Sccde(c)
    sccde.add_sample(sample_language, sample_type, ui_type)
    click.echo('Sample custom component is created.')


@cli.command()
@click.option('-C', default=Path(), type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.option('-o', '--out', type=click.Path(path_type=Path))
@_handle_sccde_errors
def make_package(c: Path, out: Optional[Path]) -> None:
    """Make package."""
    out = out.with_suffix(PACKAGE_SUFFIX) if out else None
    sccde = Sccde(c)
    sccde.make_package(out)


@cli.command()
@click.option('-C', default=Path(), type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.option('-h', '--host', default='127.0.0.1', type=str)
@click.option('-p', '--port', default=8000, type=click.IntRange(1, 65535))
@click.option('--reload/--no-reload', default=False)
@click.option('--verbose', is_flag=True)
@_handle_sccde_errors
def serve(*, c: Path, host: str, port: int, reload: bool, verbose: bool) -> None:
    """Start test server."""
    sccde = Sccde(c)
    server = sccde.server(host, port, verbose=verbose)

    click.echo('Preparing Synapse data directories..')
    with server.start():
        url = f'http://{host}:{port}'
        click.echo(f'Synapse server ready: {url}')
        try:
            if reload:
                click.echo(f'Watch dir {sccde.work_dir} for reloading.')
                for changes in watch(sccde.work_dir, watch_filter=WatchFilter(), step=1000):
                    for (change_type, file) in changes:
                        click.echo(f'{change_type.name}: {file}')
                    sccde.distribute()
                    click.echo('Relocate package file.')
                    click.echo('Please restart Synapse core process in Web-browser window.')
            else:
                while True:
                    time.sleep(0.5)
        except KeyboardInterrupt:
            pass


class WatchFilter(BaseFilter):

    """WatchFilter for watchfiles."""

    extensions: Final[list[str]]  = ['.py', '.so', '.json']

    def __call__(self, _change: Change, path: str) -> bool:
        """Return True if the path is sccde mangement file."""
        if '.synapse' in path:
            return False

        return Path(path).suffix in self.extensions


if __name__ == '__main__':
    cli()
