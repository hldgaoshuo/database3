from kv import new_kv
from utils import from_bytes


def init():
    kv = new_kv('test')
    return kv


def test_init():
    kv = init()


def test_set():
    kv = init()
    kv[1] = 1


def test_get():
    kv = init()
    kv[1] = 1
    assert from_bytes(kv[1], int) == 1
    kv["a"] = "a"
    assert from_bytes(kv["a"], str) == "a"
    kv[2] = "b"
    assert from_bytes(kv[2], str) == "b"
    kv["b"] = 2
    assert from_bytes(kv["b"], int) == 2
