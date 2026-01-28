import io

from b_plus_tree import BPlusTreeNode, BPlusTree, new_b_plus_tree_node_from_page_id, new_b_plus_tree, new_b_plus_tree_from_root_page_id
from const import META_PAGE_ID, BYTES_MAGIC_NUMBER, MAGIC_NUMBER_BS
from file import file_open, get_page, set_magic_number
from id_generator import new_id_generator
from utils import from_bytes, to_bytes


def init() -> BPlusTree:
    fd = file_open('test.db')
    meta_bs = get_page(fd, META_PAGE_ID)
    meta_buf = io.BytesIO(meta_bs)
    magic_number_bs = meta_buf.read(BYTES_MAGIC_NUMBER)
    if magic_number_bs == MAGIC_NUMBER_BS:
        used_page_id = from_bytes(meta_buf, int)
        id_generator = new_id_generator(fd, used_page_id)
        root_page_id = from_bytes(meta_buf, int)
        b_plus_tree = new_b_plus_tree_from_root_page_id(fd, id_generator, root_page_id)
    else:
        set_magic_number(fd)
        id_generator = new_id_generator(fd, META_PAGE_ID)
        b_plus_tree = new_b_plus_tree(fd, id_generator)
    return b_plus_tree


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
            child = new_b_plus_tree_node_from_page_id(node.fd, node.id_generator, page_id)
            _show(child, count + 1)
    else:
        print(f'{indent}left:{node.left_page_id} right:{node.right_page_id}')
        print(f'{indent}vals:{node.vals}')


def test_set_1():
    b_plus_tree = init()
    b_plus_tree[b'1'] = b'1'


def test_set_2():
    b_plus_tree = init()
    b_plus_tree[b'1'] = b'1'
    b_plus_tree[b'2'] = b'2'
    b_plus_tree[b'3'] = b'3'


def test_set_3():
    b_plus_tree = init()
    b_plus_tree[b'1'] = b'1'
    b_plus_tree[b'2'] = b'2'
    b_plus_tree[b'3'] = b'3'
    b_plus_tree[b'4'] = b'4'


def test_set_4():
    b_plus_tree = init()
    b_plus_tree[b'1'] = b'1'
    b_plus_tree[b'2'] = b'2'
    b_plus_tree[b'3'] = b'3'
    b_plus_tree[b'4'] = b'4'
    b_plus_tree[b'5'] = b'5'
    b_plus_tree[b'6'] = b'6'


def test_set_5():
    b_plus_tree = init()
    b_plus_tree[b'1'] = b'1'
    b_plus_tree[b'2'] = b'2'
    b_plus_tree[b'3'] = b'3'
    b_plus_tree[b'4'] = b'4'
    b_plus_tree[b'5'] = b'5'
    b_plus_tree[b'6'] = b'6'
    b_plus_tree[b'7'] = b'7'
    b_plus_tree[b'8'] = b'8'


def test_set_6():
    b_plus_tree = init()
    b_plus_tree[b'a'] = b'a'
    b_plus_tree[b'b'] = b'b'
    b_plus_tree[b'c'] = b'c'
    b_plus_tree[b'd'] = b'd'
    b_plus_tree[b'e'] = b'e'
    b_plus_tree[b'f'] = b'f'
    b_plus_tree[b'g'] = b'g'
    b_plus_tree[b'h'] = b'h'
    b_plus_tree[b'i'] = b'i'
    b_plus_tree[b'j'] = b'j'
    show(b_plus_tree.root)


def test_get_1():
    b_plus_tree = init()
    b_plus_tree[b'1'] = b'1'
    r = b_plus_tree[b'1']
    assert r == b'1'


def test_get_2():
    b_plus_tree = init()
    b_plus_tree[b'1'] = b'1'
    b_plus_tree[b'2'] = b'2'
    b_plus_tree[b'3'] = b'3'
    r = b_plus_tree[b'1']
    assert r == b'1'
    r = b_plus_tree[b'2']
    assert r == b'2'
    r = b_plus_tree[b'3']
    assert r == b'3'


