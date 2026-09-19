import inspect
import os

from buffer_pool_manager import new_buffer_pool_manager
from const import META_PAGE_ID, BYTES_MAGIC_NUMBER, MAGIC_NUMBER_BS, BUFFER_POOL_SIZE
from database import new_database, new_database_from_meta
from file import file_open
from pager import new_pager
from sql.engine import execute_sql
from utils import to_bytes
from wal import Wal, new_wal


def init(name: str, pool_size: int = 4) -> tuple[int, 'object', Wal, 'object']:
    fd = file_open(f'{name}.db')
    pager = new_pager(fd)
    wal = new_wal(f'{name}.db.wal')
    bpm = new_buffer_pool_manager(pager, pool_size, wal)
    return fd, pager, wal, bpm


def close(fd: int, wal: Wal, name: str) -> None:
    os.close(fd)
    os.close(wal.fd)
    os.remove(f'{name}.db')
    os.remove(f'{name}.db.wal')


def page_bytes(tag: bytes) -> bytes:
    return to_bytes(tag)


def test_append_on_page_set():
    name = inspect.currentframe().f_code.co_name
    fd, pager, wal, bpm = init(name)
    bs = page_bytes(b'logged')
    bpm.page_set(1, bs)
    records = wal.records()
    assert len(records) == 1
    page_id, data = records[0]
    assert page_id == 1
    assert data[:len(bs)] == bs
    close(fd, wal, name)


def test_replay_recovers_unflushed():
    name = inspect.currentframe().f_code.co_name
    fd, pager, wal, bpm = init(name)
    bs = page_bytes(b'important')
    bpm.page_set(1, bs)
    # 模拟崩溃：不 flush，丢弃 bpm，重新走启动恢复流程
    assert wal.replay(pager) == 1
    wal.truncate()
    bpm2 = new_buffer_pool_manager(pager, 4, wal)
    assert bpm2.page_get(1).read(len(bs)) == bs
    close(fd, wal, name)


def test_replay_last_write_wins():
    name = inspect.currentframe().f_code.co_name
    fd, pager, wal, bpm = init(name)
    bpm.page_set(1, page_bytes(b'old'))
    bs_new = page_bytes(b'new')
    bpm.page_set(1, bs_new)
    assert wal.replay(pager) == 2
    assert pager.page_get(1).read(len(bs_new)) == bs_new
    close(fd, wal, name)


def test_replay_ignores_torn_tail():
    name = inspect.currentframe().f_code.co_name
    fd, pager, wal, bpm = init(name)
    bs = page_bytes(b'full')
    bpm.page_set(1, bs)
    # 日志尾部追加半条记录（模拟崩溃时的半截写入）
    os.lseek(wal.fd, 0, os.SEEK_END)
    os.write(wal.fd, b'\x00' * 100)
    os.fsync(wal.fd)
    # 只有完整记录被应用，半截记录忽略
    assert wal.replay(pager) == 1
    assert pager.page_get(1).read(len(bs)) == bs
    close(fd, wal, name)


def test_checkpoint_truncate():
    name = inspect.currentframe().f_code.co_name
    fd, pager, wal, bpm = init(name)
    bpm.page_set(1, page_bytes(b'one'))
    bpm.page_set(2, page_bytes(b'two'))
    assert len(wal.records()) == 2
    bpm.flush_all_pages()
    assert wal.records() == []
    close(fd, wal, name)


def test_crash_recovery_sql():
    name = inspect.currentframe().f_code.co_name
    fd, pager, wal, bpm = init(name, BUFFER_POOL_SIZE)
    bpm.magic_number_set()
    db = new_database(bpm)
    execute_sql(db, "CREATE TABLE data (name STRING, score INT)")
    execute_sql(db, "INSERT INTO data VALUES ('xiaoming', 90)")
    # 模拟崩溃：不 flush，丢弃 bpm
    wal.replay(pager)
    wal.truncate()
    bpm2 = new_buffer_pool_manager(pager, BUFFER_POOL_SIZE, wal)
    meta = bpm2.page_get(META_PAGE_ID)
    assert meta.read(BYTES_MAGIC_NUMBER) == MAGIC_NUMBER_BS
    db2 = new_database_from_meta(bpm2, meta)
    rows = execute_sql(db2, "SELECT * FROM data")
    assert [(row.vals[0].val, row.vals[1].val) for row in rows] == [("xiaoming", 90)]
    close(fd, wal, name)
