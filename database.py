import io

from b_plus_tree import new_b_plus_tree
from const import META_PAGE_ID, INIT_B_PLUS_TREE_SEQ
from free_list import FreeList, new_free_list_from_page_id, new_free_list
from kv import KV, new_kv
from pager import Pager
from table import Table, new_table, new_table_from_bytes
from b_plus_tree_seq import BPlusTreeSeqGenerator, new_b_plus_tree_seq_generator
from utils import from_buf, from_bytes


class Database:

    def __init__(self):
        self.pager: Pager | None = None
        self.free_list: FreeList | None = None
        self.b_plus_tree_seq_gen: BPlusTreeSeqGenerator | None = None
        self.tables: KV | None = None

    def create_table(self, table_name: str, col_names: list[str], col_types: list[int]) -> Table:
        table = self.tables[table_name]
        if table is not None:
            raise ValueError("table name already exists")

        seq = self.b_plus_tree_seq_gen.get_next_seq()
        table = new_table(table_name, col_names, col_types, self.pager, self.free_list, seq)
        self.persist_table(table_name, table)
        return table

    def create_index(self, table_name: str, col_names: list[str]):
        table = self.get_table(table_name)

        col_indexes = []
        for col_name in col_names:
            col_index = table.col_names.index(col_name)
            col_indexes.append(col_index)
        col_indexes.sort()
        col_indexes = tuple(col_indexes)
        if col_indexes in table.indexes:
            raise ValueError("index already exists")

        seq = self.b_plus_tree_seq_gen.get_next_seq()
        index = new_b_plus_tree(self.pager, self.free_list, seq, True)
        table.indexes[col_indexes] = index
        self.persist_table(table_name, table)

    def get_table(self, table_name: str) -> Table:
        table_bytes = self.tables[table_name]
        if table_bytes is None:
            raise ValueError("table name not exists")
        table_row = from_bytes(table_bytes, bytes)
        table = new_table_from_bytes(table_row, self.pager, self.free_list)
        return table

    def persist_table(self, table_name: str, table: Table):
        table_row = bytes(table)
        self.tables[table_name] = table_row


def new_database(pager: Pager) -> Database:
    db = Database()
    db.pager = pager
    db.free_list = new_free_list(pager, META_PAGE_ID)
    db.b_plus_tree_seq_gen = new_b_plus_tree_seq_generator(pager, INIT_B_PLUS_TREE_SEQ)
    seq = db.b_plus_tree_seq_gen.get_next_seq()
    db.tables = new_kv(db.pager, db.free_list, seq, True)
    return db


def new_database_from_meta(pager: Pager, meta: io.BytesIO) -> Database:
    db = Database()
    db.pager = pager
    used_page_id = from_buf(meta, int)
    head_page_id = from_buf(meta, int)
    tail_page_id = from_buf(meta, int)
    db.free_list = new_free_list_from_page_id(pager, used_page_id, head_page_id, tail_page_id)
    init_seq = from_buf(meta, int)
    db.b_plus_tree_seq_gen = new_b_plus_tree_seq_generator(pager, init_seq)
    database_seq = from_buf(meta, int)
    db.tables = new_kv(db.pager, db.free_list, database_seq, False)
    return db
