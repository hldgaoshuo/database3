from const import OP_EQ, OP_LT, OP_LE, OP_GT, OP_GE
from oid import get_oid
from row import Row, new_row, new_row_from_bytes
from table import Table
from utils import from_bytes
from value.value import Value
from value.value_int import new_value_int


class Executor:
    """
    火山模型执行器基类。
    实现 Python 迭代器协议（对应 BusTub 的 Init() + Next()）：
    每次 __next__ 产出 (oid, row)，oid 是主树 key（ValueInt 序列化），
    数据源不明的执行器（如 ValuesExecutor）产出 (None, row)，耗尽抛 StopIteration。
    """

    def __iter__(self) -> 'Executor':
        raise NotImplementedError

    def __next__(self) -> tuple[bytes | None, Row]:
        raise NotImplementedError


def index_key(row: Row, col_indexes: tuple) -> bytes:
    """用行内索引列的值构造二级索引的 key"""
    key_row = new_row([row.vals[i] for i in col_indexes])
    return bytes(key_row)


def index_val(oid: int) -> bytes:
    val_row = new_row([new_value_int(oid)])
    return bytes(val_row)


def oid_from_key(key_bs: bytes) -> int:
    # 主树 key 是 ValueInt 序列化：val_type(8 字节) + val(8 字节)
    return from_bytes(key_bs[8:], int)


class ValuesExecutor(Executor):

    def __init__(self):
        self.rows: list[Row] = []
        self.rows_iter = iter(self.rows)

    def __iter__(self) -> 'ValuesExecutor':
        return self

    def __next__(self) -> tuple[bytes | None, Row]:
        row = next(self.rows_iter)
        return None, row


class SeqScanExecutor(Executor):

    def __init__(self):
        self.table: Table | None = None
        self.items_iter = iter([])

    def __iter__(self) -> 'SeqScanExecutor':
        return self

    def __next__(self) -> tuple[bytes | None, Row]:
        key_bs, val_bs = next(self.items_iter)
        row = new_row_from_bytes(val_bs)
        return key_bs, row


class IndexScanExecutor(Executor):
    """二级索引等值点查 + 回表。key_row 是索引列的值组成的 Row。"""

    def __init__(self):
        self.table: Table | None = None
        self.col_indexes: tuple = ()
        self.key_row: Row | None = None
        self.done: bool = False

    def __iter__(self) -> 'IndexScanExecutor':
        return self

    def __next__(self) -> tuple[bytes | None, Row]:
        if self.done:
            raise StopIteration
        self.done = True
        index = self.table.indexes[self.col_indexes]
        val_bs = index.get_one(bytes(self.key_row))
        if val_bs is None:
            raise StopIteration
        # 索引 val 是 Row([ValueInt(oid)])，其首元素序列化即主树 key
        val_row = new_row_from_bytes(val_bs)
        key_bs = bytes(val_row.vals[0])
        data_bs = self.table.data.get_one(key_bs)
        if data_bs is None:
            raise StopIteration
        row = new_row_from_bytes(data_bs)
        return key_bs, row


class FilterExecutor(Executor):

    def __init__(self):
        self.child: Executor | None = None
        self.col_index: int = 0
        self.op: int = OP_EQ
        self.value: Value | None = None

    def __iter__(self) -> 'FilterExecutor':
        return self

    def __next__(self) -> tuple[bytes | None, Row]:
        for oid, row in self.child:
            if self._match(row):
                return oid, row
        raise StopIteration

    def _match(self, row: Row) -> bool:
        left = row.vals[self.col_index].val
        right = self.value.val
        if self.op == OP_EQ:
            return left == right
        if self.op == OP_LT:
            return left < right
        if self.op == OP_LE:
            return left <= right
        if self.op == OP_GT:
            return left > right
        if self.op == OP_GE:
            return left >= right
        raise ValueError(f"未知比较运算符 {self.op}")


class ProjectionExecutor(Executor):

    def __init__(self):
        self.child: Executor | None = None
        self.col_indexes: list[int] = []

    def __iter__(self) -> 'ProjectionExecutor':
        return self

    def __next__(self) -> tuple[bytes | None, Row]:
        oid, row = next(self.child)
        projected = new_row([row.vals[i] for i in self.col_indexes])
        return oid, projected


