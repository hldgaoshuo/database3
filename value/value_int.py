import io
from utils import to_bytes, from_buf
from value.const import VALUE_TYPE_INT
from value.value import Value


class ValueInt(Value):

    def __init__(self):
        self.val_type: int = 0
        self.val: int = 0

    def __bytes__(self) -> bytes:
        r = b''
        r += to_bytes(self.val_type)
        r += to_bytes(self.val)
        return r

    def __eq__(self, other: 'ValueInt'):
        return self.val_type == other.val_type and self.val == other.val

    def show(self):
        print(f"ValueInt({self.val})", end="")


def new_value_int(val: int):
    r = ValueInt()
    r.val_type = VALUE_TYPE_INT
    r.val = val
    return r


def new_value_int_from_buf(buf: io.BytesIO):
    r = ValueInt()
    r.val_type = VALUE_TYPE_INT
    r.val = from_buf(buf, int)
    return r


def new_value_int_from_bytes(bytes_: bytes):
    buf = io.BytesIO(bytes_)
    return new_value_int_from_buf(buf)
