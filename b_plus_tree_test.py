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
        from_buf(meta, int)  # b_plus_tree_seq
        from_buf(meta, int)  # table_head_page_id
        from_buf(meta, int)  # table_tail_page_id
        root_page_id = from_buf(meta, int)
        b_plus_tree = new_b_plus_tree_from_root_page_id(pager, free_list, seq, root_page_id)
    else:
        pager.magic_number_set()
        free_list = new_free_list(pager, META_PAGE_ID)
        b_plus_tree = new_b_plus_tree(pager, free_list, seq)
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


# ──────────────────────────────────────────────
# delete_lt 测试
# ──────────────────────────────────────────────

def test_delete_lt_1_no_match():
    """delete_lt(key) 中 key 小于所有元素，不删任何东西"""
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'c', b'd', b'e', b'f', b'g']:
        b_plus_tree.add([(o, o)])
    b_plus_tree.delete_lt(b'a')
    show(b_plus_tree.root)
    for o in [b'c', b'd', b'e', b'f', b'g']:
        assert b_plus_tree.get_one(o) == o
    close(fd, name)


def test_delete_lt_2_delete_all():
    """delete_lt(key) 中 key 大于所有元素，删除全部"""
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e']:
        b_plus_tree.add([(o, o)])
    b_plus_tree.delete_lt(b'z')
    show(b_plus_tree.root)
    assert b_plus_tree.get_all() == []
    close(fd, name)


def test_delete_lt_3_single_leaf():
    """单叶节点（不触发分裂），删除部分"""
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'1', b'2', b'3']:
        b_plus_tree.add([(o, o)])
    b_plus_tree.delete_lt(b'2')
    show(b_plus_tree.root)
    assert b_plus_tree.get_one(b'1') is None
    assert b_plus_tree.get_one(b'2') == b'2'
    assert b_plus_tree.get_one(b'3') == b'3'
    close(fd, name)