class InsertExecutor(Executor):
    """从 child 取行，生成 OID 写主树，并同步全部二级索引。逐行回传 (oid, row)。"""

    def __init__(self):
        self.table: Table | None = None
        self.child: Executor | None = None

    def __iter__(self) -> 'InsertExecutor':
        return self

    def __next__(self) -> tuple[bytes | None, Row]:
        _, row = next(self.child)
        oid = get_oid()
        key_bs = bytes(new_value_int(oid))
        self.table.data.add([(key_bs, bytes(row))])
        val_bs = index_val(oid)
        for col_indexes, index in self.table.indexes.items():
            index.add([(index_key(row, col_indexes), val_bs)])
        return key_bs, row


class DeleteExecutor(Executor):
    """按 child 产出的 (oid, row) 删除主树记录和全部二级索引项。逐行回传被删的 (oid, row)。"""

    def __init__(self):
        self.table: Table | None = None
        self.child: Executor | None = None

    def __iter__(self) -> 'DeleteExecutor':
        return self

    def __next__(self) -> tuple[bytes | None, Row]:
        oid, row = next(self.child)
        self.table.data.delete_one(oid)
        for col_indexes, index in self.table.indexes.items():
            index.delete_one(index_key(row, col_indexes))
        return oid, row


class UpdateExecutor(Executor):
    """
    先删后插（oid 不变）：assignments 是 (col_index, Value) 常量赋值列表。
    逐行回传 (oid, 新 row)。
    """

    def __init__(self):
        self.table: Table | None = None
        self.child: Executor | None = None
        self.assignments: list[tuple[int, Value]] = []

    def __iter__(self) -> 'UpdateExecutor':
        return self

    def __next__(self) -> tuple[bytes | None, Row]:
        oid, row = next(self.child)
        val_bs = index_val(oid_from_key(oid))
        for col_indexes, index in self.table.indexes.items():
            index.delete_one(index_key(row, col_indexes))
        self.table.data.delete_one(oid)

        vals = list(row.vals)
        for col_index, value in self.assignments:
            vals[col_index] = value
        row_new = new_row(vals)
        self.table.data.add([(oid, bytes(row_new))])
        for col_indexes, index in self.table.indexes.items():
            index.add([(index_key(row_new, col_indexes), val_bs)])
        return oid, row_new


def new_values_executor(rows: list[Row]) -> ValuesExecutor:
    executor = ValuesExecutor()
    executor.rows = rows
    executor.rows_iter = iter(executor.rows)
    return executor


def new_seq_scan_executor(table: Table) -> SeqScanExecutor:
    executor = SeqScanExecutor()
    executor.table = table
    executor.items_iter = iter(table.data.items())
    return executor


def new_index_scan_executor(table: Table, col_indexes: tuple, key_row: Row) -> IndexScanExecutor:
    executor = IndexScanExecutor()
    executor.table = table
    executor.col_indexes = col_indexes
    executor.key_row = key_row
    return executor


def new_filter_executor(child: Executor, col_index: int, op: int, value: Value) -> FilterExecutor:
    executor = FilterExecutor()
    executor.child = child
    executor.col_index = col_index
    executor.op = op
    executor.value = value
    return executor


def new_projection_executor(child: Executor, col_indexes: list[int]) -> ProjectionExecutor:
    executor = ProjectionExecutor()
    executor.child = child
    executor.col_indexes = col_indexes
    return executor


def new_insert_executor(table: Table, child: Executor) -> InsertExecutor:
    executor = InsertExecutor()
    executor.table = table
    executor.child = child
    return executor


def new_delete_executor(table: Table, child: Executor) -> DeleteExecutor:
    executor = DeleteExecutor()
    executor.table = table
    executor.child = child
    return executor


def new_update_executor(table: Table, child: Executor, assignments: list[tuple[int, Value]]) -> UpdateExecutor:
    executor = UpdateExecutor()
    executor.table = table
    executor.child = child
    executor.assignments = assignments
    return executor