def test_get_3():
    b_plus_tree = init()
    b_plus_tree[b'1'] = b'1'
    b_plus_tree[b'2'] = b'2'
    b_plus_tree[b'3'] = b'3'
    b_plus_tree[b'4'] = b'4'
    r = b_plus_tree[b'1']
    assert r == b'1'
    r = b_plus_tree[b'2']
    assert r == b'2'
    r = b_plus_tree[b'3']
    assert r == b'3'
    r = b_plus_tree[b'4']
    assert r == b'4'


def test_get_4():
    b_plus_tree = init()
    b_plus_tree[b'1'] = b'1'
    b_plus_tree[b'2'] = b'2'
    b_plus_tree[b'3'] = b'3'
    b_plus_tree[b'4'] = b'4'
    b_plus_tree[b'5'] = b'5'
    b_plus_tree[b'6'] = b'6'
    r = b_plus_tree[b'1']
    assert r == b'1'
    r = b_plus_tree[b'2']
    assert r == b'2'
    r = b_plus_tree[b'3']
    assert r == b'3'
    r = b_plus_tree[b'4']
    assert r == b'4'
    r = b_plus_tree[b'5']
    assert r == b'5'
    r = b_plus_tree[b'6']
    assert r == b'6'


def test_get_5():
    b_plus_tree = init()
    b_plus_tree[b'1'] = b'1'
    b_plus_tree[b'2'] = b'2'
    b_plus_tree[b'3'] = b'3'
    b_plus_tree[b'4'] = b'4'
    b_plus_tree[b'5'] = b'5'
    b_plus_tree[b'6'] = b'6'
    b_plus_tree[b'7'] = b'7'
    b_plus_tree[b'8'] = b'8'
    r = b_plus_tree[b'1']
    assert r == b'1'
    r = b_plus_tree[b'2']
    assert r == b'2'
    r = b_plus_tree[b'3']
    assert r == b'3'
    r = b_plus_tree[b'4']
    assert r == b'4'
    r = b_plus_tree[b'5']
    assert r == b'5'
    r = b_plus_tree[b'6']
    assert r == b'6'
    r = b_plus_tree[b'7']
    assert r == b'7'
    r = b_plus_tree[b'8']
    assert r == b'8'


def test_get_6():
    b_plus_tree = init()
    b_plus_tree[b'a'] = b'a'
    b_plus_tree[b'b'] = b'b'
    b_plus_tree[b'c'] = b'c'
    b_plus_tree[b'd'] = b'd'
    b_plus_tree[b'e'] = b'e'
    b_plus_tree[b'f'] = b'f'
    b_plus_tree[b'g'] = b'g'
    b_plus_tree[b'h'] = b'h'
    b_plus_tree[b'i'] = b'i'
    b_plus_tree[b'j'] = b'j'
    r = b_plus_tree[b'a']
    assert r == b'a'
    r = b_plus_tree[b'b']
    assert r == b'b'
    r = b_plus_tree[b'c']
    assert r == b'c'
    r = b_plus_tree[b'd']
    assert r == b'd'
    r = b_plus_tree[b'e']
    assert r == b'e'
    r = b_plus_tree[b'f']
    assert r == b'f'
    r = b_plus_tree[b'g']
    assert r == b'g'
    r = b_plus_tree[b'h']
    assert r == b'h'
    r = b_plus_tree[b'i']
    assert r == b'i'
    r = b_plus_tree[b'j']
    assert r == b'j'


def test_delete_1():
    b_plus_tree = init()
    b_plus_tree[b'a'] = b'a'
    b_plus_tree[b'b'] = b'b'
    b_plus_tree[b'c'] = b'c'
    b_plus_tree[b'd'] = b'd'
    b_plus_tree[b'e'] = b'e'
    b_plus_tree[b'f'] = b'f'
    b_plus_tree[b'g'] = b'g'
    b_plus_tree[b'h'] = b'h'
    b_plus_tree[b'i'] = b'i'
    b_plus_tree[b'j'] = b'j'
    b_plus_tree[b'k'] = b'k'
    show(b_plus_tree.root)
    del b_plus_tree[b'k']
    show(b_plus_tree.root)


