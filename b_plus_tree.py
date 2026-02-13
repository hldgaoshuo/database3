from const import NULL_PAGE_ID, DEGREE
from free_list import FreeList
from pager import Pager
from utils import to_bytes, from_buf


class BPlusTreeNode:

    def __init__(self, pager: Pager, free_list: FreeList, is_leaf: bool, page_id: int, left_page_id: int,
                 right_page_id: int):
        self.pager: Pager = pager
        self.free_list: FreeList = free_list
        self.is_leaf: bool = is_leaf
        self.page_id: int = page_id
        self.left_page_id: int = left_page_id
        self.right_page_id: int = right_page_id
        self.keys: list[bytes] = []
        self.vals: list[bytes] = []
        self.page_ids: list[int] = []

    def __bytes__(self) -> bytes:
        r = b''
        r += to_bytes(self.is_leaf)
        r += to_bytes(self.page_id)
        r += to_bytes(self.left_page_id)
        r += to_bytes(self.right_page_id)
        r += to_bytes(len(self.keys))
        for key in self.keys:
            r += to_bytes(key)
        if self.is_leaf:
            r += to_bytes(len(self.vals))
            for val in self.vals:
                r += to_bytes(val)
        else:
            r += to_bytes(len(self.page_ids))
            for page_id in self.page_ids:
                r += to_bytes(page_id)
        return r

    def get_lt(self, key: bytes) -> list[bytes]:
        if self.is_leaf:
            result = self._get_lt(key)
            return result
        index = self.get_page_id_index(key)
        page_id = self.page_ids[index]
        child = new_b_plus_tree_node_from_page_id(self.pager, self.free_list, page_id)
        result = child.get_lt(key)
        return result

    def _get_lt(self, key: bytes) -> list[bytes]:
        result = []
        i = len(self.keys) - 1
        while i >= 0 and self.keys[i] >= key:
            i = i - 1
        # while i >= 0:
        #     val = self.vals[i]
        #     result.append(val)
        #     i = i - 1
        if i >= 0:
            vals = self.vals[:i + 1]
            result.extend(vals)
        result_left = self._get_left()
        result = result_left + result
        return result

    def get_le(self, key: bytes) -> list[bytes]:
        if self.is_leaf:
            result = self._get_le(key)
            return result
        index = self.get_page_id_index(key)
        page_id = self.page_ids[index]
        child = new_b_plus_tree_node_from_page_id(self.pager, self.free_list, page_id)
        result = child.get_le(key)
        return result

    def _get_le(self, key: bytes) -> list[bytes]:
        result = []
        i = len(self.keys) - 1
        while i >= 0 and self.keys[i] > key:
            i = i - 1
        # while i >= 0:
        #     val = self.vals[i]
        #     result.append(val)
        #     i = i - 1
        if i >= 0:
            vals = self.vals[:i + 1]
            result.extend(vals)
        result_left = self._get_left()
        result = result_left + result
        return result

    def get_gt(self, key: bytes) -> list[bytes]:
        if self.is_leaf:
            result = self._get_gt(key)
            return result
        index = self.get_page_id_index(key)
        page_id = self.page_ids[index]
        child = new_b_plus_tree_node_from_page_id(self.pager, self.free_list, page_id)
        result = child.get_gt(key)
        return result

    def _get_gt(self, key: bytes) -> list[bytes]:
        result = []
        i = 0
        while i < len(self.keys) and self.keys[i] <= key:
            i = i + 1
        # while i < len(self.keys):
        #     val = self.vals[i]
        #     result.append(val)
        #     i = i + 1
        if i < len(self.keys):
            vals = self.vals[i:]
            result.extend(vals)
        result_right = self._get_right()
        result.extend(result_right)
        return result

    def get_ge(self, key: bytes) -> list[bytes]:
        if self.is_leaf:
            result = self._get_ge(key)
            return result
        index = self.get_page_id_index(key)
        page_id = self.page_ids[index]
        child = new_b_plus_tree_node_from_page_id(self.pager, self.free_list, page_id)
        result = child.get_ge(key)
        return result

    def _get_ge(self, key: bytes) -> list[bytes]:
        result = []
        i = 0
        while i < len(self.keys) and self.keys[i] < key:
            i = i + 1
        # while i < len(self.keys):
        #     val = self.vals[i]
        #     result.append(val)
        #     i = i + 1
        if i < len(self.keys):
            vals = self.vals[i:]
            result.extend(vals)
        result_right = self._get_right()
        result.extend(result_right)
        return result

    def _get_left(self) -> list[bytes]:
        result = []
        node = self
        while node.left_page_id != NULL_PAGE_ID:
            node = new_b_plus_tree_node_from_page_id(self.pager, self.free_list, node.left_page_id)
            result = node.vals + result
        return result

    def _get_right(self) -> list[bytes]:
        result = []
        node = self
        while node.right_page_id != NULL_PAGE_ID:
            node = new_b_plus_tree_node_from_page_id(self.pager, self.free_list, node.right_page_id)
            result.extend(node.vals)
        return result

    def get_one(self, key: bytes) -> bytes | None:
        if self.is_leaf:
            result = self._get_one(key)
            return result
        index = self.get_page_id_index(key)
        page_id = self.page_ids[index]
        child = new_b_plus_tree_node_from_page_id(self.pager, self.free_list, page_id)
        result = child.get_one(key)
        return result

    def _get_one(self, key: bytes) -> bytes | None:
        try:
            i = self.keys.index(key)
        except ValueError:
            return None
        val = self.vals[i]
        return val

    def get_page_id_index(self, key: bytes) -> int:
        i = len(self.keys) - 1
        while i >= 0 and key < self.keys[i]:
            i = i - 1
        i = i + 1
        return i

    def add(self, key: bytes, val: bytes) -> None:
        if self.is_leaf:
            self._add(key, val)
            self.persist()
            return

        index = self.get_page_id_index(key)
        page_id = self.page_ids[index]
        child = new_b_plus_tree_node_from_page_id(self.pager, self.free_list, page_id)
        if not child.is_full():
            child.add(key, val)
            return

        # self not leaf
        # child is full
        if child.is_leaf:
            self.keys.insert(index, child.keys[DEGREE])
        else:
            self.keys.insert(index, child.keys[DEGREE - 1])
        child_new = child.split()
        self.page_ids.insert(index + 1, child_new.page_id)
        self.persist()
        if key > self.keys[index]:
            child_new.add(key, val)
        else:
            child.add(key, val)
        return

    def _add(self, key: bytes, val: bytes) -> None:
        i = len(self.keys) - 1
        while i >= 0 and key < self.keys[i]:
            i = i - 1
        if not (i >= 0 and key == self.keys[i]):
            i = i + 1
            self.keys.insert(i, key)
            self.vals.insert(i, val)

    def upsert(self, key: bytes, val: bytes) -> None:
        if self.is_leaf:
            self._upsert(key, val)
            self.persist()
            return

        index = self.get_page_id_index(key)
        page_id = self.page_ids[index]
        child = new_b_plus_tree_node_from_page_id(self.pager, self.free_list, page_id)
        if not child.is_full():
            child.upsert(key, val)
            return

        # self not leaf
        # child is full
        if child.is_leaf:
            self.keys.insert(index, child.keys[DEGREE])
        else:
            self.keys.insert(index, child.keys[DEGREE - 1])
        child_new = child.split()
        self.page_ids.insert(index + 1, child_new.page_id)
        self.persist()
        if key > self.keys[index]:
            child_new.upsert(key, val)
        else:
            child.upsert(key, val)
        return

    def _upsert(self, key: bytes, val: bytes) -> None:
        i = len(self.keys) - 1
        while i >= 0 and key < self.keys[i]:
            i = i - 1
        if i >= 0 and key == self.keys[i]:
            self.vals[i] = val
        else:
            i = i + 1
            self.keys.insert(i, key)
            self.vals.insert(i, val)

    def update_lt(self, key_search: bytes, index: int, val: bytes) -> None:
        if self.is_leaf:
            self._update_lt(key_search, index, val)
            self.persist()
            return

        index = self.get_page_id_index(key_search)
        page_id = self.page_ids[index]
        child = new_b_plus_tree_node_from_page_id(self.pager, self.free_list, page_id)
        child.update_lt(key_search, index, val)
        return

    def _update_lt(self, key_search: bytes, index: int, val: bytes) -> None:
        i = len(self.keys) - 1
        while i >= 0 and key_search < self.keys[i]:
            i = i - 1
        while i >= 0:
            val_in = self.vals[i]
            val_out = val_in[:index] + val + val_in[index + len(val):]
            self.vals[i] = val_out
            i = i - 1
        self._update_left(index, val)

    def update_le(self, key_search: bytes, index: int, val: bytes) -> None:
        if self.is_leaf:
            self._update_le(key_search, index, val)
            self.persist()
            return

        index = self.get_page_id_index(key_search)
        page_id = self.page_ids[index]
        child = new_b_plus_tree_node_from_page_id(self.pager, self.free_list, page_id)
        child.update_le(key_search, index, val)
        return

    def _update_le(self, key_search: bytes, index: int, val: bytes) -> None:
        i = len(self.keys) - 1
        while i >= 0 and key_search <= self.keys[i]:
            i = i - 1
        while i >= 0:
            val_in = self.vals[i]
            val_out = val_in[:index] + val + val_in[index + len(val):]
            self.vals[i] = val_out
            i = i - 1
        self._update_left(index, val)

    def update_gt(self, key_search: bytes, index: int, val: bytes) -> None:
        if self.is_leaf:
            self._update_gt(key_search, index, val)
            self.persist()
            return

        index = self.get_page_id_index(key_search)
        page_id = self.page_ids[index]
        child = new_b_plus_tree_node_from_page_id(self.pager, self.free_list, page_id)
        child.update_gt(key_search, index, val)
        return

    def _update_gt(self, key_search: bytes, index: int, val: bytes) -> None:
        i = 0
        while i < len(self.keys) and self.keys[i] <= key_search:
            i = i + 1
        while i < len(self.keys):
            val_in = self.vals[i]
            val_out = val_in[:index] + val + val_in[index + len(val):]
            self.vals[i] = val_out
            i = i + 1
        self._update_right(index, val)

    def update_ge(self, key_search: bytes, index: int, val: bytes) -> None:
        if self.is_leaf:
            self._update_ge(key_search, index, val)
            self.persist()
            return

        index = self.get_page_id_index(key_search)
        page_id = self.page_ids[index]
        child = new_b_plus_tree_node_from_page_id(self.pager, self.free_list, page_id)
        child.update_ge(key_search, index, val)
        return

    def _update_ge(self, key_search: bytes, index: int, val: bytes) -> None:
        i = 0
        while i < len(self.keys) and self.keys[i] < key_search:
            i = i + 1
        while i < len(self.keys):
            val_in = self.vals[i]
            val_out = val_in[:index] + val + val_in[index + len(val):]
            self.vals[i] = val_out
            i = i + 1
        self._update_right(index, val)

    def _update_left(self, index: int, val: bytes) -> None:
        node = self
        while node.left_page_id != NULL_PAGE_ID:
            node = new_b_plus_tree_node_from_page_id(self.pager, self.free_list, node.left_page_id)
            node._update_vals(index, val)
            node.persist()

    def _update_right(self, index: int, val: bytes) -> None:
        node = self
        while node.right_page_id != NULL_PAGE_ID:
            node = new_b_plus_tree_node_from_page_id(self.pager, self.free_list, node.right_page_id)
            node._update_vals(index, val)
            node.persist()

    def _update_vals(self, index: int, val: bytes) -> None:
        for i, val_in in enumerate(self.vals):
            val_out = val_in[:index] + val + val_in[index + len(val):]
            self.vals[i] = val_out

    def persist(self) -> None:
        bs = bytes(self)
        self.pager.page_set(self.page_id, bs)

    def is_full(self) -> bool:
        return len(self.keys) >= 2 * DEGREE - 1

    def split(self) -> 'BPlusTreeNode':
        new = new_b_plus_tree_node(self.pager, self.free_list, self.is_leaf)
        if self.is_leaf:
            new.keys = self.keys[DEGREE:]
            new.vals = self.vals[DEGREE:]
            self.keys = self.keys[:DEGREE]
            self.vals = self.vals[:DEGREE]
        else:
            new.keys = self.keys[DEGREE:]
            new.page_ids = self.page_ids[DEGREE:]
            self.keys = self.keys[:DEGREE - 1]
            self.page_ids = self.page_ids[:DEGREE]

        if self.right_page_id != NULL_PAGE_ID:
            r = new_b_plus_tree_node_from_page_id(self.pager, self.free_list, self.right_page_id)
            r.left_page_id = new.page_id
            r.persist()
            self.right_page_id = new.page_id
            new.left_page_id = self.page_id
            new.right_page_id = r.page_id
        else:
            self.right_page_id = new.page_id
            new.left_page_id = self.page_id

        new.persist()
        self.persist()
        return new

    def delete_one(self, key: bytes) -> bytes | None:
        if self.is_leaf:
            key_right = self._delete_one(key)
            self.persist()
            return key_right

        page_id_index = self.get_page_id_index(key)
        page_id = self.page_ids[page_id_index]
        child = new_b_plus_tree_node_from_page_id(self.pager, self.free_list, page_id)
        key_right = child.delete_one(key)

        if self.need_replace(key, key_right):
            key_index = self.get_key_index(key)
            if key_index is not None and key_right != NULL_PAGE_ID:
                self.keys[key_index] = key_right
                self.persist()

        if child.is_enough():
            return key_right

        # self not leaf
        # child is not enough
        child_left = None
        if child.left_page_id != NULL_PAGE_ID:
            child_left = new_b_plus_tree_node_from_page_id(self.pager, self.free_list, child.left_page_id)
        if self.can_borrow_child_left(page_id_index, child_left):
            self.borrow_child_left(page_id_index, child, child_left)
            return key_right

        child_right = None
        if child.right_page_id != NULL_PAGE_ID:
            child_right = new_b_plus_tree_node_from_page_id(self.pager, self.free_list, child.right_page_id)
        if self.can_borrow_child_right(page_id_index, child_right):
            self.borrow_child_right(page_id_index, child, child_right)
            return key_right

        if page_id_index < len(self.page_ids) - 1:
            self.merge_right_child(child, child_right, page_id_index)
            return key_right
        else:
            self.merge_right_child(child_left, child, page_id_index - 1)
            return key_right

    def _delete_one(self, key: bytes) -> bytes | None:
        key_right = None
        try:
            i = self.keys.index(key)
        except ValueError:
            return key_right
        self.keys.pop(i)
        self.vals.pop(i)
        try:
            key_right = self.keys[i]
        except IndexError:
            if self.right_page_id != NULL_PAGE_ID:
                right = new_b_plus_tree_node_from_page_id(self.pager, self.free_list, self.right_page_id)
                key_right = right.keys[0]
        return key_right

    def need_replace(self, removed_key: bytes, replace_key: bytes) -> bool:
        return removed_key in self.keys and replace_key is not None

    def is_enough(self) -> bool:
        return len(self.keys) >= DEGREE - 1

    def get_key_index(self, key: bytes) -> int | None:
        try:
            return self.keys.index(key)
        except ValueError:
            return None

    def can_borrow(self) -> bool:
        return len(self.keys) >= DEGREE

    def can_borrow_child_left(self, index: int, child_left: 'BPlusTreeNode') -> bool:
        return index > 0 and child_left is not None and child_left.can_borrow()

    def borrow_child_left(self, index: int, child: 'BPlusTreeNode', child_left: 'BPlusTreeNode') -> None:
        if child.is_leaf:
            _key = child_left.keys.pop(-1)
            _val = child_left.vals.pop(-1)
            child.keys.insert(0, _key)
            child.vals.insert(0, _val)
        else:
            _key = self.keys[index - 1]
            _page_id = child_left.page_ids.pop(-1)
            child.keys.insert(0, _key)
            child.page_ids.insert(0, _page_id)
        if child.is_leaf:
            _key = child.keys[0]
            self.keys[index - 1] = _key
        else:
            _key = child_left.keys.pop(-1)
            self.keys[index - 1] = _key
        self.persist()
        child.persist()
        child_left.persist()

    def can_borrow_child_right(self, index: int, child_right: 'BPlusTreeNode') -> bool:
        return index < len(self.page_ids) - 1 and child_right is not None and child_right.can_borrow()

    def borrow_child_right(self, index: int, child: 'BPlusTreeNode', child_right: 'BPlusTreeNode') -> None:
        if child.is_leaf:
            _key = child_right.keys.pop(0)
            _val = child_right.vals.pop(0)
            child.keys.append(_key)
            child.vals.append(_val)
        else:
            _key = self.keys[index]
            _page_id = child_right.page_ids.pop(0)
            child.keys.append(_key)
            child.page_ids.append(_page_id)
        if child.is_leaf:
            _key = child_right.keys[0]
            self.keys[index] = _key
        else:
            _key = child_right.keys.pop(0)
            self.keys[index] = _key
        self.persist()
        child.persist()
        child_right.persist()

    def merge_right_child(self, left_child: 'BPlusTreeNode', right_child: 'BPlusTreeNode', index: int) -> None:
        if left_child.is_leaf:
            self.keys.pop(index)
            left_child.keys.extend(right_child.keys)
            left_child.vals.extend(right_child.vals)
        else:
            _key = self.keys.pop(index)
            left_child.keys.append(_key)
            left_child.keys.extend(right_child.keys)
            left_child.page_ids.extend(right_child.page_ids)

        left_child.right_page_id = right_child.right_page_id
        if left_child.right_page_id != NULL_PAGE_ID:
            rr_child = new_b_plus_tree_node_from_page_id(self.pager, self.free_list, left_child.right_page_id)
            rr_child.left_page_id = left_child.page_id
            rr_child.persist()

        self.page_ids.pop(index + 1)
        self.persist()
        left_child.persist()
        self.free_list.add_page_id(right_child.page_id)

    def is_empty(self) -> bool:
        return len(self.keys) == 0


