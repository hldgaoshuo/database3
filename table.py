import io
from pager import Pager
from free_list import FreeList
from b_plus_tree import BPlusTree, new_b_plus_tree
from utils import to_bytes, from_buf


class Table:

    def __init__(self):
        self.name: str = ""
        self.col_names: list[str] = []
        self.col_types: list[int] = []
        self.data: BPlusTree | None = None
        self.indexes: dict[tuple, BPlusTree] = {}  # key: (col_index, col_index...)

    def __bytes__(self):
        r = b''
        r += to_bytes(self.name)
        r += to_bytes(len(self.col_names))
        for col_name in self.col_names:
            r += to_bytes(col_name)
        for col_type in self.col_types:
            r += to_bytes(col_type)
        r += to_bytes(self.data.seq)
        r += to_bytes(len(self.indexes))
        for index, tree in self.indexes.items():
            r += to_bytes(len(index))
            for col_index in index:
                r += to_bytes(col_index)
            r += to_bytes(tree.seq)
        return r


def new_table(name: str, col_names: list[str], col_types: list[int], pager: Pager, free_list: FreeList, data_seq: int) -> Table:
    r = Table()
    r.name = name
    r.col_names = col_names
    r.col_types = col_types
    r.data = new_b_plus_tree(pager, free_list, data_seq, True)
    r.indexes = {}
    return r


def new_table_from_buf(buf: io.BytesIO, pager: Pager, free_list: FreeList) -> Table:
    r = Table()
    r.name = from_buf(buf, str)
    num_cols = from_buf(buf, int)
    r.col_names = [from_buf(buf, str) for _ in range(num_cols)]
    r.col_types = [from_buf(buf, int) for _ in range(num_cols)]
    data_seq = from_buf(buf, int)
    r.data = new_b_plus_tree(pager, free_list, data_seq, False)
    num_indexes = from_buf(buf, int)
    indexes = {}
    for _ in range(num_indexes):
        num_index_cols = from_buf(buf, int)
        index = tuple(from_buf(buf, int) for _ in range(num_index_cols))
        index_seq = from_buf(buf, int)
        indexes[index] = new_b_plus_tree(pager, free_list, index_seq, False)
    r.indexes = indexes
    return r


def new_table_from_bytes(bytes_: bytes, pager: Pager, free_list: FreeList) -> Table:
    buf = io.BytesIO(bytes_)
    return new_table_from_buf(buf, pager, free_list)
