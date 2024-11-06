import pathlib
import re
from unittest import mock

import pytest
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


@pytest.fixture
def release_cycle_file():
    data_path = pathlib.Path(__file__).parent / "data" / "release-cycle_2024-11-03.json"
    with open(data_path) as file:
        yield file


@pytest.fixture
def releases_table():
    pyver = PythonVersion.this()
    # Add asterisk to active Python version
    table = re.sub(rf"  {pyver.as_release}", f"* {pyver.as_release}", RELEASES_TABLE)
    return table


def test_app(release_cycle_file, releases_table):
    with mock.patch("pirel.releases.urllib.request.urlopen") as mock_urlopen:
        # Mock call to release cycle data
        mock_urlopen.return_value.__enter__.return_value = release_cycle_file

        # Call CLI
        result = runner.invoke(app)
        assert result.exit_code == 0, result.stdout

        # Check output
        output = result.stdout.strip()
        heading, *table = output.splitlines()
        table = "\n".join(table)

        assert heading.strip() == "Python Releases"
        assert table.strip() == releases_table
