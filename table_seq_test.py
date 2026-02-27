import inspect
from const import META_PAGE_ID, BYTES_MAGIC_NUMBER, MAGIC_NUMBER_BS, INIT_TABLE_SEQ
from file import file_open
from pager import new_pager
from table_seq import TableSeqGenerator, new_table_seq_generator
from utils import from_buf


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
