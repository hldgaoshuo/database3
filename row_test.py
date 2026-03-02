import pytest
from row import new_row, new_row_from_bytes
from value.value_bool import new_value_bool
from value.value_int import new_value_int
from value.value_string import new_value_string


def test_to_bytes():
    got = bytes(new_row([new_value_int(2), new_value_string("a"), new_value_bool(True)]))
    want = (
        b'\x00\x00\x00\x00\x00\x00\x00\x03' +
        b'\x00\x00\x00\x00\x00\x00\x00\x01' + b'\x00\x00\x00\x00\x00\x00\x00\x02' +
        b'\x00\x00\x00\x00\x00\x00\x00\x02' + b'\x00\x00\x00\x01' + b'a' +
        b'\x00\x00\x00\x00\x00\x00\x00\x03' + b'\x01'
    )
    assert got == want


def test_from_bytes():
    got = new_row_from_bytes(
        b'\x00\x00\x00\x00\x00\x00\x00\x03' +
        b'\x00\x00\x00\x00\x00\x00\x00\x01' + b'\x00\x00\x00\x00\x00\x00\x00\x02' +
        b'\x00\x00\x00\x00\x00\x00\x00\x02' + b'\x00\x00\x00\x01' + b'a' +
        b'\x00\x00\x00\x00\x00\x00\x00\x03' + b'\x01'
    )
    want = new_row([new_value_int(2), new_value_string("a"), new_value_bool(True)])
    assert got == want


def test_lt():
    a = new_row([new_value_int(1), new_value_string("a")])
    b = new_row([new_value_int(2), new_value_string("a")])
    assert bytes(a) < bytes(b)


def test_gt():
    a = new_row([new_value_int(2), new_value_string("a")])
    b = new_row([new_value_int(1), new_value_string("a")])
    assert bytes(a) > bytes(b)


if __name__ == "__main__":
    pytest.main([__file__])

