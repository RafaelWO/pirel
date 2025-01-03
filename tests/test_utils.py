from __future__ import annotations

import pytest

from pirel._utils import VersionLike


@pytest.mark.parametrize(
    "a, b, cmp, expected",
    [
        [(3, 8), (3, 7, 6), "==", False],
        [(3, 8), (3, 7, 6), "<", False],
        [(3, 8), (3, 7, 6), "<=", False],
        [(3, 8), (3, 7, 6), ">", True],
        [(3, 8), (3, 7, 6), ">=", True],
    ],
)
def test_version_comparison(a, b, cmp, expected):
    class AVersion(VersionLike):
        @property
        def version_tuple(self) -> tuple[int, ...]:
            return a

    class BVersion(VersionLike):
        @property
        def version_tuple(self) -> tuple[int, ...]:
            return b

    obj_a = AVersion()
    obj_b = BVersion()
    assert eval(f"obj_a {cmp} obj_b", {"obj_a": obj_a, "obj_b": obj_b}) == expected
