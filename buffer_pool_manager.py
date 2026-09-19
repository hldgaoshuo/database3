import io

from const import BYTES_PAGE, META_PAGE_ID, MAGIC_NUMBER_BS, BYTES_MAGIC_NUMBER, BYTES_USED_PAGE_ID, \
    BYTES_HEAD_PAGE_ID, BYTES_TAIL_PAGE_ID, BYTES_B_PLUS_TREE_SEQ, BYTES_DATABASE_SEQ, BYTES_ROOT_PAGE_ID
from lru_replacer import LRUReplacer
from pager import Pager
from utils import to_bytes, from_bytes
from wal import Wal


class Frame:

    def __init__(self):
        self.page_id: int = 0
        self.data: bytearray = bytearray(BYTES_PAGE)
        self.is_dirty: bool = False


class BufferPoolManager:
    """
    写回式缓冲池。包装 Pager（磁盘管理器），对外接口与 Pager 一致，可整体替换。

    上层通过 page_get 拿到的是页副本（BytesIO），写回只能显式调用 page_set，
    调用方从不持有池内页内存，因此无需 BusTub 的 pin/unpin 机制：
    所有帧恒可驱逐，脏页在驱逐或 flush 时落盘。
    持有 Wal 时遵循 write-ahead：弄脏帧之前先把页镜像写入日志；
    flush_all_pages 全部落盘后 checkpoint（截断日志）。
    """

    def __init__(self):
        self.pager: Pager | None = None
        self.wal: Wal | None = None
        self.frames: list[Frame] = []
        self.page_table: dict[int, int] = {}
        self.free_frames: list[int] = []
        self.replacer: LRUReplacer | None = None

    def page_get(self, page_id: int) -> io.BytesIO:
        frame_id = self._fetch_frame(page_id)
        frame = self.frames[frame_id]
        page_buf = io.BytesIO(bytes(frame.data))
        return page_buf

    def page_set(self, page_id: int, page_bs: bytes) -> None:
        if len(page_bs) > BYTES_PAGE:
            raise ValueError("page_bs 超过页大小")
        frame_id = self._fetch_frame(page_id)
        frame = self.frames[frame_id]
        frame.data[:] = page_bs + b'\x00' * (BYTES_PAGE - len(page_bs))
        self._log_write_ahead(frame)
        frame.is_dirty = True

    def flush_page(self, page_id: int) -> None:
        frame_id = self.page_table.get(page_id)
        if frame_id is None:
            return
        frame = self.frames[frame_id]
        if not frame.is_dirty:
            return
        self.pager.page_set(page_id, bytes(frame.data))
        frame.is_dirty = False

    def flush_all_pages(self) -> None:
        for page_id in list(self.page_table.keys()):
            self.flush_page(page_id)
        if self.wal is not None:
            self.wal.truncate()

    def magic_number_set(self) -> None:
        offset = META_PAGE_ID * BYTES_PAGE
        bs = MAGIC_NUMBER_BS
        self._partial_write(offset, bs)

    def magic_number_exist(self) -> bool:
        offset = META_PAGE_ID * BYTES_PAGE
        bs = self._partial_read(offset, BYTES_MAGIC_NUMBER)
        return bs == MAGIC_NUMBER_BS

    def used_page_id_set(self, used_page_id: int) -> None:
        offset = (
                META_PAGE_ID * BYTES_PAGE +
                BYTES_MAGIC_NUMBER
        )
        bs = to_bytes(used_page_id)
        self._partial_write(offset, bs)

    def head_page_id_set(self, head_page_id: int) -> None:
        offset = (
                META_PAGE_ID * BYTES_PAGE +
                BYTES_MAGIC_NUMBER +
                BYTES_USED_PAGE_ID
        )
        bs = to_bytes(head_page_id)
        self._partial_write(offset, bs)

    def tail_page_id_set(self, tail_page_id: int) -> None:
        offset = (
                META_PAGE_ID * BYTES_PAGE +
                BYTES_MAGIC_NUMBER +
                BYTES_USED_PAGE_ID +
                BYTES_HEAD_PAGE_ID
        )
        bs = to_bytes(tail_page_id)
        self._partial_write(offset, bs)

    def b_plus_tree_seq_set(self, seq: int) -> None:
        offset = (
                META_PAGE_ID * BYTES_PAGE +
                BYTES_MAGIC_NUMBER +
                BYTES_USED_PAGE_ID +
                BYTES_HEAD_PAGE_ID +
                BYTES_TAIL_PAGE_ID
        )
        bs = to_bytes(seq)
        self._partial_write(offset, bs)

    def database_seq_set(self, database_page_id: int) -> None:
        offset = (
                META_PAGE_ID * BYTES_PAGE +
                BYTES_MAGIC_NUMBER +
                BYTES_USED_PAGE_ID +
                BYTES_HEAD_PAGE_ID +
                BYTES_TAIL_PAGE_ID +
                BYTES_B_PLUS_TREE_SEQ
        )
        bs = to_bytes(database_page_id)
        self._partial_write(offset, bs)

    def root_page_id_set(self, seq: int, root_page_id: int) -> None:
        offset = (
                META_PAGE_ID * BYTES_PAGE +
                BYTES_MAGIC_NUMBER +
                BYTES_USED_PAGE_ID +
                BYTES_HEAD_PAGE_ID +
                BYTES_TAIL_PAGE_ID +
                BYTES_B_PLUS_TREE_SEQ +
                BYTES_DATABASE_SEQ +
                BYTES_ROOT_PAGE_ID * seq
        )
        bs = to_bytes(root_page_id)
        self._partial_write(offset, bs)

    def root_page_id_get(self, seq: int) -> int:
        offset = (
                META_PAGE_ID * BYTES_PAGE +
                BYTES_MAGIC_NUMBER +
                BYTES_USED_PAGE_ID +
                BYTES_HEAD_PAGE_ID +
                BYTES_TAIL_PAGE_ID +
                BYTES_B_PLUS_TREE_SEQ +
                BYTES_DATABASE_SEQ +
                BYTES_ROOT_PAGE_ID * seq
        )
        root_page_id_bs = self._partial_read(offset, BYTES_ROOT_PAGE_ID)
        root_page_id = from_bytes(root_page_id_bs, int)
        return root_page_id

    def _fetch_frame(self, page_id: int) -> int:
        frame_id = self.page_table.get(page_id)
        if frame_id is not None:
            self.replacer.record_access(frame_id)
            return frame_id

        if len(self.free_frames) > 0:
            frame_id = self.free_frames.pop()
        else:
            frame_id = self.replacer.evict()
            if frame_id is None:
                raise RuntimeError("缓冲池已满且无可驱逐帧")
            victim = self.frames[frame_id]
            if victim.is_dirty:
                self.flush_page(victim.page_id)
            del self.page_table[victim.page_id]

        frame = self.frames[frame_id]
        page_bs = self.pager.file_read(page_id * BYTES_PAGE, BYTES_PAGE)
        frame.data[:] = page_bs + b'\x00' * (BYTES_PAGE - len(page_bs))
        frame.page_id = page_id
        frame.is_dirty = False
        self.page_table[page_id] = frame_id
        self.replacer.record_access(frame_id)
        return frame_id

    def _partial_write(self, offset: int, bs: bytes) -> None:
        page_id = offset // BYTES_PAGE
        inner_offset = offset % BYTES_PAGE
        if inner_offset + len(bs) > BYTES_PAGE:
            raise ValueError("partial write 跨页")
        frame_id = self._fetch_frame(page_id)
        frame = self.frames[frame_id]
        frame.data[inner_offset:inner_offset + len(bs)] = bs
        self._log_write_ahead(frame)
        frame.is_dirty = True

    def _log_write_ahead(self, frame: Frame) -> None:
        if self.wal is not None:
            self.wal.append(frame.page_id, bytes(frame.data))

    def _partial_read(self, offset: int, length: int) -> bytes:
        page_id = offset // BYTES_PAGE
        inner_offset = offset % BYTES_PAGE
        frame_id = self._fetch_frame(page_id)
        frame = self.frames[frame_id]
        bs = bytes(frame.data[inner_offset:inner_offset + length])
        return bs


def new_buffer_pool_manager(pager: Pager, pool_size: int, wal: Wal = None) -> BufferPoolManager:
    bpm = BufferPoolManager()
    bpm.pager = pager
    bpm.wal = wal
    bpm.frames = [Frame() for _ in range(pool_size)]
    bpm.page_table = {}
    bpm.free_frames = list(reversed(range(pool_size)))
    bpm.replacer = LRUReplacer()
    return bpm
