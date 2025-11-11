from __future__ import annotations

import csv
import datetime
import inspect
import io
import logging
import pathlib
import re
import shutil
import sys
import traceback
from unittest import mock

import click.testing
import pytest
from freezegun import freeze_time
from rich.console import Console
from typer.testing import CliRunner

import pirel
from pirel import _guess
from pirel.cli import app
from pirel.python_cli import PythonVersion

runner = CliRunner()
RELEASES_TABLE = """
┏━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Version ┃      Status ┃   Released ┃ End-of-life ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│    3.14 │     feature │ 2025-10-01 │  2030-10-01 │
│    3.13 │      bugfix │ 2024-10-07 │  2029-10-01 │
│    3.12 │      bugfix │ 2023-10-02 │  2028-10-01 │
│    3.11 │    security │ 2022-10-24 │  2027-10-01 │
│    3.10 │    security │ 2021-10-04 │  2026-10-01 │
│     3.9 │    security │ 2020-10-05 │  2025-10-01 │
│     3.8 │ end-of-life │ 2019-10-14 │  2024-10-07 │
│     3.7 │ end-of-life │ 2018-06-27 │  2023-06-27 │
│     3.6 │ end-of-life │ 2016-12-23 │  2021-12-23 │
│     3.5 │ end-of-life │ 2015-09-13 │  2020-09-30 │
│     3.4 │ end-of-life │ 2014-03-16 │  2019-03-18 │
│     3.3 │ end-of-life │ 2012-09-29 │  2017-09-29 │
│     3.2 │ end-of-life │ 2011-02-20 │  2016-02-20 │
│     2.7 │ end-of-life │ 2010-07-03 │  2020-01-01 │
│     3.1 │ end-of-life │ 2009-06-27 │  2012-04-09 │
│     3.0 │ end-of-life │ 2008-12-03 │  2009-06-27 │
│     2.6 │ end-of-life │ 2008-10-01 │  2013-10-29 │
└─────────┴─────────────┴────────────┴─────────────┘
""".strip()

PYVER_TO_CHECK_OUTPUT = {
    "3.8": ":warning: You are using Python 3.8 which has reached end-of-life! Please upgrade to a newer version of Python (EOL 2024-10-07)",
    "3.9": ":heavy_check_mark: You are using Python 3.9 which has security support for more than 10 months (EOL 2025-10-01)",
    "3.10": ":heavy_check_mark: You are using Python 3.10 which has security support for more than 1 year, 10 months (EOL 2026-10-01)",
    "3.11": ":heavy_check_mark: You are using Python 3.11 which has security support for more than 2 years (EOL 2027-10-01)",
    "3.12": ":rocket: You are using Python 3.12 which is actively maintained (bugfixes) and has security support for more than 3 years (EOL 2028-10-01)",
    "3.13": ":rocket: You are using Python 3.13 which is actively maintained (bugfixes) and has security support for more than 4 years (EOL 2029-10-01)",
    "3.14": ":sparkles: You are using Python 3.14 which is not released yet and still accepts new features (EOL 2030-10-01)",
}
DATE_FREEZE = datetime.date(2024, 11, 3)
RELEASE_CYCLE_DATA_PATH = (
    pathlib.Path(__file__).parent / "data" / f"release-cycle_{DATE_FREEZE}.json"
)
QUESTION_CLASSES: list[type[_guess.Question]] = [
    obj
    for _, obj in inspect.getmembers(sys.modules["pirel._guess"], inspect.isclass)
    if issubclass(obj, _guess.Question) and obj != _guess.Question
]


@pytest.fixture(scope="session")
def mock_time():
    with mock.patch("pirel.releases.DATE_NOW", DATE_FREEZE), freeze_time(DATE_FREEZE):
        yield


@pytest.fixture(autouse=True)
def mock_context():
    # Recreate Pirel Context to ensure that data is loaded on every test
    context = pirel.PirelContext()
    # Disable wrapping line breaks and emojis during tests
    context.rich_console = Console(soft_wrap=True, emoji=False)
    with mock.patch("pirel.CONTEXT", context):
        yield context


@pytest.fixture(
    params=[
        # cache file name, validity
        (None, False),
        (f"{DATE_FREEZE}_release-cycle.json", True),
        (f"{DATE_FREEZE - datetime.timedelta(days=10)}_release-cycle.json", False),
    ],
    ids=["no_cache", "valid_cache", "old_cache"],
)
def cache_file(request, tmp_path):
    cache_dir = tmp_path / "pirel"
    cache_file_name, is_valid = request.param
    if cache_file_name:
        cache_dir.mkdir()
        _cache_file = shutil.copyfile(
            RELEASE_CYCLE_DATA_PATH, cache_dir / cache_file_name
        )

    with mock.patch("pirel._cache.CACHE_DIR", cache_dir):
        yield _cache_file if cache_file_name else None, is_valid


@pytest.fixture
def stats_dir(tmp_path):
    stats_dir = tmp_path / "pirel"
    with mock.patch("pirel._guess.STATS_DIR", stats_dir):
        yield stats_dir


class MockRemoteReleasesFile:
    def __enter__(self):
        self.file_handle = RELEASE_CYCLE_DATA_PATH.open()
        return self.file_handle

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file_handle.close()


@pytest.fixture
def mock_release_cycle_file(mock_time, cache_file):
    # Mock date for reproducability
    with mock.patch("pirel.releases.DATE_NOW", DATE_FREEZE):
        with mock.patch("pirel.releases.urllib.request.urlopen") as mock_urlopen:
            # Mock call to release cycle data
            mock_urlopen.return_value = MockRemoteReleasesFile()

            yield mock_urlopen, cache_file[1]


