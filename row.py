import io
from utils import to_bytes, from_buf
from value.bool import new_bool_from_buf
from value.const import VALUE_TYPE_INT, VALUE_TYPE_STRING, VALUE_TYPE_BOOL
from value.int import new_int_from_buf
from value.string import new_string_from_buf
from value.value import Value


class Row:

    def __init__(self, oid: int, vals: list[Value]):
        self.oid: int = oid
        self.vals: list[Value] = vals

    def __bytes__(self):
        r = b''
        r += to_bytes(self.oid)
        r += to_bytes(len(self.vals))
        for val in self.vals:
            r += bytes(val)
        return r

    def __eq__(self, other: 'Row'):
        if len(self.vals) != len(other.vals):
            return False
        for i, val in enumerate(self.vals):
            if val != other.vals[i]:
                return False
        return True

    def show(self):
        print()
        for val in self.vals:
            val.show()
            print(" ", end="")


def new_row(oid: int, vals: list[Value]):
    r = Row(oid, vals)
    return r


def new_row_from_buf(buf: io.BytesIO) -> Row:
    oid = from_buf(buf, int)
    num_vals = from_buf(buf, int)
    vals = []
    for _ in range(num_vals):
        val_type = from_buf(buf, int)
        if val_type == VALUE_TYPE_INT:
            val = new_int_from_buf(buf)
            vals.append(val)
        elif val_type == VALUE_TYPE_STRING:
            val = new_string_from_buf(buf)
            vals.append(val)
        elif val_type == VALUE_TYPE_BOOL:
            val = new_bool_from_buf(buf)
            vals.append(val)
        else:
            raise ValueError("未知数据类型")
    row = Row(oid, vals)
    return row


def new_row_from_bytes(bytes_: bytes):
    buf = io.BytesIO(bytes_)
    return new_row_from_buf(buf)
