import os

from const import BYTES_PAGE, META_PAGE_ID, MAGIC_NUMBER_BS, BYTES_USED_PAGE_ID, BYTES_MAGIC_NUMBER, BYTES_TAIL_PAGE_ID, BYTES_HEAD_PAGE_ID
from utils import to_bytes


def file_open(path: str) -> int:
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_BINARY)
    return fd


def file_read(fd: int, offset: int, length: int) -> bytes:
    os.lseek(fd, offset, os.SEEK_SET)
    bs = os.read(fd, length)
    return bs


def file_update(fd: int, offset: int, data: bytes) -> None:
    os.lseek(fd, offset, os.SEEK_SET)
    os.write(fd, data)
    os.fsync(fd)


def get_page(fd: int, page_id: int) -> bytes:
    offset = page_id * BYTES_PAGE
    page_bs = file_read(fd, offset, BYTES_PAGE)
    return page_bs


def set_page(fd: int, page_id: int, page_bs: bytes) -> None:
    offset = page_id * BYTES_PAGE
    file_update(fd, offset, page_bs)


def set_magic_number(fd: int) -> None:
    offset = META_PAGE_ID * BYTES_PAGE
    file_update(fd, offset, MAGIC_NUMBER_BS)


def set_used_page_id(fd: int, used_page_id: int) -> None:
    offset = META_PAGE_ID * BYTES_PAGE + BYTES_MAGIC_NUMBER
    file_update(fd, offset, to_bytes(used_page_id))


def set_head_page_id(fd: int, head_page_id: int) -> None:
    offset = META_PAGE_ID * BYTES_PAGE + BYTES_MAGIC_NUMBER + BYTES_USED_PAGE_ID
    file_update(fd, offset, to_bytes(head_page_id))


def set_tail_page_id(fd: int, tail_page_id: int) -> None:
    offset = META_PAGE_ID * BYTES_PAGE + BYTES_MAGIC_NUMBER + BYTES_USED_PAGE_ID + BYTES_HEAD_PAGE_ID
    file_update(fd, offset, to_bytes(tail_page_id))


def set_root_page_id(fd: int, root_page_id: int) -> None:
    offset = META_PAGE_ID * BYTES_PAGE + BYTES_MAGIC_NUMBER + BYTES_USED_PAGE_ID + BYTES_HEAD_PAGE_ID + BYTES_TAIL_PAGE_ID
    file_update(fd, offset, to_bytes(root_page_id))
