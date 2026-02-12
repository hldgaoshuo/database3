import inspect
import os
from b_plus_tree import new_b_plus_tree_from_root_page_id, new_b_plus_tree
from const import META_PAGE_ID, BYTES_MAGIC_NUMBER, MAGIC_NUMBER_BS, INIT_TABLE_SEQ
from file import file_open
from free_list import FreeList, new_free_list_from_page_id, new_free_list
from pager import new_pager, Pager
from row import new_row
from table_list import Table, TableSeqGenerator, new_table_seq_generator, TableList, new_table_list_from_page_id, \
    new_table_list, new_table
from utils import new_int64, from_buf
from value.const import VALUE_TYPE_STRING, VALUE_TYPE_INT
from value.value_int import new_value_int
from value.value_int64 import new_value_int64
from value.value_string import new_value_string


def init_table_seq_gen(name: str) -> tuple[int, TableSeqGenerator]:
    fd = file_open(f'{name}.db')
    pager = new_pager(fd)
    meta = pager.page_get(META_PAGE_ID)
    magic_number_bs = meta.read(BYTES_MAGIC_NUMBER)
    if magic_number_bs == MAGIC_NUMBER_BS:
        from_buf(meta, int)  # used_page_id
        from_buf(meta, int)  # head_page_id
        from_buf(meta, int)  # tail_page_id
        table_seq = from_buf(meta, int)
        from_buf(meta, int)  # table_head_page_id
        from_buf(meta, int)  # table_tail_page_id
    else:
        pager.magic_number_set()
        table_seq = INIT_TABLE_SEQ
    table_seq_gen = new_table_seq_generator(pager, table_seq)
    return fd, table_seq_gen


def test_table_seq_gen():
    name = inspect.currentframe().f_code.co_name
    fd, table_seq_gen = init_table_seq_gen(name)
    print()
    for _ in range(5):
        r = table_seq_gen.get_next_seq()
        print(r)


def init_table(name: str) -> tuple[int, Table]:
    seq = 0
    col_names = ["name", "gender", "score"]
    col_types = [VALUE_TYPE_STRING, VALUE_TYPE_STRING, VALUE_TYPE_INT]
    fd = file_open(f'{name}.db')
    pager = new_pager(fd)
    meta = pager.page_get(META_PAGE_ID)
    magic_number_bs = meta.read(BYTES_MAGIC_NUMBER)
    if magic_number_bs == MAGIC_NUMBER_BS:
        used_page_id = from_buf(meta, int)
        head_page_id = from_buf(meta, int)
        tail_page_id = from_buf(meta, int)
        free_list = new_free_list_from_page_id(pager, used_page_id, head_page_id, tail_page_id)
        from_buf(meta, int)  # table_seq
        from_buf(meta, int)  # table_head_page_id
        from_buf(meta, int)  # table_tail_page_id
        root_page_id = from_buf(meta, int)
        b_plus_tree = new_b_plus_tree_from_root_page_id(pager, seq, free_list, root_page_id)
    else:
        pager.magic_number_set()
        free_list = new_free_list(pager, META_PAGE_ID)
        b_plus_tree = new_b_plus_tree(pager, seq, free_list)
    table = Table(name, seq, col_names, col_types, b_plus_tree)
    return fd, table


def close_table(fd: int, name: str) -> None:
    os.close(fd)
    os.remove(f'{name}.db')


def test_table():
    name = inspect.currentframe().f_code.co_name
    fd, table = init_table(name)
    key = new_value_int64(new_int64(10))
    row = new_row(new_value_int64(new_int64(10)), [new_value_string("xiaoming"), new_value_string("m"), new_value_int(90)])
    table.set(key, row)
    row = table.get(key)
    row.show()
    close_table(fd, name)


def init_table_list(name: str) -> tuple[Pager, FreeList, TableSeqGenerator, TableList]:
    fd = file_open(f'{name}.db')
    pager = new_pager(fd)
    meta = pager.page_get(META_PAGE_ID)
    magic_number_bs = meta.read(BYTES_MAGIC_NUMBER)
    if magic_number_bs == MAGIC_NUMBER_BS:
        used_page_id = from_buf(meta, int)
        head_page_id = from_buf(meta, int)
        tail_page_id = from_buf(meta, int)
        free_list = new_free_list_from_page_id(pager, used_page_id, head_page_id, tail_page_id)
        table_seq = from_buf(meta, int)
        table_seq_gen = new_table_seq_generator(pager, table_seq)
        table_head_page_id = from_buf(meta, int)
        table_tail_page_id = from_buf(meta, int)
        table_list = new_table_list_from_page_id(pager, free_list, table_head_page_id, table_tail_page_id)
    else:
        pager.magic_number_set()
        free_list = new_free_list(pager, META_PAGE_ID)
        table_seq_gen = new_table_seq_generator(pager, INIT_TABLE_SEQ)
        table_list = new_table_list(pager, free_list)
    return pager, free_list, table_seq_gen, table_list


def test_table_list():
    name = inspect.currentframe().f_code.co_name
    pager, free_list, table_seq_gen, table_list = init_table_list(name)
    table_name = "data"
    table_seq = table_seq_gen.get_next_seq()
    table_col_names = ["name", "gender", "score"]
    table_col_types = [VALUE_TYPE_STRING, VALUE_TYPE_STRING, VALUE_TYPE_INT]
    table = new_table(pager, free_list, table_name, table_seq, table_col_names, table_col_types)
    table_list.add_table(table)
