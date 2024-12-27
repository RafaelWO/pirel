from __future__ import annotations

import abc


class VersionLike(abc.ABC):
    """Abstract class for objects that hold a version (`tuple` of `int`s) and
    should be comparible based on their version.
    """

    @property
    @abc.abstractmethod
    def version_tuple(self) -> tuple[int, ...]:
        pass

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VersionLike):
            return NotImplemented
        return self.version_tuple == other.version_tuple

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, VersionLike):
            return NotImplemented
        return self.version_tuple < other.version_tuple

    def __le__(self, other: object) -> bool:
        if not isinstance(other, VersionLike):
            return NotImplemented
        return self.version_tuple <= other.version_tuple

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, VersionLike):
            return NotImplemented
        return self.version_tuple > other.version_tuple

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, VersionLike):
            return NotImplemented
        return self.version_tuple >= other.version_tuple
