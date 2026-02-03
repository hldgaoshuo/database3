import pytest
from oid import get_oid
from row import new_row, new_row_from_bytes
from utils import Int64
from value.bool import new_bool
from value.int import new_int
from value.string import new_string


def test_to_bytes():
    got = bytes(new_row(Int64(1770118732606), [new_int(2), new_string("a"), new_bool(True)]))
    want = (
        b'\x00\x00\x01\x9c#L[>' +
        b'\x00\x00\x00\x03' +
        b'\x00\x00\x00\x01' + b'\x00\x00\x00\x02' +
        b'\x00\x00\x00\x02' + b'\x00\x00\x00\x01' + b'a' +
        b'\x00\x00\x00\x03' + b'\x01'
    )
    assert got == want


def test_from_bytes():
    got = new_row_from_bytes(
        b'\x00\x00\x01\x9c#L[>' +
        b'\x00\x00\x00\x03' +
        b'\x00\x00\x00\x01' + b'\x00\x00\x00\x02' +
        b'\x00\x00\x00\x02' + b'\x00\x00\x00\x01' + b'a' +
        b'\x00\x00\x00\x03' + b'\x01'
    )
    want = new_row(Int64(1770118732606), [new_int(2), new_string("a"), new_bool(True)])
    assert got == want


if __name__ == "__main__":
    pytest.main([__file__])

