import logging

import typer
from rich.console import Console

from .python_cli import get_active_python_info
from .releases import PythonReleases

RICH_CONSOLE = Console()


app = typer.Typer()
logger = logging.getLogger("pirel")


@app.command()
def releases_table():
    py_info = get_active_python_info()
    py_version = py_info.version if py_info else None

    releases = PythonReleases()
    RICH_CONSOLE.print("", releases.to_table(py_version))


if __name__ == "__main__":
    app()
