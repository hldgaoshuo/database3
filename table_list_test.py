import inspect
import os
from b_plus_tree import new_b_plus_tree_from_root_page_id, new_b_plus_tree
from const import META_PAGE_ID, BYTES_MAGIC_NUMBER, MAGIC_NUMBER_BS
from file import file_open, get_page, set_magic_number
from free_list import new_free_list_from_page_id, new_free_list
from row import new_row
from table_list import Table, TableSeqGenerator, new_table_seq_generator
from utils import from_buf
from value.const import VALUE_TYPE_STRING, VALUE_TYPE_INT
from value.int import new_int
from value.string import new_string


def init_table(name: str) -> tuple[int, Table]:
    fd = file_open(f'{name}.db')
    seq = 0
    col_names = ["name", "gender", "score"]
    col_types = [VALUE_TYPE_STRING, VALUE_TYPE_STRING, VALUE_TYPE_INT]
    meta = get_page(fd, META_PAGE_ID)
    magic_number_bs = meta.read(BYTES_MAGIC_NUMBER)
    if magic_number_bs == MAGIC_NUMBER_BS:
        used_page_id = from_buf(meta, int)
        head_page_id = from_buf(meta, int)
        tail_page_id = from_buf(meta, int)
        free_list = new_free_list_from_page_id(fd, used_page_id, head_page_id, tail_page_id)
        from_buf(meta, int)  # table_seq
        from_buf(meta, int)  # table_head_page_id
        from_buf(meta, int)  # table_tail_page_id
        root_page_id = from_buf(meta, int)
        b_plus_tree = new_b_plus_tree_from_root_page_id(fd, seq, free_list, root_page_id)
    else:
        set_magic_number(fd)
        free_list = new_free_list(fd, META_PAGE_ID)
        b_plus_tree = new_b_plus_tree(fd, seq, free_list)
    table = Table(name, seq, col_names, col_types, b_plus_tree)
    return fd, table


def close_table(fd: int, name: str) -> None:
    os.close(fd)
    os.remove(f'{name}.db')


def test_table():
    name = inspect.currentframe().f_code.co_name
    fd, table = init_table(name)
    key = new_int(10)
    row = new_row(100, [new_string("xiaoming"), new_string("m"), new_int(90)])
    table.set(key, row)
    row = table.get(key)
    row.show()
    close_table(fd, name)


def init_table_seq_gen(name: str) -> tuple[int, TableSeqGenerator]:
    fd = file_open(f'{name}.db')
    meta = get_page(fd, META_PAGE_ID)
    magic_number_bs = meta.read(BYTES_MAGIC_NUMBER)
    if magic_number_bs == MAGIC_NUMBER_BS:
        from_buf(meta, int)  # used_page_id
        from_buf(meta, int)  # head_page_id
        from_buf(meta, int)  # tail_page_id
        table_seq = from_buf(meta, int)
        from_buf(meta, int)  # table_head_page_id
        from_buf(meta, int)  # table_tail_page_id
    else:
        set_magic_number(fd)
        table_seq = 0
    table_seq_gen = new_table_seq_generator(fd, table_seq)
    return fd, table_seq_gen


def test_table_seq_gen():
    name = inspect.currentframe().f_code.co_name
    fd, table_seq_gen = init_table_seq_gen(name)
    print()
    for _ in range(5):
        r = table_seq_gen.get_next_seq()
        print(r)
