import pytest
from value.value_int import new_value_int, new_value_int_from_bytes


def test_to_bytes():
    got = bytes(new_value_int(2))
    want = b'\x00\x00\x00\x01' + b'\x00\x00\x00\x02'
    assert got == want


def test_from_bytes():
    got = new_value_int_from_bytes(b'\x00\x00\x00\x02')
    want = new_value_int(2)
    assert got == want


if __name__ == "__main__":
    pytest.main([__file__])
