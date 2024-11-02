import re
import subprocess
import sys
from dataclasses import dataclass

PYTHON_VERSION_RE = re.compile(r"^Python ([23])\.(\d+)\.(\d+)$")


@dataclass(frozen=True)
class PythonVersion:
    major: int
    minor: int
    patch: int

    @classmethod
    def from_str(cls, version: str) -> "PythonVersion":
        return cls(*map(int, version.split(".")))

    @classmethod
    def this(cls) -> "PythonVersion":
        return cls(*sys.version_info)

    @property
    def as_release(self) -> str:
        return f"{self.major}.{self.minor}"

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __repr__(self) -> str:
        return f"PythonVersion({self.major}.{self.minor}.{self.patch})"


def parse_python_version(python_version_output: str) -> PythonVersion:
    match = PYTHON_VERSION_RE.match(python_version_output)
    if not match:
        raise ValueError(
            f"The Python version output {python_version_output!r} "
            f"does not match the regex {PYTHON_VERSION_RE.pattern!r}"
        )
    major, minor, patch = match.groups()
    return PythonVersion(major, minor, patch)


class PythonCli:
    def __init__(self):
        version_out = None
        for py in ("python", "python3", "python2"):
            try:
                version_out = subprocess.run((py, "--version"), capture_output=True)
                self.version = parse_python_version(version_out.stdout.decode())
                break
            except (FileNotFoundError, ValueError):
                pass

        if version_out is None:
            raise FileNotFoundError("Could not find an active Python interpreter")

        path_out = subprocess.run(
            (py, "-c", "import sys; print(sys.executable)"), capture_output=True
        )

        self.cmd = py
        self.path = path_out.stdout.decode().strip()
