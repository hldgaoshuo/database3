import pytest
from row import new_row, new_row_from_bytes
from utils import Int64
from value.value_bool import new_value_bool
from value.value_int import new_value_int
from value.value_int64 import new_value_int64
from value.value_string import new_value_string


def test_to_bytes():
    got = bytes(new_row(new_value_int64(Int64(1770118732606)), [new_value_int(2), new_value_string("a"), new_value_bool(True)]))
    want = (
        b'\x00\x00\x00\x04' + b'\x00\x00\x01\x9c#L[>' +
        b'\x00\x00\x00\x03' +
        b'\x00\x00\x00\x01' + b'\x00\x00\x00\x02' +
        b'\x00\x00\x00\x02' + b'\x00\x00\x00\x01' + b'a' +
        b'\x00\x00\x00\x03' + b'\x01'
    )
    assert got == want


def test_from_bytes():
    got = new_row_from_bytes(
        b'\x00\x00\x00\x04' + b'\x00\x00\x01\x9c#L[>' +
        b'\x00\x00\x00\x03' +
        b'\x00\x00\x00\x01' + b'\x00\x00\x00\x02' +
        b'\x00\x00\x00\x02' + b'\x00\x00\x00\x01' + b'a' +
        b'\x00\x00\x00\x03' + b'\x01'
    )
    want = new_row(new_value_int64(Int64(1770118732606)), [new_value_int(2), new_value_string("a"), new_value_bool(True)])
    assert got == want


if __name__ == "__main__":
    pytest.main([__file__])

