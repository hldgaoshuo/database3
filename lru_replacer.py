class LRUNode:

    def __init__(self):
        self.frame_id: int = 0
        self.prev: LRUNode | None = None
        self.next: LRUNode | None = None


class LRUReplacer:
    """
    最近最少使用替换器。
    哈希表 + 双向链表，所有操作 O(1)：
    链表头是最久未使用的帧（下一个驱逐候选），链表尾是最近使用的帧。
    """

    def __init__(self):
        self.nodes: dict[int, LRUNode] = {}
        self.head: LRUNode | None = None
        self.tail: LRUNode | None = None

    def record_access(self, frame_id: int) -> None:
        node = self.nodes.get(frame_id)
        if node is None:
            node = LRUNode()
            node.frame_id = frame_id
            self.nodes[frame_id] = node
        else:
            self._detach(node)
        self._append(node)

    def evict(self) -> int | None:
        if self.head is None:
            return None
        node = self.head
        self._detach(node)
        del self.nodes[node.frame_id]
        return node.frame_id

    def size(self) -> int:
        return len(self.nodes)

    def _detach(self, node: LRUNode) -> None:
        if node.prev is not None:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next is not None:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        node.prev = None
        node.next = None

    def _append(self, node: LRUNode) -> None:
        node.prev = self.tail
        node.next = None
        if self.tail is not None:
            self.tail.next = node
        else:
            self.head = node
        self.tail = node
