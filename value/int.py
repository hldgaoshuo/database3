import io
from utils import to_bytes, from_buf
from value.const import VALUE_TYPE_INT
from value.value import Value


class Int(Value):

    def __init__(self, val: int):
        self.val_type: int = VALUE_TYPE_INT
        self.val: int = val

    def __bytes__(self) -> bytes:
        r = b''
        r += to_bytes(self.val_type)
        r += to_bytes(self.val)
        return r

    def __eq__(self, other: 'Int'):
        return self.val_type == other.val_type and self.val == other.val


def new_int(val: int):
    r = Int(val)
    return r


def new_int_from_buf(buf: io.BytesIO):
    val = from_buf(buf, int)
    r = Int(val)
    return r


def new_int_from_bytes(bytes_: bytes):
    buf = io.BytesIO(bytes_)
    return new_int_from_buf(buf)
