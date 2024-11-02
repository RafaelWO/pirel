import datetime
import json
import urllib.request
from typing import Optional

from rich.table import Table
from rich.text import Text

from . import python_cli

DATE_NOW = datetime.date.today()
DATE_NOW_STR = str(DATE_NOW)


def parse_date(date_str: str) -> datetime.date:
    if len(date_str) == len("yyyy-mm"):
        # We need a full yyyy-mm-dd, so let's approximate
        return datetime.date.fromisoformat(date_str + "-01")
    return datetime.date.fromisoformat(date_str)


def date_style(date: datetime.date) -> str:
    """Returns the style for a date for rich table."""
    if date > DATE_NOW:
        # Future, add italics
        return "italic"
    return ""


class PythonRelease:
    def __init__(self, version: str, data: dict):
        self._version = version
        self._status = data["status"]
        self._released = parse_date(data["first_release"])
        self._end_of_life = parse_date(data["end_of_life"])

    @property
    def version(self) -> str:
        return self._version

    @property
    def status(self) -> Text:
        _status = Text(self._status)
        if _status.plain == "end-of-life":
            _status.stylize("red")
        elif _status.plain == "security":
            _status.stylize("yellow")
        elif _status.plain == "bugfix":
            _status.stylize("green")
        elif _status.plain == "prerelease":
            _status.stylize("blue")
        elif _status.plain == "feature":
            _status.stylize("magenta")
        return _status

    @property
    def released(self):
        _released = Text(str(self._released), style=date_style(self._released))
        return _released

    @property
    def end_of_life(self):
        font_style = date_style(self._end_of_life)
        if self._status == "end-of-life":
            color = "red"
        elif datetime.timedelta(days=30 * 2) + DATE_NOW > self._end_of_life:
            color = "dark_orange"
        elif datetime.timedelta(days=365) + DATE_NOW > self._end_of_life:
            color = "yellow"
        else:
            color = "green"

        eol = Text(str(self._end_of_life), style=f"{font_style} {color}")
        return eol


class PythonReleases:
    def __init__(self) -> None:
        with urllib.request.urlopen(
            "https://raw.githubusercontent.com/python/devguide/refs/heads/main/include/release-cycle.json"
        ) as f:
            self.releases_data = json.load(f)

        self.releases = [
            PythonRelease(version, data) for version, data in self.releases_data.items()
        ]

    def to_table(
        self, active_python_version: Optional[python_cli.PythonVersion] = None
    ) -> Table:
        table = Table(title="Python Releases")

        table.add_column("Version", justify="right", style="cyan", no_wrap=True)
        table.add_column("Status", justify="right", no_wrap=True)
        table.add_column(
            "Released", justify="right", style="bright_black", no_wrap=True
        )
        table.add_column("End-of-life", justify="right", no_wrap=True)

        for release in self.releases:
            row_style = None
            _version = release.version
            if (
                active_python_version
                and active_python_version.as_release == release.version
            ):
                _version = f"* [bold]{release.version}[/bold]"
                row_style = "bold"

            table.add_row(
                _version,
                release.status,
                release.released,
                release.end_of_life,
                style=row_style,
            )

        return table


if __name__ == "__main__":
    from rich.console import Console

    txt = Text("foo", style="italic dark_orange")
    Console().print(txt)
