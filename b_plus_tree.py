import io

from const import NULL_PAGE_ID, DEGREE
from file import get_page, set_page, set_root_page_id
from id_generator import IDGenerator
from utils import to_bytes, from_bytes


class BPlusTreeNode:

    def __init__(self, fd: int, id_generator: IDGenerator, is_leaf: bool, page_id: int, left_page_id: int,
                 right_page_id: int):
        # fd，id_generator，每个节点都需要携带
        self.fd: int = fd
        self.id_generator: IDGenerator = id_generator
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
        r += to_bytes(len(self.keys))
        for key in self.keys:
            r += to_bytes(key)
        if self.is_leaf:
            r += to_bytes(len(self.vals))
            for val in self.vals:
                r += to_bytes(val)
            r += to_bytes(self.left_page_id)
            r += to_bytes(self.right_page_id)
        else:
            r += to_bytes(len(self.page_ids))
            for page_id in self.page_ids:
                r += to_bytes(page_id)
        return r

    def __getitem__(self, key: bytes) -> bytes | None:
        if self.is_leaf:
            result = self.get_val(key)
            return result
        index = self.get_page_id_index(key)
        page_id = self.page_ids[index]
        child = new_b_plus_tree_node_from_page_id(self.fd, self.id_generator, page_id)
        result = child[key]
        return result

    def get_val(self, key: bytes) -> bytes | None:
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

    def __setitem__(self, key: bytes, val: bytes) -> None:
        if self.is_leaf:
            self.set_val(key, val)
            self.persist()
            return

        index = self.get_page_id_index(key)
        page_id = self.page_ids[index]
        child = new_b_plus_tree_node_from_page_id(self.fd, self.id_generator, page_id)
        if not child.is_full():
            child[key] = val
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
            child_new[key] = val
        else:
            child[key] = val
        return

    def set_val(self, key: bytes, val: bytes) -> None:
        i = len(self.keys) - 1
        while i >= 0 and key < self.keys[i]:
            i = i - 1
        if i >= 0 and key == self.keys[i]:
            self.vals[i] = val
        else:
            i = i + 1
            self.keys.insert(i, key)
            self.vals.insert(i, val)

    def persist(self) -> None:
        set_page(self.fd, self.page_id, bytes(self))

    def is_full(self) -> bool:
        return len(self.keys) >= 2 * DEGREE - 1

    def split(self) -> 'BPlusTreeNode':
        new = new_b_plus_tree_node(self.fd, self.id_generator, self.is_leaf)
        if self.is_leaf:
            new.keys = self.keys[DEGREE:]
            new.vals = self.vals[DEGREE:]
            self.keys = self.keys[:DEGREE]
            self.vals = self.vals[:DEGREE]
            if self.right_page_id != NULL_PAGE_ID:
                r = new_b_plus_tree_node_from_page_id(self.fd, self.id_generator, self.right_page_id)
                r.left_page_id = new.page_id
                r.persist()
                self.right_page_id = new.page_id
                new.left_page_id = self.page_id
                new.right_page_id = r.page_id
            else:
                self.right_page_id = new.page_id
                new.left_page_id = self.page_id
        else:
            new.keys = self.keys[DEGREE:]
            new.page_ids = self.page_ids[DEGREE:]
            self.keys = self.keys[:DEGREE - 1]
            self.page_ids = self.page_ids[:DEGREE]
        new.persist()
        self.persist()
        return new

    def __delitem__(self, key: bytes) -> None:
        self.delete(key)

    def delete(self, key: bytes) -> bytes | None:
        if self.is_leaf:
            key_right = self.delete_val(key)
            self.persist()
            return key_right

        page_id_index = self.get_page_id_index(key)
        page_id = self.page_ids[page_id_index]
        child = new_b_plus_tree_node_from_page_id(self.fd, self.id_generator, page_id)
        key_right = child.delete(key)
        if child.is_enough():
            key_index = self.get_key_index(key)
            if key_index is not None and key_right != NULL_PAGE_ID:
                self.keys[key_index] = key_right
                self.persist()
            return key_right

        # self not leaf
        # child is not enough
        child_left = None
        if child.left_page_id != NULL_PAGE_ID:
            child_left = new_b_plus_tree_node_from_page_id(self.fd, self.id_generator, child.left_page_id)
        if self.can_borrow_child_left(page_id_index, child_left):
            self.borrow_child_left(page_id_index, child, child_left)
            return key_right

        child_right = None
        if child.right_page_id != NULL_PAGE_ID:
            child_right = new_b_plus_tree_node_from_page_id(self.fd, self.id_generator, child.right_page_id)
        if self.can_borrow_child_right(page_id_index, child_right):
            self.borrow_child_right(page_id_index, child, child_right)
            return key_right

        if page_id_index < len(self.page_ids) - 1:
            self.merge_right_child(child, child_right, page_id_index)
            return key_right
        else:
            self.merge_right_child(child_left, child, page_id_index - 1)
            return key_right

    def delete_val(self, key: bytes) -> bytes | None:
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
                right = new_b_plus_tree_node_from_page_id(self.fd, self.id_generator, self.right_page_id)
                key_right = right.keys[0]
        return key_right

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
            left_child.right_page_id = right_child.right_page_id
            if left_child.right_page_id != NULL_PAGE_ID:
                rr_child = new_b_plus_tree_node_from_page_id(self.fd, self.id_generator, left_child.right_page_id)
                rr_child.left_page_id = left_child.page_id
                rr_child.persist()
        else:
            _key = self.keys.pop(index)
            left_child.keys.append(_key)
            left_child.keys.extend(right_child.keys)
            left_child.page_ids.extend(right_child.page_ids)
        self.page_ids.pop(index + 1)
        self.persist()
        left_child.persist()
        # todo right_child.page_id 如 free_list

    def is_empty(self) -> bool:
        return len(self.keys) == 0


