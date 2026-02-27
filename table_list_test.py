import inspect
from const import META_PAGE_ID, BYTES_MAGIC_NUMBER, MAGIC_NUMBER_BS, INIT_TABLE_SEQ
from file import file_open
from free_list import FreeList, new_free_list_from_page_id, new_free_list
from pager import new_pager, Pager
from table import new_table
from table_list import TableList, new_table_list_from_page_id, new_table_list
from table_seq import TableSeqGenerator, new_table_seq_generator
from utils import from_buf
from value.const import VALUE_TYPE_STRING, VALUE_TYPE_INT


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
    table = new_table(table_name, table_col_names, table_col_types, pager, free_list, table_seq)
    table_list.add_table(table)
