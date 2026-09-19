from const import OP_EQ, OP_LT, OP_LE, OP_GT, OP_GE, AGG_COUNT, AGG_SUM, AGG_MIN, AGG_MAX
from oid import get_oid
from row import Row, new_row, new_row_from_bytes
from table import Table
from utils import from_bytes
from value.const import VALUE_TYPE_INT, VALUE_TYPE_STRING, VALUE_TYPE_BOOL
from value.value import Value
from value.value_bool import new_value_bool
from value.value_int import new_value_int
from value.value_string import new_value_string


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


def new_value(literal: int | str | bool, col_type: int) -> Value:
    if col_type == VALUE_TYPE_INT:
        if type(literal) is not int:
            raise ValueError(f"类型不匹配：期望 INT，实际 {literal!r}")
        return new_value_int(literal)
    if col_type == VALUE_TYPE_STRING:
        if type(literal) is not str:
            raise ValueError(f"类型不匹配：期望 STRING，实际 {literal!r}")
        return new_value_string(literal)
    if col_type == VALUE_TYPE_BOOL:
        if type(literal) is not bool:
            raise ValueError(f"类型不匹配：期望 BOOL，实际 {literal!r}")
        return new_value_bool(literal)
    raise ValueError(f"未知列类型 {col_type}")


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


class AggregationExecutor(Executor):
    """
    哈希聚合（对齐 BusTub 的 SimpleAggregationHashTable）。
    items 是输出列规格，顺序即 SELECT 顺序：
      ('col', group_pos)        —— 分组列，group_pos 是其在 group_col_indexes 中的位置
      (AGG_xxx, col_index|None) —— 聚合列，None 表示 COUNT(*)
    聚合结果没有 oid，产出 (None, row)。
    暂不支持 NULL：空输入且无分组列时，COUNT 输出 0，其余聚合抛 ValueError。
    """

    def __init__(self):
        self.child: Executor | None = None
        self.group_col_indexes: list[int] = []
        self.items: list[tuple] = []
        self.out_col_types: list[int] = []
        self.rows_iter = None

    def __iter__(self) -> 'AggregationExecutor':
        return self

    def __next__(self) -> tuple[bytes | None, Row]:
        if self.rows_iter is None:
            self.rows_iter = iter(self._aggregate())
        return next(self.rows_iter)

    def _aggregate(self) -> list[tuple[bytes | None, Row]]:
        groups: dict[tuple, list] = {}
        for _, row in self.child:
            key = tuple(row.vals[i].val for i in self.group_col_indexes)
            accs = groups.get(key)
            if accs is None:
                accs = [None] * len(self.items)
                groups[key] = accs
            for i, item in enumerate(self.items):
                if item[0] != 'col':
                    self._combine(accs, i, item, row)
        if not groups and len(self.group_col_indexes) == 0:
            # 无 GROUP BY 时全表一组，空表也要输出一行（COUNT 为 0）
            return [(None, self._emit(tuple(), [None] * len(self.items)))]
        return [(None, self._emit(key, accs)) for key, accs in groups.items()]

    def _combine(self, accs: list, i: int, item: tuple, row: Row) -> None:
        func, col_index = item
        if func == AGG_COUNT:
            accs[i] = (accs[i] or 0) + 1
            return
        val = row.vals[col_index].val
        if accs[i] is None:
            accs[i] = val
        elif func == AGG_SUM:
            accs[i] += val
        elif func == AGG_MIN:
            accs[i] = min(accs[i], val)
        elif func == AGG_MAX:
            accs[i] = max(accs[i], val)

    def _emit(self, key: tuple, accs: list) -> Row:
        vals = []
        for i, item in enumerate(self.items):
            if item[0] == 'col':
                raw = key[item[1]]
            elif accs[i] is None and item[0] == AGG_COUNT:
                raw = 0
            elif accs[i] is None:
                raise ValueError("空表上仅 COUNT 聚合有定义（暂不支持 NULL）")
            else:
                raw = accs[i]
            vals.append(new_value(raw, self.out_col_types[i]))
        return new_row(vals)


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


def new_aggregation_executor(child: Executor, group_col_indexes: list[int], items: list[tuple],
                             out_col_types: list[int]) -> AggregationExecutor:
    executor = AggregationExecutor()
    executor.child = child
    executor.group_col_indexes = group_col_indexes
    executor.items = items
    executor.out_col_types = out_col_types
    return executor