def new_b_plus_tree_node(pager: Pager, free_list: FreeList, is_leaf: bool) -> BPlusTreeNode:
    page_id = free_list.get_page_id()
    node = BPlusTreeNode(pager, free_list, is_leaf, page_id, NULL_PAGE_ID, NULL_PAGE_ID)
    return node


def new_b_plus_tree_node_from_page_id(pager: Pager, free_list: FreeList, page_id: int) -> BPlusTreeNode:
    buf = pager.page_get(page_id)
    # 读取节点信息
    is_leaf = from_buf(buf, bool)
    _page_id = from_buf(buf, int)
    if _page_id != page_id:
        raise ValueError("page_id 错误")
    left_page_id = from_buf(buf, int)
    right_page_id = from_buf(buf, int)
    num_keys = from_buf(buf, int)
    keys = [from_buf(buf, bytes) for _ in range(num_keys)]
    if is_leaf:
        num_vals = from_buf(buf, int)
        vals = [from_buf(buf, bytes) for _ in range(num_vals)]
        node = BPlusTreeNode(pager, free_list, is_leaf, page_id, left_page_id, right_page_id)
        node.keys = keys
        node.vals = vals
    else:
        num_page_ids = from_buf(buf, int)
        page_ids = [from_buf(buf, int) for _ in range(num_page_ids)]
        node = BPlusTreeNode(pager, free_list, is_leaf, page_id, left_page_id, right_page_id)
        node.keys = keys
        node.page_ids = page_ids
    return node


