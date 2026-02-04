import pytest
from value.value_bool import new_value_bool, new_value_bool_from_bytes


def test_to_bytes():
    got = bytes(new_value_bool(True))
    want = b'\x00\x00\x00\x03' + b'\x01'
    assert got == want


def test_from_bytes():
    got = new_value_bool_from_bytes(b'\x01')
    want = new_value_bool(True)
    assert got == want


if __name__ == "__main__":
    pytest.main([__file__])
