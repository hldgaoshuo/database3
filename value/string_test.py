from value.string import new_string, new_string_from_bytes


def test_to_bytes():
    got = bytes(new_string("a"))
    want = b'\x00\x00\x00\x02' + b'\x00\x00\x00\x01' + b'a'
    assert got == want


def test_from_bytes():
    got = new_string_from_bytes(b'\x00\x00\x00\x01' + b'a')
    want = new_string("a")
    assert got == want
