import inspect
import os

import pytest

from buffer_pool_manager import new_buffer_pool_manager
from const import META_PAGE_ID, BYTES_MAGIC_NUMBER, MAGIC_NUMBER_BS, BUFFER_POOL_SIZE, OP_EQ, OP_GT, OP_LE, \
    AGG_COUNT, AGG_SUM, AGG_MIN, AGG_MAX
from database import Database, new_database
from executor import index_key, new_values_executor, new_seq_scan_executor, new_index_scan_executor, \
    new_filter_executor, new_projection_executor, new_insert_executor, new_update_executor, new_delete_executor, \
    new_aggregation_executor
from file import file_open
from pager import new_pager
from row import Row, new_row, new_row_from_bytes
from table import Table
from value.const import VALUE_TYPE_STRING, VALUE_TYPE_INT
from value.value_int import new_value_int
from value.value_string import new_value_string

TB_NAME = 'data'


def init(name: str) -> tuple[int, Database]:
    fd = file_open(f'{name}.db')
    pager = new_buffer_pool_manager(new_pager(fd), BUFFER_POOL_SIZE)
    meta = pager.page_get(META_PAGE_ID)
    magic_number_bs = meta.read(BYTES_MAGIC_NUMBER)
    assert magic_number_bs != MAGIC_NUMBER_BS
    pager.magic_number_set()
    db = new_database(pager)
    return fd, db


def close(fd: int, name: str) -> None:
    os.close(fd)
    os.remove(f'{name}.db')


def make_table(db: Database) -> Table:
    col_names = ["name", "gender", "score"]
    col_types = [VALUE_TYPE_STRING, VALUE_TYPE_STRING, VALUE_TYPE_INT]
    db.create_table(TB_NAME, col_names, col_types)
    db.create_index(TB_NAME, ["name"])
    return db.get_table(TB_NAME)


def make_row(name: str, gender: str, score: int) -> Row:
    return new_row([new_value_string(name), new_value_string(gender), new_value_int(score)])


def make_table_with_rows(db: Database) -> tuple[Table, list[Row]]:
    table = make_table(db)
    rows = [make_row("xiaoming", "m", 90), make_row("xiaohong", "f", 85), make_row("xiaogang", "m", 60)]
    executor = new_insert_executor(table, new_values_executor(rows))
    for _ in executor:
        pass
    return table, rows


def test_seq_scan():
    name = inspect.currentframe().f_code.co_name
    fd, db = init(name)
    table, rows = make_table_with_rows(db)

    result = list(new_seq_scan_executor(table))
    assert len(result) == 3
    for oid, row in result:
        assert oid is not None
        assert row in rows
    close(fd, name)


def names_of(rows: list[Row]) -> list[str]:
    return sorted(row.vals[0].val for row in rows)


def test_filter():
    name = inspect.currentframe().f_code.co_name
    fd, db = init(name)
    table, rows = make_table_with_rows(db)

    scan = new_seq_scan_executor(table)
    executor = new_filter_executor(scan, 2, OP_GT, new_value_int(80))
    result = [row for _, row in executor]
    assert names_of(result) == ["xiaohong", "xiaoming"]

    scan = new_seq_scan_executor(table)
    executor = new_filter_executor(scan, 2, OP_LE, new_value_int(85))
    result = [row for _, row in executor]
    assert names_of(result) == ["xiaogang", "xiaohong"]

    scan = new_seq_scan_executor(table)
    executor = new_filter_executor(scan, 0, OP_EQ, new_value_string("xiaohong"))
    result = [row for _, row in executor]
    assert result == [rows[1]]
    close(fd, name)


def test_projection():
    name = inspect.currentframe().f_code.co_name
    fd, db = init(name)
    table, rows = make_table_with_rows(db)

    scan = new_seq_scan_executor(table)
    executor = new_projection_executor(scan, [0, 2])
    result = sorted((row.vals[0].val, row.vals[1].val) for _, row in executor)
    assert result == [("xiaogang", 60), ("xiaohong", 85), ("xiaoming", 90)]
    close(fd, name)


def test_index_scan():
    name = inspect.currentframe().f_code.co_name
    fd, db = init(name)
    table, rows = make_table_with_rows(db)

    key_row = new_row([new_value_string("xiaohong")])
    executor = new_index_scan_executor(table, (0,), key_row)
    result = [row for _, row in executor]
    assert result == [rows[1]]

    key_row = new_row([new_value_string("nobody")])
    executor = new_index_scan_executor(table, (0,), key_row)
    result = [row for _, row in executor]
    assert result == []
    close(fd, name)


