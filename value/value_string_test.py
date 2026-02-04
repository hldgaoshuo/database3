import pytest
from value.value_string import new_value_string, new_value_string_from_bytes


def test_to_bytes():
    got = bytes(new_value_string("a"))
    want = b'\x00\x00\x00\x02' + b'\x00\x00\x00\x01' + b'a'
    assert got == want


def test_from_bytes():
    got = new_value_string_from_bytes(b'\x00\x00\x00\x01' + b'a')
    want = new_value_string("a")
    assert got == want


if __name__ == "__main__":
    pytest.main([__file__])
