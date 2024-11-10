import logging
import sys

import typer
from rich.console import Console

from .logging import setup_logging
from .python_cli import get_active_python_info
from .releases import PythonReleases

if sys.version_info < (3, 9):
    from typing_extensions import Annotated
else:
    from typing import Annotated

RICH_CONSOLE = Console()


app = typer.Typer()
logger = logging.getLogger("pirel")


def logging_callback(ctx: typer.Context, verbosity: int):
    if ctx.resilient_parsing:
        return

    setup_logging(verbosity)
    return verbosity


VERBOSE_OPTION = Annotated[
    int, typer.Option("--verbose", "-v", count=True, callback=logging_callback)
]


@app.command()
def releases_table(
    verbose: VERBOSE_OPTION = 0,
):
    """Shows all Python releases. Your active Python interpreter is highlighted."""
    py_info = get_active_python_info()
    py_version = py_info.version if py_info else None

    releases = PythonReleases()
    RICH_CONSOLE.print("", releases.to_table(py_version))


if __name__ == "__main__":
    app()
