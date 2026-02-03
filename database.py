import io

from const import META_PAGE_ID, INIT_TABLE_SEQ
from free_list import FreeList, new_free_list_from_page_id, new_free_list
from table_list import TableSeqGenerator, Table, TableList, new_table_seq_generator, new_table_list_from_page_id, \
    new_table_list
from utils import from_buf


class Database:

    def __init__(self, fd: int, free_list: FreeList, table_seq_gen: TableSeqGenerator, table_list: TableList, tables: dict[str, Table]):
        self.fd: int = fd
        self.free_list: FreeList = free_list
        self.table_seq_gen: TableSeqGenerator = table_seq_gen
        self.table_list: TableList = table_list
        self.tables: dict[str, Table] = tables


def new_database(fd: int) -> Database:
    free_list = new_free_list(fd, META_PAGE_ID)
    table_seq_gen = new_table_seq_generator(fd, INIT_TABLE_SEQ)
    table_list = new_table_list(fd, free_list)
    tables = table_list.get_tables()
    db = Database(fd, free_list, table_seq_gen, table_list, tables)
    return db


def new_database_from_meta(fd: int, meta: io.BytesIO) -> Database:
    used_page_id = from_buf(meta, int)
    head_page_id = from_buf(meta, int)
    tail_page_id = from_buf(meta, int)
    free_list = new_free_list_from_page_id(fd, used_page_id, head_page_id, tail_page_id)
    table_seq = from_buf(meta, int)
    table_seq_gen = new_table_seq_generator(fd, table_seq)
    table_head_page_id = from_buf(meta, int)
    table_tail_page_id = from_buf(meta, int)
    table_list = new_table_list_from_page_id(fd, free_list, table_head_page_id, table_tail_page_id)
    tables = table_list.get_tables()
    db = Database(fd, free_list, table_seq_gen, table_list, tables)
    return db
