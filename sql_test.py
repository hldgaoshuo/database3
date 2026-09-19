import inspect
import os

import pytest

from buffer_pool_manager import new_buffer_pool_manager
from const import META_PAGE_ID, BYTES_MAGIC_NUMBER, MAGIC_NUMBER_BS, BUFFER_POOL_SIZE
from database import Database, new_database, new_database_from_meta
from executor import IndexScanExecutor, SeqScanExecutor
from file import file_open
from pager import new_pager
from wal import new_wal
from sql.engine import execute_sql, build_scan, parse_sql
from value.const import VALUE_TYPE_STRING, VALUE_TYPE_INT

TB_NAME = 'data'


def init(name: str) -> tuple[int, Database]:
    fd = file_open(f'{name}.db')
    pager = new_pager(fd)
    wal = new_wal(f'{name}.db.wal')
    wal.replay(pager)
    wal.truncate()
    pager = new_buffer_pool_manager(pager, BUFFER_POOL_SIZE, wal)
    meta = pager.page_get(META_PAGE_ID)
    magic_number_bs = meta.read(BYTES_MAGIC_NUMBER)
    assert magic_number_bs != MAGIC_NUMBER_BS
    pager.magic_number_set()
    db = new_database(pager)
    return fd, db


def reopen(fd: int, name: str) -> Database:
    pager = new_pager(fd)
    wal = new_wal(f'{name}.db.wal')
    wal.replay(pager)
    wal.truncate()
    pager = new_buffer_pool_manager(pager, BUFFER_POOL_SIZE, wal)
    meta = pager.page_get(META_PAGE_ID)
    magic_number_bs = meta.read(BYTES_MAGIC_NUMBER)
    assert magic_number_bs == MAGIC_NUMBER_BS
    db = new_database_from_meta(pager, meta)
    return db


def close(fd: int, name: str) -> None:
    os.close(fd)
    os.remove(f'{name}.db')
    os.remove(f'{name}.db.wal')


def init_data(db: Database) -> None:
    execute_sql(db, "CREATE TABLE data (name STRING, gender STRING, score INT)")
    execute_sql(db, "CREATE INDEX idx_name ON data (name)")
    assert execute_sql(db, "INSERT INTO data VALUES ('xiaoming', 'm', 90)") == 1
    assert execute_sql(db, "INSERT INTO data VALUES ('xiaohong', 'f', 85)") == 1
    assert execute_sql(db, "INSERT INTO data VALUES ('xiaogang', 'm', 60)") == 1


def names_scores_of(rows) -> list[tuple[str, int]]:
    return sorted((row.vals[0].val, row.vals[1].val) for row in rows)


def test_create_table():
    name = inspect.currentframe().f_code.co_name
    fd, db = init(name)
    execute_sql(db, "CREATE TABLE data (name STRING, gender STRING, score INT)")
    table = db.get_table(TB_NAME)
    assert table.col_names == ["name", "gender", "score"]
    assert table.col_types == [VALUE_TYPE_STRING, VALUE_TYPE_STRING, VALUE_TYPE_INT]
    close(fd, name)


def test_insert_and_select():
    name = inspect.currentframe().f_code.co_name
    fd, db = init(name)
    init_data(db)
    rows = execute_sql(db, "SELECT * FROM data")
    assert names_scores_of(rows) == [("xiaogang", "m"), ("xiaohong", "f"), ("xiaoming", "m")]
    close(fd, name)


def test_select_projection():
    name = inspect.currentframe().f_code.co_name
    fd, db = init(name)
    init_data(db)
    rows = execute_sql(db, "SELECT name, score FROM data")
    assert names_scores_of(rows) == [("xiaogang", 60), ("xiaohong", 85), ("xiaoming", 90)]
    close(fd, name)


def test_select_where():
    name = inspect.currentframe().f_code.co_name
    fd, db = init(name)
    init_data(db)

    rows = execute_sql(db, "SELECT * FROM data WHERE score > 80")
    assert names_scores_of(rows) == [("xiaohong", "f"), ("xiaoming", "m")]

    rows = execute_sql(db, "SELECT * FROM data WHERE score <= 85")
    assert names_scores_of(rows) == [("xiaogang", "m"), ("xiaohong", "f")]

    rows = execute_sql(db, "SELECT * FROM data WHERE score >= 60 AND gender = 'm'")
    assert names_scores_of(rows) == [("xiaogang", "m"), ("xiaoming", "m")]

    # 关键字大小写不敏感
    rows = execute_sql(db, "select * from data where name = 'xiaohong'")
    assert names_scores_of(rows) == [("xiaohong", "f")]
    close(fd, name)


def test_build_scan_uses_index():
    name = inspect.currentframe().f_code.co_name
    fd, db = init(name)
    init_data(db)
    table = db.get_table(TB_NAME)

    # 索引列上的等值条件 → IndexScan
    stmt = parse_sql("SELECT * FROM data WHERE name = 'xiaohong' AND score > 60")
    executor = build_scan(table, stmt.conditions)
    assert isinstance(executor.child, IndexScanExecutor)

    # 非等值条件 → SeqScan + Filter
    stmt = parse_sql("SELECT * FROM data WHERE score > 60")
    executor = build_scan(table, stmt.conditions)
    assert isinstance(executor.child, SeqScanExecutor)
    close(fd, name)


