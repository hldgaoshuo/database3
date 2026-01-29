import io
from b_plus_tree import BPlusTree, new_b_plus_tree_from_root_page_id, new_b_plus_tree
from const import META_PAGE_ID, BYTES_MAGIC_NUMBER, MAGIC_NUMBER_BS
from file import file_open, get_page, set_magic_number
from free_list import new_free_list_from_page_id, new_free_list
from utils import from_buf, to_bytes


class KV:

    def __init__(self, fd: int, b_plus_tree: BPlusTree):
        self.fd: int = fd
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
    fd = file_open(f'{name}.db')
    meta_bs = get_page(fd, META_PAGE_ID)
    meta_buf = io.BytesIO(meta_bs)
    magic_number_bs = meta_buf.read(BYTES_MAGIC_NUMBER)
    if magic_number_bs == MAGIC_NUMBER_BS:
        used_page_id = from_buf(meta_buf, int)
        head_page_id = from_buf(meta_buf, int)
        tail_page_id = from_buf(meta_buf, int)
        free_list = new_free_list_from_page_id(fd, used_page_id, head_page_id, tail_page_id)
        root_page_id = from_buf(meta_buf, int)
        b_plus_tree = new_b_plus_tree_from_root_page_id(fd, free_list, root_page_id)
    else:
        set_magic_number(fd)
        free_list = new_free_list(fd, META_PAGE_ID)
        b_plus_tree = new_b_plus_tree(fd, free_list)
    kv = KV(fd, b_plus_tree)
    return kv
