import os


def file_open(path: str) -> int:
    # O_BINARY 仅 Windows 存在，POSIX 下默认为二进制模式
    fd = os.open(path, os.O_RDWR | os.O_CREAT | getattr(os, 'O_BINARY', 0))
    return fd
