import io
from utils import to_bytes, from_buf
from value.const import VALUE_TYPE_STRING
from value.value import Value


class ValueString(Value):

    def __init__(self, val: str):
        self.val_type: int = VALUE_TYPE_STRING
        self.val: str = val

    def __bytes__(self) -> bytes:
        r = b''
        r += to_bytes(self.val_type)
        r += to_bytes(self.val)
        return r

    def __eq__(self, other: 'ValueString'):
        return self.val_type == other.val_type and self.val == other.val

    def show(self):
        print(f"ValueString({self.val})", end="")


def new_value_string(val: str):
    r = ValueString(val)
    return r


def new_value_string_from_buf(buf: io.BytesIO):
    val = from_buf(buf, str)
    r = ValueString(val)
    return r


def new_value_string_from_bytes(bytes_: bytes):
    buf = io.BytesIO(bytes_)
    return new_value_string_from_buf(buf)

