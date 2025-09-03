import pytest

from libdc3.units import UNIT_PREFIXES


def test_unit_prefixes_content():
    assert "/fb" in UNIT_PREFIXES
    assert UNIT_PREFIXES["/fb"] == 10**-15

    with pytest.raises(KeyError):
        UNIT_PREFIXES["fb"]
