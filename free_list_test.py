import os
import inspect
import pytest
from const import META_PAGE_ID, BYTES_MAGIC_NUMBER, MAGIC_NUMBER_BS, NULL_PAGE_ID
from file import file_open
from free_list import FreeList, new_free_list, new_free_list_from_page_id
from pager import new_pager
from utils import from_buf


def init(name: str) -> tuple[int, FreeList]:
    fd = file_open(f'{name}.db')
    pager = new_pager(fd)
    meta = pager.page_get(META_PAGE_ID)
    magic_number_bs = meta.read(BYTES_MAGIC_NUMBER)
    if magic_number_bs == MAGIC_NUMBER_BS:
        used_page_id = from_buf(meta, int)
        head_page_id = from_buf(meta, int)
        tail_page_id = from_buf(meta, int)
        free_list = new_free_list_from_page_id(pager, used_page_id, head_page_id, tail_page_id)
    else:
        pager.magic_number_set()
        free_list = new_free_list(pager, META_PAGE_ID)
    return fd, free_list


def close(fd: int, name: str) -> None:
    os.close(fd)
    os.remove(f'{name}.db')


def test_add_unused_page_id_1():
    name = inspect.currentframe().f_code.co_name
    fd, free_list = init(name)
    free_list.add_unused_page_id(10)
    close(fd, name)


def test_add_unused_page_id_2():
    name = inspect.currentframe().f_code.co_name
    fd, free_list = init(name)
    for i in [10, 20]:
        free_list.add_unused_page_id(i)
    close(fd, name)


def test_add_unused_page_id_3():
    name = inspect.currentframe().f_code.co_name
    fd, free_list = init(name)
    for i in [10, 20, 30]:
        free_list.add_unused_page_id(i)
    close(fd, name)


def test_add_unused_page_id_4():
    name = inspect.currentframe().f_code.co_name
    fd, free_list = init(name)
    for i in [10, 20, 30, 40, 50]:
        free_list.add_unused_page_id(i)
    close(fd, name)


def test_get_unused_page_id_1():
    name = inspect.currentframe().f_code.co_name
    fd, free_list = init(name)
    free_list.add_unused_page_id(10)
    for i in [10, NULL_PAGE_ID]:
        r = free_list.get_unused_page_id()
        assert r == i
    close(fd, name)


def test_get_unused_page_id_2():
    name = inspect.currentframe().f_code.co_name
    fd, free_list = init(name)
    for i in [10, 20]:
        free_list.add_unused_page_id(i)
    for i in [10, 20, NULL_PAGE_ID]:
        r = free_list.get_unused_page_id()
        assert r == i
    close(fd, name)


def test_get_unused_page_id_3():
    name = inspect.currentframe().f_code.co_name
    fd, free_list = init(name)
    for i in [10, 20, 30]:
        free_list.add_unused_page_id(i)
    for i in [10, 20, 30, 1]:
        r = free_list.get_unused_page_id()
        assert r == i
    close(fd, name)


def test_get_unused_page_id_4():
    name = inspect.currentframe().f_code.co_name
    fd, free_list = init(name)
    for i in [10, 20, 30, 40]:
        free_list.add_unused_page_id(i)
    for i in [10, 20, 30, 40, 1, 2, NULL_PAGE_ID]:
        r = free_list.get_unused_page_id()
        assert r == i
    close(fd, name)


if __name__ == "__main__":
    pytest.main([__file__])
