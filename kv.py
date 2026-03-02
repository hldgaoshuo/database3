from b_plus_tree import BPlusTree, new_b_plus_tree
from free_list import FreeList
from pager import Pager
from utils import to_bytes


class KV:

    def __init__(self):
        self.data: BPlusTree | None = None

    def __getitem__(self, item):
        _item = to_bytes(item)
        return self.data.get_one(_item)

    def __setitem__(self, key, value):
        _key = to_bytes(key)
        _value = to_bytes(value)
        key_vals = [(_key, _value)]
        self.data.upsert(key_vals)

    def __delitem__(self, key):
        _key = to_bytes(key)
        self.data.delete_one(_key)


def new_kv(pager: Pager, free_list: FreeList, seq: int, is_seq_new: bool) -> KV:
    kv = KV()
    kv.data = new_b_plus_tree(pager, free_list, seq, is_seq_new)
    return kv
