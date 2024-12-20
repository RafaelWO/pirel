from __future__ import annotations

import logging
import re
import subprocess
import sys
from dataclasses import dataclass

PYTHON_VERSION_RE = re.compile(r"Python ([23])\.(\d+)\.(\d+)")
logger = logging.getLogger("pirel")


@dataclass(frozen=True)
class PythonVersion:
    major: int
    minor: int
    patch: int

    @classmethod
    def from_cli(cls, version: str) -> PythonVersion:
        match = PYTHON_VERSION_RE.match(version)
        if not match:
            raise ValueError(
                f"The Python version output {version!r} "
                f"does not match the regex {PYTHON_VERSION_RE.pattern!r}"
            )
        return PythonVersion(*map(int, match.groups()))

    @classmethod
    def this(cls) -> PythonVersion:
        return cls(*sys.version_info[:3])

    @property
    def as_release(self) -> str:
        return f"{self.major}.{self.minor}"

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __repr__(self) -> str:
        return f"PythonVersion({self.major}.{self.minor}.{self.patch})"


@dataclass(frozen=True)
class ActivePythonInfo:
    cmd: str
    path: str
    version: PythonVersion


def get_active_python_info() -> ActivePythonInfo | None:
    version_out = None
    for py_exe in ("python", "python3", "python2"):
        try:
            logger.debug(f"Trying command `{py_exe}`")
            # TODO: Check if there is a better way to inspect the active Python version
            version_out = subprocess.run((py_exe, "--version"), capture_output=True)
            version = PythonVersion.from_cli(version_out.stdout.decode())
            break
        except (FileNotFoundError, ValueError):
            logger.debug(
                f"Failed to get Python version from command {py_exe!r}", exc_info=True
            )

    if version_out is None:
        logger.warning("Could not find an active Python interpreter")
        return None

    path_out = subprocess.run(
        (py_exe, "-c", "import sys; print(sys.executable)"), capture_output=True
    )
    path = path_out.stdout.decode().strip()
    logger.info(f"Found active Python interpreter at {path!r} (command {py_exe!r})")

    return ActivePythonInfo(cmd=py_exe, path=path, version=version)