def test_update():
    name = inspect.currentframe().f_code.co_name
    fd, db = init(name)
    init_data(db)

    assert execute_sql(db, "UPDATE data SET score = 95 WHERE name = 'xiaohong'") == 1
    rows = execute_sql(db, "SELECT score FROM data WHERE name = 'xiaohong'")
    assert [row.vals[0].val for row in rows] == [95]

    # 更新索引列：旧 key 失效，新 key 生效
    assert execute_sql(db, "UPDATE data SET name = 'xiaolan' WHERE name = 'xiaohong'") == 1
    assert execute_sql(db, "SELECT * FROM data WHERE name = 'xiaohong'") == []
    assert names_scores_of(execute_sql(db, "SELECT * FROM data WHERE name = 'xiaolan'")) == [("xiaolan", "f")]
    close(fd, name)


def test_delete():
    name = inspect.currentframe().f_code.co_name
    fd, db = init(name)
    init_data(db)

    assert execute_sql(db, "DELETE FROM data WHERE score < 80") == 1
    assert names_scores_of(execute_sql(db, "SELECT * FROM data")) == [("xiaohong", "f"), ("xiaoming", "m")]
    # 索引同步删除
    assert execute_sql(db, "SELECT * FROM data WHERE name = 'xiaogang'") == []
    close(fd, name)


def test_insert_type_mismatch():
    name = inspect.currentframe().f_code.co_name
    fd, db = init(name)
    execute_sql(db, "CREATE TABLE data (name STRING, gender STRING, score INT)")
    with pytest.raises(ValueError):
        execute_sql(db, "INSERT INTO data VALUES (90, 'm', 90)")
    with pytest.raises(ValueError):
        execute_sql(db, "INSERT INTO data VALUES ('xiaoming', 'm')")
    close(fd, name)


def test_reopen():
    name = inspect.currentframe().f_code.co_name
    fd, db = init(name)
    init_data(db)
    db.pager.flush_all_pages()

    db2 = reopen(fd, name)
    rows = execute_sql(db2, "SELECT * FROM data WHERE score >= 85")
    assert names_scores_of(rows) == [("xiaohong", "f"), ("xiaoming", "m")]
    close(fd, name)


def test_group_by():
    name = inspect.currentframe().f_code.co_name
    fd, db = init(name)
    init_data(db)

    rows = execute_sql(db, "SELECT gender, COUNT(*), SUM(score) FROM data GROUP BY gender")
    result = sorted((row.vals[0].val, row.vals[1].val, row.vals[2].val) for row in rows)
    assert result == [("f", 1, 85), ("m", 2, 150)]
    close(fd, name)


def test_aggregation_no_group_by():
    name = inspect.currentframe().f_code.co_name
    fd, db = init(name)
    init_data(db)

    rows = execute_sql(db, "SELECT COUNT(*), MIN(score), MAX(score) FROM data")
    [(row)] = rows
    assert (row.vals[0].val, row.vals[1].val, row.vals[2].val) == (3, 60, 90)

    # WHERE 先过滤，再聚合
    rows = execute_sql(db, "SELECT COUNT(*) FROM data WHERE gender = 'f'")
    assert rows[0].vals[0].val == 1
    close(fd, name)


def test_having():
    name = inspect.currentframe().f_code.co_name
    fd, db = init(name)
    init_data(db)

    rows = execute_sql(db, "SELECT gender, SUM(score) FROM data GROUP BY gender HAVING SUM(score) > 100")
    result = sorted((row.vals[0].val, row.vals[1].val) for row in rows)
    assert result == [("m", 150)]

    # HAVING 引用分组列
    rows = execute_sql(db, "SELECT gender, COUNT(*) FROM data GROUP BY gender HAVING gender = 'f'")
    result = [(row.vals[0].val, row.vals[1].val) for row in rows]
    assert result == [("f", 1)]
    close(fd, name)


def test_aggregation_validation():
    name = inspect.currentframe().f_code.co_name
    fd, db = init(name)
    init_data(db)

    # 普通列必须出现在 GROUP BY 中
    with pytest.raises(ValueError):
        execute_sql(db, "SELECT name, COUNT(*) FROM data")
    # HAVING 引用的列/聚合必须出现在 SELECT 中
    with pytest.raises(ValueError):
        execute_sql(db, "SELECT gender, COUNT(*) FROM data GROUP BY gender HAVING score > 1")
    # SUM 仅支持 INT 列
    with pytest.raises(ValueError):
        execute_sql(db, "SELECT SUM(name) FROM data")
    # WHERE 不支持聚合函数
    with pytest.raises(ValueError):
        execute_sql(db, "SELECT * FROM data WHERE COUNT(*) > 1")
    close(fd, name)
