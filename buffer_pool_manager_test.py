import inspect
import os

from buffer_pool_manager import BufferPoolManager, new_buffer_pool_manager
from const import BYTES_PAGE
from file import file_open
from pager import new_pager
from utils import to_bytes


def init(name: str, pool_size: int) -> tuple[int, BufferPoolManager]:
    fd = file_open(f'{name}.db')
    pager = new_pager(fd)
    bpm = new_buffer_pool_manager(pager, pool_size)
    return fd, bpm


def close(fd: int, name: str) -> None:
    os.close(fd)
    os.remove(f'{name}.db')


def page_bytes(tag: bytes) -> bytes:
    return to_bytes(tag)


def test_page_set_get():
    name = inspect.currentframe().f_code.co_name
    fd, bpm = init(name, 4)
    bs = page_bytes(b'hello')
    bpm.page_set(1, bs)
    buf = bpm.page_get(1)
    assert buf.read(len(bs)) == bs
    close(fd, name)


def test_page_get_unwritten():
    name = inspect.currentframe().f_code.co_name
    fd, bpm = init(name, 4)
    buf = bpm.page_get(1)
    assert buf.read() == b'\x00' * BYTES_PAGE
    close(fd, name)


def test_write_back():
    name = inspect.currentframe().f_code.co_name
    fd, bpm = init(name, 4)
    bs = page_bytes(b'dirty')
    bpm.page_set(1, bs)
    # flush 前：写回式缓存，磁盘上还是旧数据
    disk_buf = bpm.pager.page_get(1)
    assert disk_buf.read(len(bs)) != bs
    # flush 后：磁盘与缓存一致
    bpm.flush_page(1)
    disk_buf = bpm.pager.page_get(1)
    assert disk_buf.read(len(bs)) == bs
    close(fd, name)


def test_flush_all_pages():
    name = inspect.currentframe().f_code.co_name
    fd, bpm = init(name, 4)
    bs1 = page_bytes(b'page1')
    bs2 = page_bytes(b'page2')
    bpm.page_set(1, bs1)
    bpm.page_set(2, bs2)
    bpm.flush_all_pages()
    assert bpm.pager.page_get(1).read(len(bs1)) == bs1
    assert bpm.pager.page_get(2).read(len(bs2)) == bs2
    for frame in bpm.frames:
        assert not frame.is_dirty
    close(fd, name)


def test_lru_evict_order():
    name = inspect.currentframe().f_code.co_name
    fd, bpm = init(name, 2)
    bpm.page_set(1, page_bytes(b'one'))
    bpm.page_set(2, page_bytes(b'two'))
    # 访问 1，使 2 成为最久未使用
    bpm.page_get(1)
    # 池已满，载入 3 应驱逐 2
    bpm.page_set(3, page_bytes(b'three'))
    assert 2 not in bpm.page_table
    assert 1 in bpm.page_table
    assert 3 in bpm.page_table
    close(fd, name)


def test_evict_dirty_auto_flush():
    name = inspect.currentframe().f_code.co_name
    fd, bpm = init(name, 1)
    bs = page_bytes(b'auto')
    bpm.page_set(1, bs)
    # 池只有 1 帧，读 page 2 驱逐 page 1，脏页应自动落盘
    bpm.page_get(2)
    assert 1 not in bpm.page_table
    assert bpm.pager.page_get(1).read(len(bs)) == bs
    # 重新读回 page 1，内容正确
    buf = bpm.page_get(1)
    assert buf.read(len(bs)) == bs
    close(fd, name)


def test_meta_partial_write():
    name = inspect.currentframe().f_code.co_name
    fd, bpm = init(name, 4)
    assert not bpm.magic_number_exist()
    bpm.magic_number_set()
    assert bpm.magic_number_exist()
    bpm.used_page_id_set(42)
    bpm.root_page_id_set(0, 7)
    bpm.root_page_id_set(1, 8)
    assert bpm.root_page_id_get(0) == 7
    assert bpm.root_page_id_get(1) == 8
    close(fd, name)


def test_meta_reopen():
    name = inspect.currentframe().f_code.co_name
    fd, bpm = init(name, 4)
    bpm.magic_number_set()
    bpm.root_page_id_set(0, 99)
    bpm.flush_all_pages()
    # 用一个新的缓冲池（缓存为空）包装同一个 fd，模拟 reopen
    bpm2 = new_buffer_pool_manager(new_pager(fd), 4)
    assert bpm2.magic_number_exist()
    assert bpm2.root_page_id_get(0) == 99
    close(fd, name)
