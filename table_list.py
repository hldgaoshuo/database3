from b_plus_tree import BPlusTree
from utils import to_bytes


class Table:

    def __init__(self, name: str, col_names: list[str], col_types: list[int], b_plus_tree: BPlusTree):
        self.name: str = name
        self.col_names: list[str] = col_names
        self.col_types: list[int] = col_types
        self.b_plus_tree: BPlusTree = b_plus_tree

    def __bytes__(self):
        r = b''
        r += to_bytes(self.name)
        r += to_bytes(len(self.col_names))
        for col_name in self.col_names:
            r += to_bytes(col_name)
        for col_type in self.col_types:
            r += to_bytes(col_type)
        r += to_bytes(self.b_plus_tree.root.page_id)
        return r


class TableListNode:

    def __init__(self):
        pass


class TableList:

    def __init__(self):
        pass
