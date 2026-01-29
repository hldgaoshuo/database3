import io
from const import META_PAGE_ID, BYTES_MAGIC_NUMBER, MAGIC_NUMBER_BS, NULL_PAGE_ID
from file import file_open, get_page, set_magic_number
from free_list import FreeList, new_free_list, new_free_list_from_page_id
from utils import from_buf


def init() -> FreeList:
    fd = file_open('test.db')
    meta_bs = get_page(fd, META_PAGE_ID)
    meta_buf = io.BytesIO(meta_bs)
    magic_number_bs = meta_buf.read(BYTES_MAGIC_NUMBER)
    if magic_number_bs == MAGIC_NUMBER_BS:
        used_page_id = from_buf(meta_buf, int)
        from_buf(meta_buf, int)  # skip root_page_id
        head_page_id = from_buf(meta_buf, int)
        tail_page_id = from_buf(meta_buf, int)
        free_list = new_free_list_from_page_id(fd, used_page_id, head_page_id, tail_page_id)
    else:
        set_magic_number(fd)
        free_list = new_free_list(fd, META_PAGE_ID)
    return free_list


def test_add_unused_page_id_1():
    free_list = init()
    free_list.add_unused_page_id(10)


def test_add_unused_page_id_2():
    free_list = init()
    for i in [10, 20]:
        free_list.add_unused_page_id(i)


def test_add_unused_page_id_3():
    free_list = init()
    for i in [10, 20, 30]:
        free_list.add_unused_page_id(i)


def test_add_unused_page_id_4():
    free_list = init()
    for i in [10, 20, 30, 40, 50]:
        free_list.add_unused_page_id(i)


def test_get_unused_page_id_1():
    free_list = init()
    free_list.add_unused_page_id(10)
    for i in [10, NULL_PAGE_ID]:
        r = free_list.get_unused_page_id()
        assert r == i


def test_get_unused_page_id_2():
    free_list = init()
    for i in [10, 20]:
        free_list.add_unused_page_id(i)
    for i in [10, 20, NULL_PAGE_ID]:
        r = free_list.get_unused_page_id()
        assert r == i


def test_get_unused_page_id_3():
    free_list = init()
    for i in [10, 20, 30]:
        free_list.add_unused_page_id(i)
    for i in [10, 20, 30, 1]:
        r = free_list.get_unused_page_id()
        assert r == i


def test_get_unused_page_id_4():
    free_list = init()
    for i in [10, 20, 30, 40]:
        free_list.add_unused_page_id(i)
    for i in [10, 20, 30, 40, 1, 2, NULL_PAGE_ID]:
        r = free_list.get_unused_page_id()
        assert r == i
