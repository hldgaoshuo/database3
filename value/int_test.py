from value.int import new_int, new_int_from_bytes


def test_to_bytes():
    got = bytes(new_int(2))
    want = b'\x00\x00\x00\x01' + b'\x00\x00\x00\x02'
    assert got == want


def test_from_bytes():
    got = new_int_from_bytes(b'\x00\x00\x00\x02')
    want = new_int(2)
    assert got == want
