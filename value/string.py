import io
from utils import to_bytes, from_buf
from value.const import VALUE_TYPE_STRING
from value.value import Value


class String(Value):

    def __init__(self, val: str):
        self.val_type: int = VALUE_TYPE_STRING
        self.val: str = val

    def __bytes__(self) -> bytes:
        r = b''
        r += to_bytes(self.val_type)
        r += to_bytes(self.val)
        return r

    def __eq__(self, other: 'String'):
        return self.val_type == other.val_type and self.val == other.val

    def show(self):
        print(f"String({self.val})", end="")


def new_string(val: str):
    r = String(val)
    return r


def new_string_from_buf(buf: io.BytesIO):
    val = from_buf(buf, str)
    r = String(val)
    return r


def new_string_from_bytes(bytes_: bytes):
    buf = io.BytesIO(bytes_)
    return new_string_from_buf(buf)