def test_insert_updates_index():
    name = inspect.currentframe().f_code.co_name
    fd, db = init(name)
    table = make_table(db)
    row = make_row("xiaoming", "m", 90)

    executor = new_insert_executor(table, new_values_executor([row]))
    [(oid, _)] = list(executor)

    # 主树可查
    assert new_row_from_bytes(table.data.get_one(oid)) == row
    # 二级索引可查且能回表
    index = table.indexes[(0,)]
    val_bs = index.get_one(index_key(row, (0,)))
    assert val_bs is not None
    val_row = new_row_from_bytes(val_bs)
    assert table.data.get_one(bytes(val_row.vals[0])) is not None
    close(fd, name)


def test_delete():
    name = inspect.currentframe().f_code.co_name
    fd, db = init(name)
    table, rows = make_table_with_rows(db)

    scan = new_seq_scan_executor(table)
    child = new_filter_executor(scan, 0, OP_EQ, new_value_string("xiaohong"))
    executor = new_delete_executor(table, child)
    deleted = [row for _, row in executor]
    assert deleted == [rows[1]]

    # 主树和索引都删掉了
    result = [row for _, row in new_seq_scan_executor(table)]
    assert names_of(result) == ["xiaogang", "xiaoming"]
    index = table.indexes[(0,)]
    assert index.get_one(index_key(rows[1], (0,))) is None
    assert index.get_one(index_key(rows[0], (0,))) is not None
    close(fd, name)


def test_update():
    name = inspect.currentframe().f_code.co_name
    fd, db = init(name)
    table, rows = make_table_with_rows(db)

    scan = new_seq_scan_executor(table)
    child = new_filter_executor(scan, 0, OP_EQ, new_value_string("xiaohong"))
    assignments = [(0, new_value_string("xiaolan")), (2, new_value_int(95))]
    executor = new_update_executor(table, child, assignments)
    updated = [row for _, row in executor]
    row_new = make_row("xiaolan", "f", 95)
    assert updated == [row_new]

    # 旧索引 key 失效，新索引 key 生效，主树已更新
    index = table.indexes[(0,)]
    assert index.get_one(index_key(rows[1], (0,))) is None
    assert index.get_one(index_key(row_new, (0,))) is not None
    result = [row for _, row in new_seq_scan_executor(table)]
    assert names_of(result) == ["xiaogang", "xiaolan", "xiaoming"]
    assert row_new in result
    close(fd, name)


def test_aggregation_group_by():
    name = inspect.currentframe().f_code.co_name
    fd, db = init(name)
    table, rows = make_table_with_rows(db)

    # SELECT gender, COUNT(*), SUM(score) FROM data GROUP BY gender
    scan = new_seq_scan_executor(table)
    items = [('col', 0), (AGG_COUNT, None), (AGG_SUM, 2)]
    out_col_types = [VALUE_TYPE_STRING, VALUE_TYPE_INT, VALUE_TYPE_INT]
    executor = new_aggregation_executor(scan, [1], items, out_col_types)
    result = sorted((row.vals[0].val, row.vals[1].val, row.vals[2].val) for _, row in executor)
    assert result == [("f", 1, 85), ("m", 2, 150)]
    close(fd, name)


def test_aggregation_no_group_by():
    name = inspect.currentframe().f_code.co_name
    fd, db = init(name)
    table, rows = make_table_with_rows(db)

    # SELECT COUNT(*), MIN(score), MAX(score) FROM data
    scan = new_seq_scan_executor(table)
    items = [(AGG_COUNT, None), (AGG_MIN, 2), (AGG_MAX, 2)]
    out_col_types = [VALUE_TYPE_INT, VALUE_TYPE_INT, VALUE_TYPE_INT]
    executor = new_aggregation_executor(scan, [], items, out_col_types)
    [(oid, row)] = list(executor)
    assert oid is None
    assert (row.vals[0].val, row.vals[1].val, row.vals[2].val) == (3, 60, 90)
    close(fd, name)


def test_aggregation_empty_table():
    name = inspect.currentframe().f_code.co_name
    fd, db = init(name)
    table = make_table(db)

    # 空表无 GROUP BY：COUNT 输出 0
    scan = new_seq_scan_executor(table)
    executor = new_aggregation_executor(scan, [], [(AGG_COUNT, None)], [VALUE_TYPE_INT])
    [(_, row)] = list(executor)
    assert row.vals[0].val == 0

    # 空表无 GROUP BY：SUM/MIN/MAX 无定义（暂不支持 NULL）
    scan = new_seq_scan_executor(table)
    executor = new_aggregation_executor(scan, [], [(AGG_SUM, 2)], [VALUE_TYPE_INT])
    with pytest.raises(ValueError):
        list(executor)

    # 空表有 GROUP BY：输出零行
    scan = new_seq_scan_executor(table)
    executor = new_aggregation_executor(scan, [1], [('col', 0), (AGG_COUNT, None)],
                                        [VALUE_TYPE_STRING, VALUE_TYPE_INT])
    assert list(executor) == []
    close(fd, name)
