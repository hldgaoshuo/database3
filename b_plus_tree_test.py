import inspect
import os
import pytest

from b_plus_tree import BPlusTreeNode, BPlusTree, new_b_plus_tree_node_from_page_id, new_b_plus_tree, new_b_plus_tree_from_root_page_id
from free_list import new_free_list, new_free_list_from_page_id
from const import META_PAGE_ID, BYTES_MAGIC_NUMBER, MAGIC_NUMBER_BS
from file import file_open
from pager import new_pager
from utils import from_buf


def init(name: str) -> tuple[int, BPlusTree]:
    seq = 0
    fd = file_open(f'{name}.db')
    pager = new_pager(fd)
    meta = pager.page_get(META_PAGE_ID)
    magic_number_bs = meta.read(BYTES_MAGIC_NUMBER)
    if magic_number_bs == MAGIC_NUMBER_BS:
        used_page_id = from_buf(meta, int)
        head_page_id = from_buf(meta, int)
        tail_page_id = from_buf(meta, int)
        free_list = new_free_list_from_page_id(pager, used_page_id, head_page_id, tail_page_id)
        from_buf(meta, int)  # table_seq
        from_buf(meta, int)  # table_head_page_id
        from_buf(meta, int)  # table_tail_page_id
        root_page_id = from_buf(meta, int)
        b_plus_tree = new_b_plus_tree_from_root_page_id(pager, seq, free_list, root_page_id)
    else:
        pager.magic_number_set()
        free_list = new_free_list(pager, META_PAGE_ID)
        b_plus_tree = new_b_plus_tree(pager, seq, free_list)
    return fd, b_plus_tree


def show(node: BPlusTreeNode) -> None:
    print()
    _show(node, 0)


def _show(node: BPlusTreeNode, count: int) -> None:
    indent = '---- ' * count
    keys = ','.join([str(k) for k in node.keys])
    print(f'{indent}key:{keys} page_id:{node.page_id}')
    print(f'{indent}left:{node.left_page_id} right:{node.right_page_id}')
    if not node.is_leaf:
        for page_id in node.page_ids:
            child = new_b_plus_tree_node_from_page_id(node.pager, node.free_list, page_id)
            _show(child, count + 1)
    else:
        print(f'{indent}left:{node.left_page_id} right:{node.right_page_id}')
        print(f'{indent}vals:{node.vals}')


def close(fd: int, name: str) -> None:
    os.close(fd)
    os.remove(f'{name}.db')


def test_add_1():
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    b_plus_tree.add([(b'1', b'1')])
    close(fd, name)


def test_add_2():
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'1', b'2', b'3']:
        b_plus_tree.add([(o, o)])
    close(fd, name)


def test_add_3():
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'1', b'2', b'3', b'4']:
        b_plus_tree.add([(o, o)])
    close(fd, name)


def test_add_4():
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'1', b'2', b'3', b'4', b'5', b'6']:
        b_plus_tree.add([(o, o)])
    close(fd, name)


def test_add_5():
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8']:
        b_plus_tree.add([(o, o)])
    close(fd, name)


def test_add_6():
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j']:
        b_plus_tree.add([(o, o)])
    show(b_plus_tree.root)
    close(fd, name)


def test_get_one_1():
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    b_plus_tree.add([(b'1', b'1')])
    r = b_plus_tree.get_one(b'1')
    assert r == b'1'
    close(fd, name)


def test_get_one_2():
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'1', b'2', b'3']:
        b_plus_tree.add([(o, o)])
    for o in [b'1', b'2', b'3']:
        r = b_plus_tree.get_one(o)
        assert r == o
    close(fd, name)


def test_get_one_3():
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'1', b'2', b'3', b'4']:
        b_plus_tree.add([(o, o)])
    for o in [b'1', b'2', b'3', b'4']:
        r = b_plus_tree.get_one(o)
        assert r == o
    close(fd, name)


def test_get_one_4():
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'1', b'2', b'3', b'4', b'5', b'6']:
        b_plus_tree.add([(o, o)])
    for o in [b'1', b'2', b'3', b'4', b'5', b'6']:
        r = b_plus_tree.get_one(o)
        assert r == o
    close(fd, name)


def test_get_one_5():
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8']:
        b_plus_tree.add([(o, o)])
    for o in [b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8']:
        r = b_plus_tree.get_one(o)
        assert r == o
    close(fd, name)


def test_get_one_6():
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j']:
        b_plus_tree.add([(o, o)])
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j']:
        r = b_plus_tree.get_one(o)
        assert r == o
    close(fd, name)


def test_delete_one_1():
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree.add([(o, o)])
    show(b_plus_tree.root)
    b_plus_tree.delete_one(b'k')
    show(b_plus_tree.root)
    close(fd, name)


def test_delete_one_2():
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree.add([(o, o)])
    show(b_plus_tree.root)
    for o in [b'k', b'j']:
        b_plus_tree.delete_one(o)
    show(b_plus_tree.root)
    close(fd, name)


def test_delete_one_3():
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree.add([(o, o)])
    show(b_plus_tree.root)
    for o in [b'k', b'j', b'i']:
        b_plus_tree.delete_one(o)
    show(b_plus_tree.root)
    close(fd, name)


def test_delete_one_4():
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree.add([(o, o)])
    show(b_plus_tree.root)
    for o in [b'k', b'j', b'i', b'h']:
        b_plus_tree.delete_one(o)
    show(b_plus_tree.root)
    close(fd, name)


def test_delete_one_5():
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree.add([(o, o)])
    show(b_plus_tree.root)
    for o in [b'k', b'j', b'i', b'h', b'g']:
        b_plus_tree.delete_one(o)
    show(b_plus_tree.root)
    close(fd, name)


def test_delete_one_6():
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree.add([(o, o)])
    show(b_plus_tree.root)
    for o in [b'k', b'j', b'i', b'h', b'g', b'f']:
        b_plus_tree.delete_one(o)
    show(b_plus_tree.root)
    close(fd, name)


def test_delete_one_7():
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree.add([(o, o)])
    show(b_plus_tree.root)
    for o in [b'k', b'j', b'i', b'h', b'g', b'f', b'e']:
        b_plus_tree.delete_one(o)
    show(b_plus_tree.root)
    close(fd, name)


def test_delete_one_8():
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree.add([(o, o)])
    show(b_plus_tree.root)
    for o in [b'k', b'j', b'i', b'h', b'g', b'f', b'e', b'd']:
        b_plus_tree.delete_one(o)
    show(b_plus_tree.root)
    close(fd, name)


def test_delete_one_9():
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree.add([(o, o)])
    show(b_plus_tree.root)
    for o in [b'k', b'j', b'i', b'h', b'g', b'f', b'e', b'd', b'c']:
        b_plus_tree.delete_one(o)
    show(b_plus_tree.root)
    close(fd, name)


def test_delete_one_10():
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree.add([(o, o)])
    show(b_plus_tree.root)
    for o in [b'k', b'j', b'i', b'h', b'g', b'f', b'e', b'd', b'c', b'b']:
        b_plus_tree.delete_one(o)
    show(b_plus_tree.root)
    close(fd, name)


def test_delete_one_11():
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree.add([(o, o)])
    show(b_plus_tree.root)
    for o in [b'k', b'j', b'i', b'h', b'g', b'f', b'e', b'd', b'c', b'b', b'a']:
        b_plus_tree.delete_one(o)
    show(b_plus_tree.root)
    close(fd, name)


if __name__ == "__main__":
    pytest.main([__file__])