def new_b_plus_tree_node(fd: int, id_generator: IDGenerator, is_leaf: bool) -> BPlusTreeNode:
    page_id = id_generator.get_next_page_id()
    node = BPlusTreeNode(fd, id_generator, is_leaf, page_id, NULL_PAGE_ID, NULL_PAGE_ID)
    return node


def new_b_plus_tree_node_from_page_id(fd: int, id_generator: IDGenerator, page_id: int) -> BPlusTreeNode:
    page = get_page(fd, page_id)
    buf = io.BytesIO(page)
    # 读取节点信息
    is_leaf = from_bytes(buf, bool)
    page_id = from_bytes(buf, int)
    num_keys = from_bytes(buf, int)
    keys = [from_bytes(buf, bytes) for _ in range(num_keys)]
    if is_leaf:
        num_vals = from_bytes(buf, int)
        vals = [from_bytes(buf, bytes) for _ in range(num_vals)]
        left_page_id = from_bytes(buf, int)
        right_page_id = from_bytes(buf, int)
        node = BPlusTreeNode(fd, id_generator, is_leaf, page_id, left_page_id, right_page_id)
        node.keys = keys
        node.vals = vals
    else:
        num_page_ids = from_bytes(buf, int)
        page_ids = [from_bytes(buf, int) for _ in range(num_page_ids)]
        node = BPlusTreeNode(fd, id_generator, is_leaf, page_id, NULL_PAGE_ID, NULL_PAGE_ID)
        node.keys = keys
        node.page_ids = page_ids
    return node


class BPlusTree:

    def __init__(self, fd: int, id_generator: IDGenerator, root: BPlusTreeNode):
        self.fd: int = fd
        self.id_generator: IDGenerator = id_generator
        self.root: BPlusTreeNode = root

    def __getitem__(self, key: bytes) -> bytes | None:
        val = self.root[key]
        return val

    def __setitem__(self, key: bytes, val: bytes) -> None:
        if self.root.is_full():
            child = self.root
            new_root = new_b_plus_tree_node(self.fd, self.id_generator, False)
            _key = child.keys[DEGREE - 1]
            if child.is_leaf:
                _key = child.keys[DEGREE]
            new_root.keys = [_key]
            new_root.page_ids = [child.page_id]
            child_new = child.split()
            new_root.page_ids.append(child_new.page_id)
            new_root.persist()
            set_root_page_id(self.fd, new_root.page_id)
            self.root = new_root
        self.root[key] = val

    def __delitem__(self, key: bytes) -> None:
        del self.root[key]
        if self.root.is_empty() and not self.root.is_leaf:
            page_id = self.root.page_ids[0]
            new_root = new_b_plus_tree_node_from_page_id(self.fd, self.id_generator, page_id)
            set_root_page_id(self.fd, new_root.page_id)
            self.root = new_root


def new_b_plus_tree(fd: int, id_generator: IDGenerator) -> BPlusTree:
    root = new_b_plus_tree_node(fd, id_generator, True)
    set_root_page_id(fd, root.page_id)
    return BPlusTree(fd, id_generator, root)


def new_b_plus_tree_from_root_page_id(fd: int, id_generator: IDGenerator, root_page_id: int) -> BPlusTree:
    root = new_b_plus_tree_node_from_page_id(fd, id_generator, root_page_id)
    return BPlusTree(fd, id_generator, root)
