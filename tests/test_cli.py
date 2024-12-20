import datetime
import logging
import pathlib
import re
from unittest import mock

import pytest
from rich.console import Console
from typer.testing import CliRunner

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
}


@pytest.fixture(scope="module")
def mock_rich_no_wrap():
    with mock.patch("pirel.cli.RICH_CONSOLE", Console(soft_wrap=True, emoji=False)):
        yield


@pytest.fixture
def mock_release_cycle_file():
    date_freeze = "2024-11-03"
    data_path = (
        pathlib.Path(__file__).parent / "data" / f"release-cycle_{date_freeze}.json"
    )
    with open(data_path) as file:
        with mock.patch("pirel.releases.urllib.request.urlopen") as mock_urlopen:
            # Mock call to release cycle data
            mock_urlopen.return_value.__enter__.return_value = file

            # Mock date for reproducability
            with mock.patch(
                "pirel.releases.DATE_NOW", datetime.date.fromisoformat(date_freeze)
            ):
                yield


@pytest.fixture
def releases_table():
    pyver = PythonVersion.this()
    # Add asterisk to active Python version
    table = re.sub(rf"  {pyver.as_release}", f"* {pyver.as_release}", RELEASES_TABLE)
    return table


@pytest.mark.parametrize("args, log_count", [(None, 2), ("list", 0)])
def test_pirel_list(
    args, log_count, mock_rich_no_wrap, mock_release_cycle_file, releases_table, caplog
):
    caplog.set_level(logging.WARNING)

    # Call CLI
    result = runner.invoke(app, args)
    assert result.exit_code == 0, result.stdout

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


def test_pirel_check(mock_rich_no_wrap, mock_release_cycle_file):
    pyver = PythonVersion.this()

    # Call CLI
    result = runner.invoke(app, "check")
    assert result.exit_code == 0, result.stdout

    # Check output
    output = result.stdout.strip()
    assert output == PYVER_TO_CHECK_OUTPUT[pyver.as_release]


def test_pirel_check_no_interpreter():
    with mock.patch("pirel.cli.get_active_python_info") as m_py_info:
        m_py_info.return_value = None

        # Call CLI
        result = runner.invoke(app, "check")
        assert result.exit_code == 2, result.stdout
