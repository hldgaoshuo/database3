import os
import io

from const import BYTES_PAGE, META_PAGE_ID, MAGIC_NUMBER_BS, BYTES_MAGIC_NUMBER, BYTES_USED_PAGE_ID, BYTES_HEAD_PAGE_ID, \
    BYTES_TAIL_PAGE_ID, BYTES_TABLE_SEQ, BYTES_TABLE_HEAD_PAGE_ID, BYTES_TABLE_TAIL_PAGE_ID, BYTES_ROOT_PAGE_ID
from utils import to_bytes, from_bytes


class Pager:

    def __init__(self, fd: int):
        self.fd: int = fd

    def magic_number_set(self) -> None:
        offset = META_PAGE_ID * BYTES_PAGE
        bs = MAGIC_NUMBER_BS
        self.file_update(offset, bs)

    def magic_number_exist(self) -> bool:
        offset = META_PAGE_ID * BYTES_PAGE
        bs = self.file_read(offset, BYTES_MAGIC_NUMBER)
        return bs == MAGIC_NUMBER_BS

    def used_page_id_set(self, used_page_id: int) -> None:
        offset = (
                META_PAGE_ID * BYTES_PAGE +
                BYTES_MAGIC_NUMBER
        )
        bs = to_bytes(used_page_id)
        self.file_update(offset, bs)

    def head_page_id_set(self, head_page_id: int) -> None:
        offset = (
                META_PAGE_ID * BYTES_PAGE +
                BYTES_MAGIC_NUMBER +
                BYTES_USED_PAGE_ID
        )
        bs = to_bytes(head_page_id)
        self.file_update(offset, bs)

    def tail_page_id_set(self, tail_page_id: int) -> None:
        offset = (
                META_PAGE_ID * BYTES_PAGE +
                BYTES_MAGIC_NUMBER +
                BYTES_USED_PAGE_ID +
                BYTES_HEAD_PAGE_ID
        )
        bs = to_bytes(tail_page_id)
        self.file_update(offset, bs)

    def table_seq_set(self, seq: int) -> None:
        offset = (
                META_PAGE_ID * BYTES_PAGE +
                BYTES_MAGIC_NUMBER +
                BYTES_USED_PAGE_ID +
                BYTES_HEAD_PAGE_ID +
                BYTES_TAIL_PAGE_ID
        )
        bs = to_bytes(seq)
        self.file_update(offset, bs)

    def table_head_page_id_set(self, table_head_page_id: int) -> None:
        offset = (
                META_PAGE_ID * BYTES_PAGE +
                BYTES_MAGIC_NUMBER +
                BYTES_USED_PAGE_ID +
                BYTES_HEAD_PAGE_ID +
                BYTES_TAIL_PAGE_ID +
                BYTES_TABLE_SEQ
        )
        bs = to_bytes(table_head_page_id)
        self.file_update(offset, bs)

    def table_tail_page_id_set(self, table_tail_page_id: int) -> None:
        offset = (
                META_PAGE_ID * BYTES_PAGE +
                BYTES_MAGIC_NUMBER +
                BYTES_USED_PAGE_ID +
                BYTES_HEAD_PAGE_ID +
                BYTES_TAIL_PAGE_ID +
                BYTES_TABLE_SEQ +
                BYTES_TABLE_HEAD_PAGE_ID
        )
        bs = to_bytes(table_tail_page_id)
        self.file_update(offset, bs)

    def root_page_id_set(self, seq: int, root_page_id: int) -> None:
        offset = (
                META_PAGE_ID * BYTES_PAGE +
                BYTES_MAGIC_NUMBER +
                BYTES_USED_PAGE_ID +
                BYTES_HEAD_PAGE_ID +
                BYTES_TAIL_PAGE_ID +
                BYTES_TABLE_SEQ +
                BYTES_TABLE_HEAD_PAGE_ID +
                BYTES_TABLE_TAIL_PAGE_ID +
                BYTES_ROOT_PAGE_ID * seq
        )
        bs = to_bytes(root_page_id)
        self.file_update(offset, bs)

    def root_page_id_get(self, seq: int) -> int:
        offset = (
                META_PAGE_ID * BYTES_PAGE +
                BYTES_MAGIC_NUMBER +
                BYTES_USED_PAGE_ID +
                BYTES_HEAD_PAGE_ID +
                BYTES_TAIL_PAGE_ID +
                BYTES_TABLE_SEQ +
                BYTES_TABLE_HEAD_PAGE_ID +
                BYTES_TABLE_TAIL_PAGE_ID +
                BYTES_ROOT_PAGE_ID * seq
        )
        root_page_id_bs = self.file_read(offset, BYTES_ROOT_PAGE_ID)
        root_page_id = from_bytes(root_page_id_bs, int)
        return root_page_id

    def page_get(self, page_id: int) -> io.BytesIO:
        offset = page_id * BYTES_PAGE
        page_bs = self.file_read(offset, BYTES_PAGE)
        page_buf = io.BytesIO(page_bs)
        return page_buf

    def page_set(self, page_id: int, page_bs: bytes) -> None:
        offset = page_id * BYTES_PAGE
        self.file_update(offset, page_bs)

    def file_read(self, offset: int, length: int) -> bytes:
        os.lseek(self.fd, offset, os.SEEK_SET)
        bs = os.read(self.fd, length)
        return bs

    def file_update(self, offset: int, data: bytes) -> None:
        os.lseek(self.fd, offset, os.SEEK_SET)
        os.write(self.fd, data)
        os.fsync(self.fd)


def new_pager(fd: int) -> Pager:
    pager = Pager(fd)
    return pager
