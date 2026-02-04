import io
from utils import Int64, to_bytes, from_buf
from value.const import VALUE_TYPE_INT64
from value.value import Value


class ValueInt64(Value):

    def __init__(self, val: Int64):
        self.val_type: int = VALUE_TYPE_INT64
        self.val: Int64 = val

    def __bytes__(self) -> bytes:
        r = b''
        r += to_bytes(self.val_type)
        r += to_bytes(self.val)
        return r

    def __eq__(self, other: 'ValueInt64'):
        return self.val_type == other.val_type and self.val == other.val

    def show(self):
        print(f"ValueInt64({self.val})", end="")


def new_value_int64(val: Int64):
    r = ValueInt64(val)
    return r


def new_value_int64_from_buf(buf: io.BytesIO):
    val = from_buf(buf, Int64)
    r = ValueInt64(val)
    return r


def new_value_int64_from_bytes(bytes_: bytes):
    buf = io.BytesIO(bytes_)
    return new_value_int64_from_buf(buf)
