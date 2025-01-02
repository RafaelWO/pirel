from __future__ import annotations

import datetime
import json
import pathlib
from typing import Any, Dict, Optional, cast

import platformdirs

CACHE_DIR = platformdirs.user_cache_path("pirel")
CACHE_FILE_GLOB = "*_release-cycle.json"


def filename() -> str:
    """The name of today's cache file."""
    return f"{datetime.date.today().isoformat()}_release-cycle.json"


def clear(clear_all: bool = False) -> None:
    """Delete old or all cache files."""
    for cache_file in CACHE_DIR.glob(CACHE_FILE_GLOB):
        if clear_all or not cache_file.name == filename():
            cache_file.unlink()


def save(data: dict[str, Any]) -> None:
    """Save data to new cache file."""
    cache_file = CACHE_DIR / filename()
    if not CACHE_DIR.exists():
        CACHE_DIR.mkdir(parents=True)

    with cache_file.open("w") as file:
        json.dump(data, file)

    # Delete old cache
    clear()


def get_latest_cache_file() -> Optional[pathlib.Path]:
    """Returns the path to the latest cache file `None` if no cache exists."""
    return max(CACHE_DIR.glob(CACHE_FILE_GLOB), default=None)


def calc_cache_age_days(cache_file: pathlib.Path) -> int:
    """Returns the age of the cache in days."""
    cache_date = datetime.date.fromisoformat(cache_file.name.split("_")[0])
    return (datetime.date.today() - cache_date).days


def load(cache_file: pathlib.Path) -> dict[str, Any]:
    """Loads the data from a cache file path."""
    with cache_file.open() as file:
        return cast(Dict[str, Any], json.load(file))