class BPlusTree:

    def __init__(self, pager: Pager, seq: int, free_list: FreeList, root: BPlusTreeNode):
        self.pager: Pager = pager
        self.seq: int = seq
        self.free_list: FreeList = free_list
        self.root: BPlusTreeNode = root

    def get_all(self) -> list[bytes]:
        # todo：可以优化，BPlusTree 记录最左边和最右边的叶子节点，直接从叶子节点开始遍历
        vals = self.root.get_ge(b'')
        return vals

    def get_lt(self, key: bytes) -> list[bytes]:
        vals = self.root.get_lt(key)
        return vals

    def get_le(self, key: bytes) -> list[bytes]:
        vals = self.root.get_le(key)
        return vals

    def get_gt(self, key: bytes) -> list[bytes]:
        vals = self.root.get_gt(key)
        return vals

    def get_ge(self, key: bytes) -> list[bytes]:
        vals = self.root.get_ge(key)
        return vals

    def get_one(self, key: bytes) -> bytes | None:
        val = self.root.get_one(key)
        return val

    def add(self, key_vals: list[tuple[bytes, bytes]]) -> None:
        for key, val in key_vals:
            if self.root.is_full():
                child = self.root
                new_root = new_b_plus_tree_node(self.pager, self.free_list, False)
                _key = child.keys[DEGREE - 1]
                if child.is_leaf:
                    _key = child.keys[DEGREE]
                new_root.keys = [_key]
                new_root.page_ids = [child.page_id]
                child_new = child.split()
                new_root.page_ids.append(child_new.page_id)
                new_root.persist()
                self.pager.root_page_id_set(self.seq, new_root.page_id)
                self.root = new_root
            self.root.add(key, val)

    def upsert(self, key_vals: list[tuple[bytes, bytes]]) -> None:
        for key, val in key_vals:
            if self.root.is_full():
                child = self.root
                new_root = new_b_plus_tree_node(self.pager, self.free_list, False)
                _key = child.keys[DEGREE - 1]
                if child.is_leaf:
                    _key = child.keys[DEGREE]
                new_root.keys = [_key]
                new_root.page_ids = [child.page_id]
                child_new = child.split()
                new_root.page_ids.append(child_new.page_id)
                new_root.persist()
                self.pager.root_page_id_set(self.seq, new_root.page_id)
                self.root = new_root
            self.root.upsert(key, val)

    def update_lt(self, key_search: bytes, index_vals: list[tuple[int, bytes]]) -> None:
        for index, val in index_vals:
            self.root.update_lt(key_search, index, val)

    def update_le(self, key_search: bytes, index_vals: list[tuple[int, bytes]]) -> None:
        for index, val in index_vals:
            self.root.update_le(key_search, index, val)

    def update_gt(self, key_search: bytes, index_vals: list[tuple[int, bytes]]) -> None:
        for index, val in index_vals:
            self.root.update_gt(key_search, index, val)

    def update_ge(self, key_search: bytes, index_vals: list[tuple[int, bytes]]) -> None:
        for index, val in index_vals:
            self.root.update_ge(key_search, index, val)

    def delete_one(self, key: bytes) -> None:
        self.root.delete_one(key)
        if self.root.is_empty() and not self.root.is_leaf:
            page_id = self.root.page_ids[0]
            new_root = new_b_plus_tree_node_from_page_id(self.pager, self.free_list, page_id)
            self.pager.root_page_id_set(self.seq, new_root.page_id)
            self.root = new_root


def new_b_plus_tree(pager: Pager, seq: int, free_list: FreeList) -> BPlusTree:
    root = new_b_plus_tree_node(pager, free_list, True)
    root.persist()
    pager.root_page_id_set(seq, root.page_id)
    return BPlusTree(pager, seq, free_list, root)


def new_b_plus_tree_from_root_page_id(pager: Pager, seq: int, free_list: FreeList, root_page_id: int) -> BPlusTree:
    root = new_b_plus_tree_node_from_page_id(pager, free_list, root_page_id)
    return BPlusTree(pager, seq, free_list, root)
