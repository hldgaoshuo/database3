import os

from const import BYTES_PAGE
from pager import Pager
from utils import to_bytes, from_bytes

BYTES_WAL_PAGE_ID = 8
BYTES_WAL_RECORD = BYTES_WAL_PAGE_ID + BYTES_PAGE


class Wal:
    """
    预写式日志（redo-only 物理日志）。
    每条记录是一整个页镜像：[page_id(8 字节)][页数据(4096 字节)]，定长。
    约定：脏页写回数据文件之前，页镜像必须先落日志（write-ahead）。
    恢复时顺序重放（物理 redo 幂等，同页后写覆盖先写），
    尾部不完整记录视为崩溃时的半截写入，直接忽略。
    flush_all_pages 之后 checkpoint：截断日志。
    注意：没有事务 undo，操作中途崩溃（如 B+ 树分裂写了一半）不在本层保证。
    """

    def __init__(self):
        self.fd: int = 0

    def append(self, page_id: int, page_bs: bytes) -> None:
        if len(page_bs) != BYTES_PAGE:
            raise ValueError("wal 记录必须是整页")
        record = to_bytes(page_id) + page_bs
        os.lseek(self.fd, 0, os.SEEK_END)
        os.write(self.fd, record)
        os.fsync(self.fd)

    def replay(self, pager: Pager) -> int:
        """顺序重放到数据文件，返回应用的记录数；尾部不完整记录忽略"""
        count = 0
        os.lseek(self.fd, 0, os.SEEK_SET)
        while True:
            record = os.read(self.fd, BYTES_WAL_RECORD)
            if len(record) < BYTES_WAL_RECORD:
                break
            page_id = from_bytes(record[:BYTES_WAL_PAGE_ID], int)
            pager.page_set(page_id, record[BYTES_WAL_PAGE_ID:])
            count += 1
        return count

    def truncate(self) -> None:
        os.ftruncate(self.fd, 0)
        os.lseek(self.fd, 0, os.SEEK_SET)
        os.fsync(self.fd)

    def records(self) -> list[tuple[int, bytes]]:
        """测试用：读出全部完整记录"""
        result = []
        os.lseek(self.fd, 0, os.SEEK_SET)
        while True:
            record = os.read(self.fd, BYTES_WAL_RECORD)
            if len(record) < BYTES_WAL_RECORD:
                break
            page_id = from_bytes(record[:BYTES_WAL_PAGE_ID], int)
            result.append((page_id, record[BYTES_WAL_PAGE_ID:]))
        return result


def new_wal(path: str) -> Wal:
    wal = Wal()
    # O_BINARY 仅 Windows 存在，POSIX 下默认为二进制模式
    wal.fd = os.open(path, os.O_RDWR | os.O_CREAT | getattr(os, 'O_BINARY', 0))
    return wal
