from b_plus_tree import BPlusTree, new_b_plus_tree_from_root_page_id, new_b_plus_tree
from const import META_PAGE_ID, BYTES_MAGIC_NUMBER, MAGIC_NUMBER_BS
from file import file_open
from free_list import new_free_list_from_page_id, new_free_list
from pager import Pager, new_pager
from utils import from_buf, to_bytes


class KV:

    def __init__(self, pager: Pager, b_plus_tree: BPlusTree):
        self.pager: Pager = pager
        self.b_plus_tree: BPlusTree = b_plus_tree

    def __getitem__(self, item):
        _item = to_bytes(item)
        return self.b_plus_tree[_item]

    def __setitem__(self, key, value):
        _key = to_bytes(key)
        _value = to_bytes(value)
        self.b_plus_tree[_key] = _value

    def __delitem__(self, key):
        _key = to_bytes(key)
        del self.b_plus_tree[_key]


def new_kv(name: str) -> KV:
    seq = 0  # kv only have one b plus tree
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
    kv = KV(pager, b_plus_tree)
    return kv
