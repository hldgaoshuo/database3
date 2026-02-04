import pytest
from utils import new_int64
from value.value_int64 import new_value_int64, new_value_int64_from_bytes


def test_to_bytes():
    got = bytes(new_value_int64(new_int64(5)))
    want = b'\x00\x00\x00\x04' + b'\x00\x00\x00\x00\x00\x00\x00\x05'
    assert got == want


def test_from_bytes():
    got = new_value_int64_from_bytes(b'\x00\x00\x00\x00\x00\x00\x00\x05')
    want = new_value_int64(new_int64(5))
    assert got == want


if __name__ == "__main__":
    pytest.main([__file__])
