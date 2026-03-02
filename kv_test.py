import pytest

from const import META_PAGE_ID, BYTES_MAGIC_NUMBER, MAGIC_NUMBER_BS
from file import file_open
from free_list import new_free_list_from_page_id, new_free_list
from kv import new_kv, KV
from pager import new_pager
from utils import from_bytes, from_buf

KV_NAME = 'test_kv'


def init(name: str) -> tuple[int, KV]:
    fd = file_open(f'{name}.db')
    pager = new_pager(fd)
    meta = pager.page_get(META_PAGE_ID)
    magic_number_bs = meta.read(BYTES_MAGIC_NUMBER)
    if magic_number_bs == MAGIC_NUMBER_BS:
        used_page_id = from_buf(meta, int)
        head_page_id = from_buf(meta, int)
        tail_page_id = from_buf(meta, int)
        free_list = new_free_list_from_page_id(pager, used_page_id, head_page_id, tail_page_id)
        from_buf(meta, int)  # b_plus_tree_seq
        from_buf(meta, int)  # database_seq
        kv = new_kv(pager, free_list, 0, False)
    else:
        pager.magic_number_set()
        free_list = new_free_list(pager, META_PAGE_ID)
        kv = new_kv(pager, free_list, 0, True)
    return fd, kv


def test_init():
    init(KV_NAME)


def test_set():
    _, kv = init(KV_NAME)
    kv[1] = 1


def test_get():
    _, kv = init(KV_NAME)
    kv[1] = 1
    assert from_bytes(kv[1], int) == 1
    kv["a"] = "a"
    assert from_bytes(kv["a"], str) == "a"
    kv[2] = "b"
    assert from_bytes(kv[2], str) == "b"
    kv["b"] = 2
    assert from_bytes(kv["b"], int) == 2


if __name__ == "__main__":
    pytest.main([__file__])
