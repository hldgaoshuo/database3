import inspect
from const import META_PAGE_ID, BYTES_MAGIC_NUMBER, MAGIC_NUMBER_BS, INIT_B_PLUS_TREE_SEQ
from file import file_open
from pager import new_pager
from b_plus_tree_seq import BPlusTreeSeqGenerator, new_b_plus_tree_seq_generator
from utils import from_buf


def init_b_plus_tree_seq_gen(name: str) -> tuple[int, BPlusTreeSeqGenerator]:
    fd = file_open(f'{name}.db')
    pager = new_pager(fd)
    meta = pager.page_get(META_PAGE_ID)
    magic_number_bs = meta.read(BYTES_MAGIC_NUMBER)
    if magic_number_bs == MAGIC_NUMBER_BS:
        from_buf(meta, int)  # used_page_id
        from_buf(meta, int)  # head_page_id
        from_buf(meta, int)  # tail_page_id
        init_seq = from_buf(meta, int)
        from_buf(meta, int)  # table_head_page_id
        from_buf(meta, int)  # table_tail_page_id
    else:
        pager.magic_number_set()
        init_seq = INIT_B_PLUS_TREE_SEQ
    seq_gen = new_b_plus_tree_seq_generator(pager, init_seq)
    return fd, seq_gen


def test_b_plus_tree_seq_gen():
    name = inspect.currentframe().f_code.co_name
    fd, seq_gen = init_b_plus_tree_seq_gen(name)
    print()
    for _ in range(5):
        r = seq_gen.get_next_seq()
        print(r)
