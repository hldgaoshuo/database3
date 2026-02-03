import io


class Int64:

    def __init__(self, val: int):
        self.val: int = val

    def __bytes__(self):
        r = self.val.to_bytes(length=8, byteorder="big", signed=True)
        return r


def new_int64(val: int) -> Int64:
    r = Int64(val)
    return r


def new_int64_from_buf(buf: io.BytesIO) -> Int64:
    bs = buf.read(8)
    r = int.from_bytes(bytes=bs, byteorder="big", signed=True)
    return Int64(r)


def to_bytes(value: int | bool | bytes | str | Int64) -> bytes:
    if type(value) is int:
        return value.to_bytes(length=4, byteorder="big", signed=True)
    elif type(value) is bool:
        return value.to_bytes(length=1, byteorder="big")
    elif type(value) is bytes:
        length = len(value).to_bytes(length=4, byteorder="big")
        return length + value
    elif type(value) is str:
        value_bs = value.encode("utf-8")
        length_bs = len(value_bs).to_bytes(length=4, byteorder="big")
        return length_bs + value_bs
    elif type(value) is Int64:
        return bytes(value)
    else:
        raise ValueError(f"to_bytes() 不支持 {type(value)} 类型")


def from_buf(buf: io.BytesIO, type_: type) -> int | bool | bytes | str | Int64:
    if type_ is int:
        bs = buf.read(4)
        return int.from_bytes(bytes=bs, byteorder="big", signed=True)
    elif type_ is bool:
        bs = buf.read(1)
        return bool.from_bytes(bytes=bs, byteorder="big")
    elif type_ is bytes:
        length_bs = buf.read(4)
        length = int.from_bytes(bytes=length_bs, byteorder="big")
        value = buf.read(length)
        return value
    elif type_ is str:
        length_bs = buf.read(4)
        length = int.from_bytes(bytes=length_bs, byteorder="big")
        value_bs = buf.read(length)
        return value_bs.decode("utf-8")
    elif type_ is Int64:
        return new_int64_from_buf(buf)
    else:
        raise ValueError(f"from_xxx() 不支持 {type_} 类型")


def from_bytes(bytes_: bytes, type_: type) -> int | bool | bytes | str:
    buf = io.BytesIO(bytes_)
    return from_buf(buf, type_)
