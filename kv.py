from b_plus_tree import BPlusTree, new_b_plus_tree_from_root_page_id, new_b_plus_tree
from const import META_PAGE_ID, BYTES_MAGIC_NUMBER, MAGIC_NUMBER_BS
from file import file_open
from free_list import new_free_list_from_page_id, new_free_list
from pager import Pager, new_pager
from utils import from_buf, to_bytes


class KV:

    def __init__(self):
        self.pager: Pager | None = None
        self.data: BPlusTree | None = None

    def __getitem__(self, item):
        _item = to_bytes(item)
        return self.data.get_one(_item)

    def __setitem__(self, key, value):
        _key = to_bytes(key)
        _value = to_bytes(value)
        key_vals = [(_key, _value)]
        self.data.add(key_vals)

    def __delitem__(self, key):
        _key = to_bytes(key)
        self.data.delete_one(_key)


def new_kv(name: str) -> KV:
    seq = 0  # kv only have one b plus tree
    kv = KV()
    fd = file_open(f'{name}.db')
    pager = new_pager(fd)
    kv.pager = pager
    meta = pager.page_get(META_PAGE_ID)
    magic_number_bs = meta.read(BYTES_MAGIC_NUMBER)
    if magic_number_bs == MAGIC_NUMBER_BS:
        used_page_id = from_buf(meta, int)
        head_page_id = from_buf(meta, int)
        tail_page_id = from_buf(meta, int)
        free_list = new_free_list_from_page_id(pager, used_page_id, head_page_id, tail_page_id)
        from_buf(meta, int)  # b_plus_tree_seq
        from_buf(meta, int)  # table_head_page_id
        from_buf(meta, int)  # table_tail_page_id
        root_page_id = from_buf(meta, int)
        kv.data = new_b_plus_tree_from_root_page_id(pager, free_list, seq, root_page_id)
    else:
        pager.magic_number_set()
        free_list = new_free_list(pager, META_PAGE_ID)
        kv.data = new_b_plus_tree(pager, free_list, seq)
    return kv
