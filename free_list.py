from const import NULL_PAGE_ID, NUM_PAGE_IDS
from file import get_page, set_page, set_used_page_id, set_tail_page_id, set_head_page_id
from utils import to_bytes, from_buf


class PageIdGenerator:
    def __init__(self, fd: int, init_page_id: int):
        self.fd: int = fd
        self.used_page_id: int = init_page_id

    def get_next_page_id(self):
        self.used_page_id += 1
        set_used_page_id(self.fd, self.used_page_id)
        return self.used_page_id


def new_page_id_generator(fd: int, init_page_id: int):
    return PageIdGenerator(fd, init_page_id)


class FreeListNode:

    def __init__(self, fd: int, page_id: int, next_page_id: int):
        self.fd: int = fd
        self.page_id: int = page_id
        self.next_page_id: int = next_page_id
        self.unused: int = 0
        self.page_ids: list[int] = []

    def __bytes__(self) -> bytes:
        r = b''
        r += to_bytes(self.page_id)
        r += to_bytes(self.next_page_id)
        r += to_bytes(self.unused)
        r += to_bytes(len(self.page_ids))
        for page_id in self.page_ids:
            r += to_bytes(page_id)
        return r

    def persist(self) -> None:
        set_page(self.fd, self.page_id, bytes(self))

    def add_unused_page_id(self, page_id: int) -> None:
        self.page_ids.append(page_id)

    def have_unused(self) -> bool:
        return self.unused < len(self.page_ids)

    def get_unused_page_id(self) -> int:
        if self.have_unused():
            result = self.page_ids[self.unused]
            self.unused += 1
            self.persist()
            return result
        return NULL_PAGE_ID

    def is_full(self) -> bool:
        return len(self.page_ids) >= NUM_PAGE_IDS


def new_free_list_node(fd: int, page_id: int, next_page_id: int) -> FreeListNode:
    node = FreeListNode(fd, page_id, next_page_id)
    return node


def new_free_list_node_from_page_id(fd: int, page_id: int) -> FreeListNode:
    buf = get_page(fd, page_id)
    _page_id = from_buf(buf, int)
    if _page_id != page_id:
        raise ValueError("page_id 错误")
    next_page_id = from_buf(buf, int)
    unused = from_buf(buf, int)
    num_page_ids = from_buf(buf, int)
    page_ids = [from_buf(buf, int) for _ in range(num_page_ids)]
    node = FreeListNode(fd, page_id, next_page_id)
    node.unused = unused
    node.page_ids = page_ids
    return node


class FreeList:

    def __init__(self, fd: int, page_id_generator: PageIdGenerator, head: FreeListNode, tail: FreeListNode):
        self.fd: int = fd
        self.page_id_generator: PageIdGenerator = page_id_generator
        self.head: FreeListNode = head
        self.tail: FreeListNode = tail

    # 对外暴露使用
    def get_page_id(self) -> int:
        page_id = self.get_unused_page_id()
        if page_id == NULL_PAGE_ID:
            page_id = self.page_id_generator.get_next_page_id()
        return page_id

    # 对外暴露使用
    def add_page_id(self, page_id: int) -> None:
        self.add_unused_page_id(page_id)

    def add_unused_page_id(self, page_id: int) -> None:
        if not self.tail.is_full():
            self.tail.add_unused_page_id(page_id)
            self.tail.persist()
            return

        # tail is full
        new_tail_page_id = self.page_id_generator.get_next_page_id()
        new_tail = new_free_list_node(self.fd, new_tail_page_id, NULL_PAGE_ID)
        new_tail.add_unused_page_id(page_id)
        new_tail.persist()
        self.tail.next_page_id = new_tail.page_id
        self.tail.persist()
        self.tail = new_tail
        set_tail_page_id(self.fd, new_tail.page_id)
        return

    def get_unused_page_id(self) -> int:
        result = self._get_unused_page_id(self.head)
        return result

    def _get_unused_page_id(self, node: FreeListNode) -> int:
        unused_page_id = node.get_unused_page_id()
        if unused_page_id != NULL_PAGE_ID:
            return unused_page_id

        if not node.is_full():
            return NULL_PAGE_ID

        if node.next_page_id == NULL_PAGE_ID:
            return NULL_PAGE_ID

        # node 没有空位
        # node 无可用
        # node 有下一页
        self.add_unused_page_id(node.page_id)
        if node.next_page_id == self.tail.page_id:
            node_next = self.tail
        else:
            node_next = new_free_list_node_from_page_id(self.fd, node.next_page_id)
        if node.page_id == self.head.page_id:
            self.head = node_next
            set_head_page_id(self.fd, node_next.page_id)

        unused_page_id = node_next.get_unused_page_id()
        return unused_page_id


def new_free_list(fd: int, init_page_id: int) -> FreeList:
    page_id_generator = new_page_id_generator(fd, init_page_id)
    head_page_id = page_id_generator.get_next_page_id()
    head = new_free_list_node(fd, head_page_id, NULL_PAGE_ID)
    head.persist()
    set_head_page_id(fd, head.page_id)
    set_tail_page_id(fd, head.page_id)
    free_list = FreeList(fd, page_id_generator, head, head)
    return free_list


def new_free_list_from_page_id(fd: int, init_page_id: int, head_page_id: int, tail_page_id: int) -> FreeList:
    page_id_generator = new_page_id_generator(fd, init_page_id)
    head = new_free_list_node_from_page_id(fd, head_page_id)
    tail = new_free_list_node_from_page_id(fd, tail_page_id)
    free_list = FreeList(fd, page_id_generator, head, tail)
    return free_list
