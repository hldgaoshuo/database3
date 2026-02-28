import io

from b_plus_tree import new_b_plus_tree
from const import META_PAGE_ID, INIT_B_PLUS_TREE_SEQ
from free_list import FreeList, new_free_list_from_page_id, new_free_list
from pager import Pager
from row import Row, new_row_from_bytes
from table import Table, new_table
from b_plus_tree_seq import BPlusTreeSeqGenerator, new_b_plus_tree_seq_generator
from value.value import Value
from table_list import TableList, new_table_list_from_page_id, new_table_list
from utils import from_buf


class Database:

    def __init__(self):
        self.pager: Pager | None = None
        self.free_list: FreeList | None = None
        self.b_plus_tree_seq_gen: BPlusTreeSeqGenerator | None = None
        self.table_list: TableList | None = None
        self.tables: dict[str, Table] = {}

    def create_table(self, table_name: str, col_names: list[str], col_types: list[int]):
        if table_name in self.tables:
            raise ValueError("table name already exists")
        seq = self.b_plus_tree_seq_gen.get_next_seq()
        table = new_table(table_name, col_names, col_types, self.pager, self.free_list, seq)
        self.table_list.add_table(table)
        self.tables[table_name] = table

    def create_index(self, table_name: str, col_names: list[str]):
        if table_name not in self.tables:
            raise ValueError("table name not exists")
        table = self.tables[table_name]
        col_indexes = []
        for col_name in col_names:
            col_index = table.col_names.index(col_name)
            col_indexes.append(col_index)
        col_indexes.sort()
        col_indexes = tuple(col_indexes)
        seq = self.b_plus_tree_seq_gen.get_next_seq()
        index = new_b_plus_tree(self.pager, self.free_list, seq)
        table.indexes[col_indexes] = index

    # todo 先把 KV 用的的方法拿过来，后面接了前端再看怎么写合适
    def add(self, name: str, key: Value, row: Row):
        table = self.tables[name]
        _key = bytes(key)
        _row = bytes(row)
        key_vals = [(_key, _row)]
        table.data.add(key_vals)

    def get_one(self, name: str, key: Value) -> Row:
        table = self.tables[name]
        _key = bytes(key)
        _row = table.data.get_one(_key)
        row = new_row_from_bytes(_row)
        return row

    def delete_one(self, name: str, key: Value):
        table = self.tables[name]
        _key = bytes(key)
        table.data.delete_one(_key)


def new_database(pager: Pager) -> Database:
    db = Database()
    db.pager = pager
    free_list = new_free_list(pager, META_PAGE_ID)
    db.free_list = free_list
    b_plus_tree_seq_gen = new_b_plus_tree_seq_generator(pager, INIT_B_PLUS_TREE_SEQ)
    db.b_plus_tree_seq_gen = b_plus_tree_seq_gen
    table_list = new_table_list(pager, free_list)
    db.table_list = table_list
    tables = table_list.get_tables()
    db.tables = tables
    return db


def new_database_from_meta(pager: Pager, meta: io.BytesIO) -> Database:
    db = Database()
    db.pager = pager
    used_page_id = from_buf(meta, int)
    head_page_id = from_buf(meta, int)
    tail_page_id = from_buf(meta, int)
    free_list = new_free_list_from_page_id(pager, used_page_id, head_page_id, tail_page_id)
    db.free_list = free_list
    init_seq = from_buf(meta, int)
    b_plus_tree_seq_gen = new_b_plus_tree_seq_generator(pager, init_seq)
    db.b_plus_tree_seq_gen = b_plus_tree_seq_gen
    table_head_page_id = from_buf(meta, int)
    table_tail_page_id = from_buf(meta, int)
    table_list = new_table_list_from_page_id(pager, free_list, table_head_page_id, table_tail_page_id)
    db.table_list = table_list
    tables = table_list.get_tables()
    db.tables = tables
    return db
