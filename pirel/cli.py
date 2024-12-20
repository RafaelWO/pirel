import logging
import sys
from typing import Optional

import typer
from rich.console import Console

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


# This callback is a hack to "redirect" to the `list` command if no command is passed.
# This will be removed in a future version.
@app.callback(invoke_without_command=True)
def redirect_no_command_to_list(
    ctx: typer.Context,
    verbose: Annotated[int, typer.Option("--verbose", "-v", count=True)] = 0,
) -> None:
    if not ctx.invoked_subcommand:
        setup_logging(verbose)
        logger.warning(
            "Invoking `pirel` without a command is deprecated"
            " and will be removed in a future version."
        )
        logger.warning("Please use `pirel list` instead.")
        print_releases()


@app.command("list")
def list_releases(verbose: VERBOSE_OPTION = 0) -> None:
    """Lists all Python releases in a table. Your active Python interpreter is highlighted."""
    print_releases()


@app.command("check")
def check_release(verbose: VERBOSE_OPTION = 0) -> None:
    """Shows release information about your active Python interpreter.

    If no active Python interpreter is found, the program exits with code 2.
    """
    py_info = get_active_python_info()
    if not py_info:
        logger.error("Could not find active Python interpreter in PATH.")
        raise typer.Exit(code=2)

    releases = load_releases()
    active_release = releases[py_info.version.as_release]

    RICH_CONSOLE.print(f"\n{active_release}", highlight=False)


if __name__ == "__main__":
    app()  # pragma: no cover
