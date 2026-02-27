import io
from utils import to_bytes, from_buf
from value.const import VALUE_TYPE_BOOL
from value.value import Value


class ValueBool(Value):

    def __init__(self):
        self.val_type: int = 0
        self.val: bool = False

    def __bytes__(self) -> bytes:
        r = b''
        r += to_bytes(self.val_type)
        r += to_bytes(self.val)
        return r

    def __eq__(self, other: 'ValueBool'):
        return self.val_type == other.val_type and self.val == other.val

    def __repr__(self):
        return f"ValueBool({self.val_type, self.val})"
    
    def show(self):
        print(f"ValueBool({self.val})", end="")
        

def new_value_bool(val: bool):
    r = ValueBool()
    r.val_type = VALUE_TYPE_BOOL
    r.val = val
    return r


def new_value_bool_from_buf(buf: io.BytesIO):
    r = ValueBool()
    r.val_type = VALUE_TYPE_BOOL
    r.val = from_buf(buf, bool)
    return r


def new_value_bool_from_bytes(bytes_: bytes):
    buf = io.BytesIO(bytes_)
    return new_value_bool_from_buf(buf)
