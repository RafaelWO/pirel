import logging
import sys
from typing import Optional

import typer
from rich.console import Console

import pirel

from .logging import setup_logging
from .python_cli import get_active_python_info
from .releases import load_releases

if sys.version_info < (3, 9):
    from typing_extensions import Annotated
else:
    from typing import Annotated

RICH_CONSOLE = Console()


app = typer.Typer(name="pirel")
logger = logging.getLogger("pirel")


def logging_callback(ctx: typer.Context, verbosity: int) -> Optional[int]:
    if ctx.resilient_parsing:
        return None

    setup_logging(verbosity)
    return verbosity


def version_callback(value: bool) -> None:
    if value:
        print(f"pirel {pirel.__version__}")
        raise typer.Exit()


VERBOSE_OPTION = Annotated[
    int,
    typer.Option(
        "--verbose",
        "-v",
        help="Enable verbose logging; can be supplied multiple times to increase verbosity.",
        count=True,
        callback=logging_callback,
    ),
]


def print_releases() -> None:
    """Prints all Python releases as a table."""
    py_info = get_active_python_info()
    py_version = py_info.version if py_info else None

    releases = load_releases()
    RICH_CONSOLE.print(releases.to_table(py_version), new_line_start=True)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    verbose: VERBOSE_OPTION = 0,
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            help="Dispay the version of pirel",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """The Python release cycle in your terminal."""
    if not ctx.invoked_subcommand:
        # This hack is for backwards compatibility that "redirects" to the `list`
        # command if no command is passed.
        # This will be removed in a future version.
        logger.warning(
            "Invoking `pirel` without a command is deprecated"
            " and will be removed in a future version."
        )
        logger.warning("Please use `pirel list` instead.")
        print_releases()


@app.command("list")
def list_releases() -> None:
    """Lists all Python releases in a table. Your active Python interpreter is highlighted."""
    print_releases()


@app.command("check")
def check_release() -> None:
    """Shows release information about your active Python interpreter.

    If the active version is end-of-life, the program exits with code 1.
    If no active Python interpreter is found, the program exits with code 2.
    """
    py_info = get_active_python_info()
    if not py_info:
        logger.error(
            "Could not find active Python interpreter in PATH. Try to run with `--verbose`"
        )
        raise typer.Exit(code=2)

    releases = load_releases()
    active_release = releases[py_info.version.as_release]

    RICH_CONSOLE.print(f"\n{active_release}", highlight=False)

    if active_release.is_eol:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()  # pragma: no cover