def test_delete_lt_4_multi_level_delete_left_subtrees():
    """多层树，删除若干整棵左子树"""
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree.add([(o, o)])
    show(b_plus_tree.root)
    b_plus_tree.delete_lt(b'e')
    show(b_plus_tree.root)
    for o in [b'a', b'b', b'c', b'd']:
        assert b_plus_tree.get_one(o) is None, f"{o} should be deleted"
    for o in [b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        assert b_plus_tree.get_one(o) == o, f"{o} should exist"
    close(fd, name)


def test_delete_lt_5_delete_within_leaf():
    """delete_lt 的切割点落在叶节点中间"""
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j']:
        b_plus_tree.add([(o, o)])
    show(b_plus_tree.root)
    b_plus_tree.delete_lt(b'c')
    show(b_plus_tree.root)
    assert b_plus_tree.get_one(b'a') is None
    assert b_plus_tree.get_one(b'b') is None
    for o in [b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j']:
        assert b_plus_tree.get_one(o) == o
    close(fd, name)


def test_delete_lt_6_tree_height_shrinks():
    """删除大量数据后树高度应该收缩"""
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree.add([(o, o)])
    show(b_plus_tree.root)
    # 删除绝大多数，只留最后一个
    b_plus_tree.delete_lt(b'k')
    show(b_plus_tree.root)
    assert b_plus_tree.root.is_leaf, "树应该收缩到只剩一个叶节点（根即叶）"
    assert b_plus_tree.get_one(b'k') == b'k'
    close(fd, name)


def test_delete_lt_7_key_is_exact_boundary():
    """delete_lt(k) 恰好等于某个 key：该 key 本身不被删除"""
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h']:
        b_plus_tree.add([(o, o)])
    b_plus_tree.delete_lt(b'd')
    show(b_plus_tree.root)
    assert b_plus_tree.get_one(b'd') == b'd', "边界值 d 不应被删除"
    for o in [b'a', b'b', b'c']:
        assert b_plus_tree.get_one(o) is None
    for o in [b'd', b'e', b'f', b'g', b'h']:
        assert b_plus_tree.get_one(o) == o
    close(fd, name)


def test_delete_lt_8_get_all_consistent():
    """delete_lt 后 get_all 返回的结果应与逐个 get_one 一致"""
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    keys = [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j']
    for o in keys:
        b_plus_tree.add([(o, o)])
    b_plus_tree.delete_lt(b'f')
    show(b_plus_tree.root)
    remaining = [o for o in keys if o >= b'f']
    assert b_plus_tree.get_all() == remaining
    close(fd, name)


# ──────────────────────────────────────────────
# delete_le 测试
# ──────────────────────────────────────────────

def test_delete_le_1_no_match():
    """delete_le(key) 中 key 小于所有元素，不删任何东西"""
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'c', b'd', b'e', b'f', b'g']:
        b_plus_tree.add([(o, o)])
    b_plus_tree.delete_le(b'a')
    show(b_plus_tree.root)
    for o in [b'c', b'd', b'e', b'f', b'g']:
        assert b_plus_tree.get_one(o) == o
    close(fd, name)


def test_delete_le_2_delete_all():
    """delete_le(key) 中 key >= 最大元素，删除全部"""
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e']:
        b_plus_tree.add([(o, o)])
    b_plus_tree.delete_le(b'e')
    show(b_plus_tree.root)
    assert b_plus_tree.get_all() == []
    close(fd, name)


def test_delete_le_3_boundary_deleted():
    """delete_le 的边界值本身也被删除（le = less than or equal）"""
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'1', b'2', b'3', b'4', b'5']:
        b_plus_tree.add([(o, o)])
    b_plus_tree.delete_le(b'3')
    show(b_plus_tree.root)
    assert b_plus_tree.get_one(b'1') is None
    assert b_plus_tree.get_one(b'2') is None
    assert b_plus_tree.get_one(b'3') is None  # 边界值也被删
    assert b_plus_tree.get_one(b'4') == b'4'
    assert b_plus_tree.get_one(b'5') == b'5'
    close(fd, name)


def test_delete_le_4_multi_level():
    """多层树，delete_le 删除左侧整棵子树"""
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree.add([(o, o)])
    show(b_plus_tree.root)
    b_plus_tree.delete_le(b'e')
    show(b_plus_tree.root)
    for o in [b'a', b'b', b'c', b'd', b'e']:
        assert b_plus_tree.get_one(o) is None, f"{o} should be deleted"
    for o in [b'f', b'g', b'h', b'i', b'j', b'k']:
        assert b_plus_tree.get_one(o) == o, f"{o} should exist"
    close(fd, name)


def test_delete_le_5_tree_height_shrinks():
    """delete_le 删除绝大多数后树高收缩"""
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree.add([(o, o)])
    b_plus_tree.delete_le(b'j')
    show(b_plus_tree.root)
    assert b_plus_tree.root.is_leaf, "只剩一个元素，树应收缩为叶节点"
    assert b_plus_tree.get_one(b'k') == b'k'
    close(fd, name)


def test_delete_le_6_get_all_consistent():
    """delete_le 后 get_all 结果正确"""
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    keys = [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j']
    for o in keys:
        b_plus_tree.add([(o, o)])
    b_plus_tree.delete_le(b'd')
    show(b_plus_tree.root)
    remaining = [o for o in keys if o > b'd']
    assert b_plus_tree.get_all() == remaining
    close(fd, name)


# ──────────────────────────────────────────────
# delete_gt 测试
# ──────────────────────────────────────────────

def test_delete_gt_1_no_match():
    """delete_gt(key) 中 key >= 最大元素，不删任何东西"""
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e']:
        b_plus_tree.add([(o, o)])
    b_plus_tree.delete_gt(b'z')
    show(b_plus_tree.root)
    for o in [b'a', b'b', b'c', b'd', b'e']:
        assert b_plus_tree.get_one(o) == o
    close(fd, name)


def test_delete_gt_2_delete_all():
    """delete_gt(key) 中 key 小于所有元素，删除全部"""
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e']:
        b_plus_tree.add([(o, o)])
    b_plus_tree.delete_gt(b'0')
    show(b_plus_tree.root)
    assert b_plus_tree.get_all() == []
    close(fd, name)


def test_delete_gt_3_boundary_kept():
    """delete_gt 的边界值本身不被删除（gt = strictly greater than）"""
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'1', b'2', b'3', b'4', b'5']:
        b_plus_tree.add([(o, o)])
    b_plus_tree.delete_gt(b'3')
    show(b_plus_tree.root)
    assert b_plus_tree.get_one(b'3') == b'3'   # 边界值保留
    assert b_plus_tree.get_one(b'4') is None
    assert b_plus_tree.get_one(b'5') is None
    assert b_plus_tree.get_one(b'1') == b'1'
    assert b_plus_tree.get_one(b'2') == b'2'
    close(fd, name)


def test_delete_gt_4_multi_level():
    """多层树，delete_gt 删除右侧整棵子树"""
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree.add([(o, o)])
    show(b_plus_tree.root)
    b_plus_tree.delete_gt(b'g')
    show(b_plus_tree.root)
    for o in [b'h', b'i', b'j', b'k']:
        assert b_plus_tree.get_one(o) is None, f"{o} should be deleted"
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g']:
        assert b_plus_tree.get_one(o) == o, f"{o} should exist"
    close(fd, name)


def test_delete_gt_5_tree_height_shrinks():
    """delete_gt 删除绝大多数后树高收缩"""
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree.add([(o, o)])
    b_plus_tree.delete_gt(b'a')
    show(b_plus_tree.root)
    assert b_plus_tree.root.is_leaf, "只剩一个元素，树应收缩为叶节点"
    assert b_plus_tree.get_one(b'a') == b'a'
    close(fd, name)


def test_delete_gt_6_get_all_consistent():
    """delete_gt 后 get_all 结果正确"""
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    keys = [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j']
    for o in keys:
        b_plus_tree.add([(o, o)])
    b_plus_tree.delete_gt(b'f')
    show(b_plus_tree.root)
    remaining = [o for o in keys if o <= b'f']
    assert b_plus_tree.get_all() == remaining
    close(fd, name)


def test_delete_gt_7_delete_within_leaf():
    """切割点落在叶节点中间"""
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h']:
        b_plus_tree.add([(o, o)])
    b_plus_tree.delete_gt(b'e')
    show(b_plus_tree.root)
    for o in [b'f', b'g', b'h']:
        assert b_plus_tree.get_one(o) is None
    for o in [b'a', b'b', b'c', b'd', b'e']:
        assert b_plus_tree.get_one(o) == o
    close(fd, name)


# ──────────────────────────────────────────────
# delete_ge 测试
# ──────────────────────────────────────────────

def test_delete_ge_1_no_match():
    """delete_ge(key) 中 key > 最大元素，不删任何东西"""
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e']:
        b_plus_tree.add([(o, o)])
    b_plus_tree.delete_ge(b'z')
    show(b_plus_tree.root)
    for o in [b'a', b'b', b'c', b'd', b'e']:
        assert b_plus_tree.get_one(o) == o
    close(fd, name)


def test_delete_ge_2_delete_all():
    """delete_ge(key) 中 key <= 最小元素，删除全部"""
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e']:
        b_plus_tree.add([(o, o)])
    b_plus_tree.delete_ge(b'a')
    show(b_plus_tree.root)
    assert b_plus_tree.get_all() == []
    close(fd, name)


def test_delete_ge_3_boundary_deleted():
    """delete_ge 的边界值本身也被删除（ge = greater than or equal）"""
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'1', b'2', b'3', b'4', b'5']:
        b_plus_tree.add([(o, o)])
    b_plus_tree.delete_ge(b'3')
    show(b_plus_tree.root)
    assert b_plus_tree.get_one(b'3') is None   # 边界值也被删
    assert b_plus_tree.get_one(b'4') is None
    assert b_plus_tree.get_one(b'5') is None
    assert b_plus_tree.get_one(b'1') == b'1'
    assert b_plus_tree.get_one(b'2') == b'2'
    close(fd, name)


def test_delete_ge_4_multi_level():
    """多层树，delete_ge 删除右侧整棵子树"""
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree.add([(o, o)])
    show(b_plus_tree.root)
    b_plus_tree.delete_ge(b'g')
    show(b_plus_tree.root)
    for o in [b'g', b'h', b'i', b'j', b'k']:
        assert b_plus_tree.get_one(o) is None, f"{o} should be deleted"
    for o in [b'a', b'b', b'c', b'd', b'e', b'f']:
        assert b_plus_tree.get_one(o) == o, f"{o} should exist"
    close(fd, name)


def test_delete_ge_5_tree_height_shrinks():
    """delete_ge 删除绝大多数后树高收缩"""
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j', b'k']:
        b_plus_tree.add([(o, o)])
    b_plus_tree.delete_ge(b'b')
    show(b_plus_tree.root)
    assert b_plus_tree.root.is_leaf, "只剩一个元素，树应收缩为叶节点"
    assert b_plus_tree.get_one(b'a') == b'a'
    close(fd, name)


def test_delete_ge_6_get_all_consistent():
    """delete_ge 后 get_all 结果正确"""
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    keys = [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h', b'i', b'j']
    for o in keys:
        b_plus_tree.add([(o, o)])
    b_plus_tree.delete_ge(b'f')
    show(b_plus_tree.root)
    remaining = [o for o in keys if o < b'f']
    assert b_plus_tree.get_all() == remaining
    close(fd, name)


def test_delete_ge_7_delete_within_leaf():
    """切割点落在叶节点中间"""
    name = inspect.currentframe().f_code.co_name
    fd, b_plus_tree = init(name)
    for o in [b'a', b'b', b'c', b'd', b'e', b'f', b'g', b'h']:
        b_plus_tree.add([(o, o)])
    b_plus_tree.delete_ge(b'f')
    show(b_plus_tree.root)
    for o in [b'f', b'g', b'h']:
        assert b_plus_tree.get_one(o) is None
    for o in [b'a', b'b', b'c', b'd', b'e']:
        assert b_plus_tree.get_one(o) == o
    close(fd, name)


if __name__ == "__main__":
    pytest.main([__file__])
