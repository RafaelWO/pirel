import logging
from typing import Annotated, Optional

import typer

import pirel

from . import _cache, _guess
from .logging import setup_logging
from .python_cli import get_active_python_info

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

    pirel.CONTEXT.rich_console.print(
        pirel.CONTEXT.releases.to_table(py_version), new_line_start=True
    )


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    no_cache: Annotated[
        Optional[bool],
        typer.Option("--no-cache", help="Clear cache before running"),
    ] = None,
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
    if no_cache:
        _cache.clear(clear_all=True)

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

    active_release = pirel.CONTEXT.releases[py_info.version.as_release]

    pirel.CONTEXT.rich_console.print(f"\n{active_release}")

    if active_release.is_eol:
        raise typer.Exit(code=1)


@app.command("guess")
def ask_random_question() -> None:
    """Prompts the user with a random question regarding Python releases.

    For example, "When was Python 3.9 released?" or "Who was the release manager for
    Python 3.6?".

    The history is stored in the user data directory.
    """
    question = _guess.get_random_question()
    score = int(question.ask())
    _guess.store_question_score(question, score)


if __name__ == "__main__":
    app()  # pragma: no cover
