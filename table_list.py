import io

from b_plus_tree import BPlusTree, new_b_plus_tree, new_b_plus_tree_from_root_page_id
from const import NUM_TABLE, NULL_PAGE_ID
from free_list import FreeList
from pager import Pager
from row import new_row_from_bytes, Row
from value.value import Value
from utils import to_bytes, from_buf


class TableSeqGenerator:
    def __init__(self, pager: Pager, init_seq: int):
        self.pager: Pager = pager
        self.next_seq: int = init_seq

    def get_next_seq(self):
        r = self.next_seq
        self.next_seq += 1
        self.pager.table_seq_set(self.next_seq)
        return r


def new_table_seq_generator(pager: Pager, init_seq: int):
    return TableSeqGenerator(pager, init_seq)


class Table:

    def __init__(self, name: str, seq: int, col_names: list[str], col_types: list[int], b_plus_tree: BPlusTree):
        self.name: str = name
        self.seq: int = seq
        self.col_names: list[str] = col_names
        self.col_types: list[int] = col_types
        self.b_plus_tree: BPlusTree = b_plus_tree

    def __bytes__(self):
        r = b''
        r += to_bytes(self.name)
        r += to_bytes(self.seq)
        r += to_bytes(len(self.col_names))
        for col_name in self.col_names:
            r += to_bytes(col_name)
        for col_type in self.col_types:
            r += to_bytes(col_type)
        return r

    def set(self, key: Value, row: Row):
        _key = bytes(key)
        _row = bytes(row)
        self.b_plus_tree[_key] = _row

    def get(self, key: Value) -> Row:
        _key = bytes(key)
        val = self.b_plus_tree[_key]
        row = new_row_from_bytes(val)
        return row

    def delete(self, key: Value):
        _key = bytes(key)
        del self.b_plus_tree[_key]


def new_table(pager: Pager, free_list: FreeList, name: str, seq: int, col_names: list[str], col_types: list[int]) -> Table:
    b_plus_tree = new_b_plus_tree(pager, seq, free_list)
    return Table(name, seq, col_names, col_types, b_plus_tree)


def new_table_from_bytes(pager: Pager, free_list: FreeList, buf: io.BytesIO) -> Table:
    name = from_buf(buf, str)
    seq = from_buf(buf, int)
    num_cols = from_buf(buf, int)
    col_names = [from_buf(buf, str) for _ in range(num_cols)]
    col_types = [from_buf(buf, int) for _ in range(num_cols)]
    root_page_id = pager.root_page_id_get(seq)
    b_plus_tree = new_b_plus_tree_from_root_page_id(pager, seq, free_list, root_page_id)
    table = Table(name, seq, col_names, col_types, b_plus_tree)
    return table


class TableListNode:

    def __init__(self, pager: Pager, page_id: int, next_page_id: int):
        self.pager: Pager = pager
        self.page_id: int = page_id
        self.next_page_id: int = next_page_id
        self.tables: list[Table] = []

    def __bytes__(self):
        r = b''
        r += to_bytes(self.page_id)
        r += to_bytes(self.next_page_id)
        r += to_bytes(len(self.tables))
        for table in self.tables:
            r += bytes(table)
        return r

    def persist(self) -> None:
        bs = bytes(self)
        self.pager.page_set(self.page_id, bs)

    def add_table(self, table: Table) -> None:
        self.tables.append(table)

    def is_full(self) -> bool:
        return len(self.tables) >= NUM_TABLE


def new_table_list_node(pager: Pager, page_id: int, next_page_id: int) -> TableListNode:
    node = TableListNode(pager, page_id, next_page_id)
    return node


def new_table_list_node_from_page_id(pager: Pager, free_list: FreeList, page_id: int) -> TableListNode:
    buf = pager.page_get(page_id)
    _page_id = from_buf(buf, int)
    if _page_id != page_id:
        raise ValueError("page_id 错误")
    next_page_id = from_buf(buf, int)
    num_tables = from_buf(buf, int)
    tables = [new_table_from_bytes(pager, free_list, buf) for _ in range(num_tables)]
    node = TableListNode(pager, page_id, next_page_id)
    node.tables = tables
    return node


class TableList:

    def __init__(self, pager: Pager, free_list: FreeList, head: TableListNode, tail: TableListNode):
        self.pager: Pager = pager
        self.free_list: FreeList = free_list
        self.head: TableListNode = head
        self.tail: TableListNode = tail

    def add_table(self, table: Table) -> None:
        if not self.tail.is_full():
            self.tail.add_table(table)
            self.tail.persist()
            return

        # tail is full
        new_tail_page_id = self.free_list.get_page_id()
        new_tail = new_table_list_node(self.pager, new_tail_page_id, NULL_PAGE_ID)
        new_tail.add_table(table)
        new_tail.persist()
        self.tail.next_page_id = new_tail.page_id
        self.tail.persist()
        self.tail = new_tail
        self.pager.table_tail_page_id_set(new_tail.page_id)
        return

    def get_tables(self) -> dict[str, Table]:
        tables = {}
        node = self.head
        while True:
            for table in node.tables:
                tables[table.name] = table
            if node.next_page_id == NULL_PAGE_ID:
                break
            node = new_table_list_node_from_page_id(self.pager, self.free_list, node.next_page_id)
        return tables


def new_table_list(pager: Pager, free_list: FreeList) -> TableList:
    head_page_id = free_list.get_page_id()
    head = new_table_list_node(pager, head_page_id, NULL_PAGE_ID)
    head.persist()
    pager.table_head_page_id_set(head.page_id)
    pager.table_tail_page_id_set(head.page_id)
    table_list = TableList(pager, free_list, head, head)
    return table_list


def new_table_list_from_page_id(pager: Pager, free_list: FreeList, head_page_id: int, tail_page_id: int) -> TableList:
    head = new_table_list_node_from_page_id(pager, free_list, head_page_id)
    tail = new_table_list_node_from_page_id(pager, free_list, tail_page_id)
    table_list = TableList(pager, free_list, head, tail)
    return table_list
