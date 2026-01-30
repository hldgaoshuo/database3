from value.bool import new_bool, new_bool_from_bytes


def test_to_bytes():
    got = bytes(new_bool(True))
    want = b'\x00\x00\x00\x03' + b'\x01'
    assert got == want


def test_from_bytes():
    got = new_bool_from_bytes(b'\x01')
    want = new_bool(True)
    assert got == want
