import io
import os

from b_plus_tree import BPlusTreeNode, BPlusTree, new_b_plus_tree_node_from_page_id, new_b_plus_tree, new_b_plus_tree_from_root_page_id
from free_list import new_free_list, new_free_list_from_page_id
from const import META_PAGE_ID, BYTES_MAGIC_NUMBER, MAGIC_NUMBER_BS
from file import file_open, get_page, set_magic_number
from utils import from_buf


def init() -> tuple[int, BPlusTree]:
    fd = file_open('test.db')
    meta_bs = get_page(fd, META_PAGE_ID)
    meta_buf = io.BytesIO(meta_bs)
    magic_number_bs = meta_buf.read(BYTES_MAGIC_NUMBER)
    if magic_number_bs == MAGIC_NUMBER_BS:
        used_page_id = from_buf(meta_buf, int)
        head_page_id = from_buf(meta_buf, int)
        tail_page_id = from_buf(meta_buf, int)
        free_list = new_free_list_from_page_id(fd, used_page_id, head_page_id, tail_page_id)
        root_page_id = from_buf(meta_buf, int)
        b_plus_tree = new_b_plus_tree_from_root_page_id(fd, free_list, root_page_id)
    else:
        set_magic_number(fd)
        free_list = new_free_list(fd, META_PAGE_ID)
        b_plus_tree = new_b_plus_tree(fd, free_list)
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
            child = new_b_plus_tree_node_from_page_id(node.fd, node.free_list, page_id)
            _show(child, count + 1)
    else:
        print(f'{indent}left:{node.left_page_id} right:{node.right_page_id}')
        print(f'{indent}vals:{node.vals}')


def close(fd: int) -> None:
    os.close(fd)
    os.remove('test.db')


def test_set_1():
    fd, b_plus_tree = init()
    b_plus_tree[b'1'] = b'1'
    close(fd)


def test_set_2():
    fd, b_plus_tree = init()
    for o in [b'1', b'2', b'3']:
        b_plus_tree[o] = o
    close(fd)


def test_set_3():
    fd, b_plus_tree = init()
    for o in [b'1', b'2', b'3', b'4']:
        b_plus_tree[o] = o
    close(fd)


def test_set_4():
    fd, b_plus_tree = init()
    for o in [b'1', b'2', b'3', b'4', b'5', b'6']:
        b_plus_tree[o] = o
    close(fd)


def test_set_5():
    fd, b_plus_tree = init()
    for o in [b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8']:
        b_plus_tree[o] = o
    close(fd)


def test_set_6():
    fd, b_plus_tree = init()
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j']:
        b_plus_tree[o] = o
    show(b_plus_tree.root)
    close(fd)


def test_get_1():
    fd, b_plus_tree = init()
    b_plus_tree[b'1'] = b'1'
    r = b_plus_tree[b'1']
    assert r == b'1'
    close(fd)


def test_get_2():
    fd, b_plus_tree = init()
    for o in [b'1', b'2', b'3']:
        b_plus_tree[o] = o
    for o in [b'1', b'2', b'3']:
        r = b_plus_tree[o]
        assert r == o
    close(fd)


def test_get_3():
    fd, b_plus_tree = init()
    for o in [b'1', b'2', b'3', b'4']:
        b_plus_tree[o] = o
    for o in [b'1', b'2', b'3', b'4']:
        r = b_plus_tree[o]
        assert r == o
    close(fd)


def test_get_4():
    fd, b_plus_tree = init()
    for o in [b'1', b'2', b'3', b'4', b'5', b'6']:
        b_plus_tree[o] = o
    for o in [b'1', b'2', b'3', b'4', b'5', b'6']:
        r = b_plus_tree[o]
        assert r == o
    close(fd)


def test_get_5():
    fd, b_plus_tree = init()
    for o in [b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8']:
        b_plus_tree[o] = o
    for o in [b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8']:
        r = b_plus_tree[o]
        assert r == o
    close(fd)


def test_get_6():
    fd, b_plus_tree = init()
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j']:
        b_plus_tree[o] = o
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j']:
        r = b_plus_tree[o]
        assert r == o
    close(fd)


def test_delete_1():
    fd, b_plus_tree = init()
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree[o] = o
    show(b_plus_tree.root)
    del b_plus_tree[b'k']
    show(b_plus_tree.root)
    close(fd)


def test_delete_2():
    fd, b_plus_tree = init()
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree[o] = o
    show(b_plus_tree.root)
    for o in [b'k', b'j']:
        del b_plus_tree[o]
    show(b_plus_tree.root)


def test_delete_3():
    fd, b_plus_tree = init()
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree[o] = o
    show(b_plus_tree.root)
    for o in [b'k', b'j', b'i']:
        del b_plus_tree[o]
    show(b_plus_tree.root)
    close(fd)


def test_delete_4():
    fd, b_plus_tree = init()
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree[o] = o
    show(b_plus_tree.root)
    for o in [b'k', b'j', b'i', b'h']:
        del b_plus_tree[o]
    show(b_plus_tree.root)
    close(fd)


def test_delete_5():
    fd, b_plus_tree = init()
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree[o] = o
    show(b_plus_tree.root)
    for o in [b'k', b'j', b'i', b'h', b'g']:
        del b_plus_tree[o]
    show(b_plus_tree.root)
    close(fd)


def test_delete_6():
    fd, b_plus_tree = init()
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree[o] = o
    show(b_plus_tree.root)
    for o in [b'k', b'j', b'i', b'h', b'g', b'f']:
        del b_plus_tree[o]
    show(b_plus_tree.root)
    close(fd)


def test_delete_7():
    fd, b_plus_tree = init()
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree[o] = o
    show(b_plus_tree.root)
    for o in [b'k', b'j', b'i', b'h', b'g', b'f', b'e']:
        del b_plus_tree[o]
    show(b_plus_tree.root)
    close(fd)


def test_delete_8():
    fd, b_plus_tree = init()
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree[o] = o
    show(b_plus_tree.root)
    for o in [b'k', b'j', b'i', b'h', b'g', b'f', b'e', b'd']:
        del b_plus_tree[o]
    show(b_plus_tree.root)
    close(fd)


def test_delete_9():
    fd, b_plus_tree = init()
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree[o] = o
    show(b_plus_tree.root)
    for o in [b'k', b'j', b'i', b'h', b'g', b'f', b'e', b'd', b'c']:
        del b_plus_tree[o]
    show(b_plus_tree.root)
    close(fd)


def test_delete_10():
    fd, b_plus_tree = init()
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree[o] = o
    show(b_plus_tree.root)
    for o in [b'k', b'j', b'i', b'h', b'g', b'f', b'e', b'd', b'c', b'b']:
        del b_plus_tree[o]
    show(b_plus_tree.root)
    close(fd)


def test_delete_11():
    fd, b_plus_tree = init()
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree[o] = o
    show(b_plus_tree.root)
    for o in [b'k', b'j', b'i', b'h', b'g', b'f', b'e', b'd', b'c', b'b', b'a']:
        del b_plus_tree[o]
    show(b_plus_tree.root)
    close(fd)

