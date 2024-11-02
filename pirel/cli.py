import logging

import typer
from rich.console import Console

from . import python_cli
from .releases import PythonReleases

RICH_CONSOLE = Console()


app = typer.Typer()
logger = logging.getLogger("pirel")


@app.callback(invoke_without_command=True)
def releases_table():
    try:
        py_cli = python_cli.PythonCli()
        logger.info(f"Found interpreter at {py_cli.path!r} (via {py_cli.cmd!r})")
        py_version = py_cli.version
    except FileNotFoundError:
        logger.warning("Could not find an active Python interpreter")
        py_version = None

    releases = PythonReleases()
    RICH_CONSOLE.print("", releases.to_table(py_version))


if __name__ == "__main__":
    app()