@pytest.fixture
def releases_table():
    pyver = PythonVersion.this()
    # Add asterisk to active Python version
    table = re.sub(rf"  {pyver.as_release}", f"* {pyver.as_release}", RELEASES_TABLE)
    return table


@pytest.fixture(
    params=[tuple(), ("--no-cache",)], ids=lambda x: ",".join(x) if x else "none"
)
def global_cli_args(request):
    return request.param


@pytest.fixture(params=QUESTION_CLASSES)
def question(request) -> _guess.Question:
    question = request.param(pirel.CONTEXT.releases.to_list())
    return question


def check_exit_code(result: click.testing.Result, code: int = 0):
    """
    Helper to check the exit code of a typer/click app and inlcude the traceback if any.
    """
    assert result.exit_code == code, "\n".join(
        [result.stdout, *traceback.format_exception(*result.exc_info)]
    )


@pytest.mark.parametrize(
    "args, log_count", [(None, 2), ("list", 0)], ids=["root", "list"]
)
def test_pirel_list(
    args,
    log_count,
    mock_release_cycle_file,
    releases_table,
    global_cli_args,
    caplog,
):
    caplog.set_level(logging.WARNING)
    mock_urlopen, is_cache_valid = mock_release_cycle_file

    # Call CLI
    _args = [*global_cli_args]
    if args:
        _args.append(args)
    result = runner.invoke(app, _args)
    check_exit_code(result)

    # Check output
    output = result.stdout.strip()
    heading, *table = output.splitlines()
    table = "\n".join(table)

    assert heading.strip() == "Python Releases"
    assert table.strip() == releases_table

    logs = caplog.messages
    assert len(logs) == log_count
    # If called without args, check that the warning is emitted
    if args is None:
        assert logs[-1] == "Please use `pirel list` instead."

    if is_cache_valid and "--no-cache" not in _args:
        mock_urlopen.assert_not_called()
    else:
        mock_urlopen.assert_called_once()


def test_pirel_check(mock_release_cycle_file, global_cli_args):
    mock_urlopen, is_cache_valid = mock_release_cycle_file
    pyver = PythonVersion.this()
    expected_exit_code = (
        1 if "end-of-life" in PYVER_TO_CHECK_OUTPUT[pyver.as_release] else 0
    )

    # Call CLI
    _args = [*global_cli_args, "check"]
    result = runner.invoke(app, _args)
    check_exit_code(result, code=expected_exit_code)

    # Check output
    output = result.stdout.strip()
    assert output == PYVER_TO_CHECK_OUTPUT[pyver.as_release]

    if is_cache_valid and "--no-cache" not in _args:
        mock_urlopen.assert_not_called()
    else:
        mock_urlopen.assert_called_once()


def test_pirel_check_no_interpreter():
    with mock.patch("pirel.cli.get_active_python_info") as m_py_info:
        m_py_info.return_value = None

        # Call CLI
        result = runner.invoke(app, "check")
        check_exit_code(result, code=2)


def test_pirel_version():
    result = runner.invoke(app, "--version")
    check_exit_code(result)

    assert result.stdout.strip() == f"pirel {pirel.__version__}"


@pytest.mark.parametrize(
    "correct, idx_answer",
    [(True, True), (True, False), (False, True), (False, False)],
    ids=[
        "correct-idx_answer",
        "correct-full_answer",
        "wrong-idx_answer",
        "wrong-full_answer",
    ],
)
def test_pirel_guess(
    correct: bool,  # answer with correct or wrong answer
    idx_answer: bool,  # answer with the index (a, b, etc.) or the name of the answer
    question,
    mock_release_cycle_file,
    stats_dir: pathlib.Path,
):
    # Setup expected values
    choice_enum = "abcd"
    if correct:
        user_response = question.correct_answer
        question_response = f"{question.correct_answer} is correct!"
    else:
        user_response = next(
            c for c in question.choices if c != question.correct_answer
        )
        question_response = (
            f"{user_response} is wrong! (Correct answer: {question.correct_answer})"
        )
    if idx_answer:
        q_idx = question.choices.index(user_response)
        user_response = choice_enum[q_idx]

    _input = f"foo\n{user_response}"
    choices = "\n".join(f" {i}) {c}" for i, c in zip(choice_enum, question.choices))
    full_question = (
        f"{question.format_question()}\n{choices}{_guess.PirelPrompt.prompt_suffix}"
    )
    expected_out = f"{full_question}Please select one of the available options or indices (a, b, etc.)\n{full_question}{question_response}"

    # Mock stream for user prompt
    with mock.patch("pirel._guess.PirelPrompt.stream", io.StringIO(_input)):
        with mock.patch("pirel._guess.get_random_question") as m_question:
            m_question.return_value = question
            # Call CLI
            result = runner.invoke(app, "guess")
            check_exit_code(result, code=0)

            assert result.stdout.strip() == expected_out

    # Checks stats
    stats_file = stats_dir / _guess.STATS_FILENAME
    assert stats_file.exists()
    expected_stats = {
        "time": datetime.datetime.now().isoformat(),
        "question_cls": question.__class__.__name__,
        "target_release": question.target_release.version,
        "score": int(correct),
    }
    with stats_file.open(newline="") as file:
        reader = csv.DictReader(file, quoting=csv.QUOTE_NONNUMERIC)
        data = [row for row in reader]

    assert len(data) == 1
    assert data[0] == expected_stats
