import os


def file_open(path: str) -> int:
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_BINARY)
    return fd