def test_delete_2():
    b_plus_tree = init()
    b_plus_tree[b'a'] = b'a'
    b_plus_tree[b'b'] = b'b'
    b_plus_tree[b'c'] = b'c'
    b_plus_tree[b'd'] = b'd'
    b_plus_tree[b'e'] = b'e'
    b_plus_tree[b'f'] = b'f'
    b_plus_tree[b'g'] = b'g'
    b_plus_tree[b'h'] = b'h'
    b_plus_tree[b'i'] = b'i'
    b_plus_tree[b'j'] = b'j'
    b_plus_tree[b'k'] = b'k'
    show(b_plus_tree.root)
    del b_plus_tree[b'k']
    del b_plus_tree[b'j']
    show(b_plus_tree.root)


def test_delete_3():
    b_plus_tree = init()
    b_plus_tree[b'a'] = b'a'
    b_plus_tree[b'b'] = b'b'
    b_plus_tree[b'c'] = b'c'
    b_plus_tree[b'd'] = b'd'
    b_plus_tree[b'e'] = b'e'
    b_plus_tree[b'f'] = b'f'
    b_plus_tree[b'g'] = b'g'
    b_plus_tree[b'h'] = b'h'
    b_plus_tree[b'i'] = b'i'
    b_plus_tree[b'j'] = b'j'
    b_plus_tree[b'k'] = b'k'
    show(b_plus_tree.root)
    del b_plus_tree[b'k']
    del b_plus_tree[b'j']
    del b_plus_tree[b'i']
    show(b_plus_tree.root)


def test_delete_4():
    b_plus_tree = init()
    b_plus_tree[b'a'] = b'a'
    b_plus_tree[b'b'] = b'b'
    b_plus_tree[b'c'] = b'c'
    b_plus_tree[b'd'] = b'd'
    b_plus_tree[b'e'] = b'e'
    b_plus_tree[b'f'] = b'f'
    b_plus_tree[b'g'] = b'g'
    b_plus_tree[b'h'] = b'h'
    b_plus_tree[b'i'] = b'i'
    b_plus_tree[b'j'] = b'j'
    b_plus_tree[b'k'] = b'k'
    show(b_plus_tree.root)
    del b_plus_tree[b'k']
    del b_plus_tree[b'j']
    del b_plus_tree[b'i']
    del b_plus_tree[b'h']
    show(b_plus_tree.root)


def test_delete_5():
    b_plus_tree = init()
    b_plus_tree[b'a'] = b'a'
    b_plus_tree[b'b'] = b'b'
    b_plus_tree[b'c'] = b'c'
    b_plus_tree[b'd'] = b'd'
    b_plus_tree[b'e'] = b'e'
    b_plus_tree[b'f'] = b'f'
    b_plus_tree[b'g'] = b'g'
    b_plus_tree[b'h'] = b'h'
    b_plus_tree[b'i'] = b'i'
    b_plus_tree[b'j'] = b'j'
    b_plus_tree[b'k'] = b'k'
    show(b_plus_tree.root)
    del b_plus_tree[b'k']
    del b_plus_tree[b'j']
    del b_plus_tree[b'i']
    del b_plus_tree[b'h']
    del b_plus_tree[b'g']
    show(b_plus_tree.root)


def test_delete_6():
    b_plus_tree = init()
    b_plus_tree[b'a'] = b'a'
    b_plus_tree[b'b'] = b'b'
    b_plus_tree[b'c'] = b'c'
    b_plus_tree[b'd'] = b'd'
    b_plus_tree[b'e'] = b'e'
    b_plus_tree[b'f'] = b'f'
    b_plus_tree[b'g'] = b'g'
    b_plus_tree[b'h'] = b'h'
    b_plus_tree[b'i'] = b'i'
    b_plus_tree[b'j'] = b'j'
    b_plus_tree[b'k'] = b'k'
    show(b_plus_tree.root)
    del b_plus_tree[b'k']
    del b_plus_tree[b'j']
    del b_plus_tree[b'i']
    del b_plus_tree[b'h']
    del b_plus_tree[b'g']
    del b_plus_tree[b'f']
    show(b_plus_tree.root)
