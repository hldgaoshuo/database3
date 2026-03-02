import io
from utils import to_bytes, from_buf
from value.value_bool import new_value_bool_from_buf
from value.const import VALUE_TYPE_INT, VALUE_TYPE_STRING, VALUE_TYPE_BOOL
from value.value_int import new_value_int_from_buf
from value.value_string import new_value_string_from_buf
from value.value import Value


class Row:

    def __init__(self):
        self.vals: list[Value] = []
        self.vals_iter = iter(self.vals)

    def __bytes__(self):
        r = b''
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

    def __iter__(self):
        return self.vals_iter

    def __next__(self):
        return next(self.vals_iter)

    def show(self):
        print()
        for val in self.vals:
            val.show()
            print(" ", end="")

    def add(self, val: Value):
        self.vals.append(val)


def new_row(vals: list[Value]):
    r = Row()
    r.vals = vals
    r.vals_iter = iter(r.vals)
    return r


def new_row_from_buf(buf: io.BytesIO) -> Row:
    r = Row()
    num_vals = from_buf(buf, int)
    vals = []
    for _ in range(num_vals):
        val_type = from_buf(buf, int)
        if val_type == VALUE_TYPE_INT:
            val = new_value_int_from_buf(buf)
            vals.append(val)
        elif val_type == VALUE_TYPE_STRING:
            val = new_value_string_from_buf(buf)
            vals.append(val)
        elif val_type == VALUE_TYPE_BOOL:
            val = new_value_bool_from_buf(buf)
            vals.append(val)
        else:
            raise ValueError("未知数据类型")
    r.vals = vals
    r.vals_iter = iter(r.vals)
    return r


def new_row_from_bytes(bytes_: bytes):
    buf = io.BytesIO(bytes_)
    return new_row_from_buf(buf)
