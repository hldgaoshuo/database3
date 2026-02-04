import io
from utils import to_bytes, from_buf
from value.const import VALUE_TYPE_BOOL
from value.value import Value


class ValueBool(Value):

    def __init__(self, val: bool):
        self.val_type: int = VALUE_TYPE_BOOL
        self.val: bool = val

    def __bytes__(self) -> bytes:
        r = b''
        r += to_bytes(self.val_type)
        r += to_bytes(self.val)
        return r

    def __eq__(self, other: 'ValueBool'):
        return self.val_type == other.val_type and self.val == other.val
    
    def show(self):
        print(f"ValueBool({self.val})", end="")
        

def new_value_bool(val: bool):
    r = ValueBool(val)
    return r


def new_value_bool_from_buf(buf: io.BytesIO):
    val = from_buf(buf, bool)
    r = ValueBool(val)
    return r


def new_value_bool_from_bytes(bytes_: bytes):
    buf = io.BytesIO(bytes_)
    return new_value_bool_from_buf(buf)
