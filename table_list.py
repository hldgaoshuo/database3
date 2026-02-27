from const import NUM_TABLE, NULL_PAGE_ID
from free_list import FreeList
from pager import Pager
from table import Table, new_table_from_bytes
from utils import to_bytes, from_buf


class TableListNode:

    def __init__(self):
        self.pager: Pager | None = None
        self.page_id: int = 0
        self.next_page_id: int = 0
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
    node = TableListNode()
    node.pager = pager
    node.page_id = page_id
    node.next_page_id = next_page_id
    node.tables = []
    return node


def new_table_list_node_from_page_id(pager: Pager, free_list: FreeList, page_id: int) -> TableListNode:
    node = TableListNode()
    node.pager = pager
    buf = pager.page_get(page_id)
    _page_id = from_buf(buf, int)
    if _page_id != page_id:
        raise ValueError("page_id 错误")
    node.page_id = page_id
    node.next_page_id = from_buf(buf, int)
    num_tables = from_buf(buf, int)
    node.tables = [new_table_from_bytes(buf, pager, free_list) for _ in range(num_tables)]
    return node


class TableList:

    def __init__(self):
        self.pager: Pager | None = None
        self.free_list: FreeList | None = None
        self.head: TableListNode | None = None
        self.tail: TableListNode | None = None

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
    table_list = TableList()
    table_list.pager = pager
    table_list.free_list = free_list
    head_page_id = free_list.get_page_id()
    head = new_table_list_node(pager, head_page_id, NULL_PAGE_ID)
    head.persist()
    pager.table_head_page_id_set(head.page_id)
    pager.table_tail_page_id_set(head.page_id)
    table_list.head = head
    table_list.tail = head
    return table_list


def new_table_list_from_page_id(pager: Pager, free_list: FreeList, head_page_id: int, tail_page_id: int) -> TableList:
    table_list = TableList()
    table_list.pager = pager
    table_list.free_list = free_list
    table_list.head = new_table_list_node_from_page_id(pager, free_list, head_page_id)
    table_list.tail = new_table_list_node_from_page_id(pager, free_list, tail_page_id)
    return table_list
