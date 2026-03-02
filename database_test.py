from const import META_PAGE_ID, BYTES_MAGIC_NUMBER, MAGIC_NUMBER_BS
from database import Database, new_database_from_meta, new_database
from file import file_open
from pager import new_pager
from row import new_row, new_row_from_bytes
from value.const import VALUE_TYPE_STRING, VALUE_TYPE_INT
from value.value_int import new_value_int
from value.value_string import new_value_string

DB_NAME = 'test_kv'
TB_NAME = 'data'


def init(name: str) -> tuple[int, Database]:
    fd = file_open(f'{name}.db')
    pager = new_pager(fd)
    meta = pager.page_get(META_PAGE_ID)
    magic_number_bs = meta.read(BYTES_MAGIC_NUMBER)
    if magic_number_bs == MAGIC_NUMBER_BS:
        db = new_database_from_meta(pager, meta)
    else:
        pager.magic_number_set()
        db = new_database(pager)
    return fd, db


def test_create_table():
    _, db = init(DB_NAME)
    table_col_names = ["name", "gender", "score"]
    table_col_types = [VALUE_TYPE_STRING, VALUE_TYPE_STRING, VALUE_TYPE_INT]
    db.create_table(TB_NAME, table_col_names, table_col_types)


def test_create_index():
    _, db = init(DB_NAME)
    index_col_names = ["name"]
    db.create_index(TB_NAME, index_col_names)


def test_add():
    _, db = init(DB_NAME)
    key = new_value_int(10)
    val = new_row(10, [new_value_string("xiaoming"), new_value_string("m"), new_value_int(90)])
    _key = bytes(key)
    _val = bytes(val)
    table = db.get_table(TB_NAME)
    table.data.add([(_key, _val)])


def test_get_one():
    _, db = init(DB_NAME)
    table = db.get_table(TB_NAME)
    key = new_value_int(10)
    val = new_row(10, [new_value_string("xiaoming"), new_value_string("m"), new_value_int(90)])
    _key = bytes(key)
    _val = bytes(val)
    result_row = table.data.get_one(_key)
    assert result_row == _val
    result = new_row_from_bytes(result_row)
    assert result == val
