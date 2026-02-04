import inspect
from const import META_PAGE_ID, BYTES_MAGIC_NUMBER, MAGIC_NUMBER_BS
from database import Database, new_database_from_meta, new_database
from file import file_open, get_page, set_magic_number
from row import new_row
from utils import new_int64
from value.const import VALUE_TYPE_STRING, VALUE_TYPE_INT
from value.value_int import new_value_int
from value.value_int64 import new_value_int64
from value.value_string import new_value_string


def init(name: str) -> tuple[int, Database]:
    fd = file_open(f'{name}.db')
    meta = get_page(fd, META_PAGE_ID)
    magic_number_bs = meta.read(BYTES_MAGIC_NUMBER)
    if magic_number_bs == MAGIC_NUMBER_BS:
        db = new_database_from_meta(fd, meta)
    else:
        set_magic_number(fd)
        db = new_database(fd)
    return fd, db


def test_create():
    name = inspect.currentframe().f_code.co_name
    fd, db = init(name)
    table_name = "data"
    table_col_names = ["name", "gender", "score"]
    table_col_types = [VALUE_TYPE_STRING, VALUE_TYPE_STRING, VALUE_TYPE_INT]
    db.create(table_name, table_col_names, table_col_types)


def test_set():
    name = inspect.currentframe().f_code.co_name
    fd, db = init(name)
    table_name = "data"
    table_col_names = ["name", "gender", "score"]
    table_col_types = [VALUE_TYPE_STRING, VALUE_TYPE_STRING, VALUE_TYPE_INT]
    db.create(table_name, table_col_names, table_col_types)
    key = new_value_int64(new_int64(10))
    row = new_row(new_value_int64(new_int64(10)), [new_value_string("xiaoming"), new_value_string("m"), new_value_int(90)])
    db.set(table_name, key, row)


def test_get():
    name = inspect.currentframe().f_code.co_name
    fd, db = init(name)
    table_name = "data"
    table_col_names = ["name", "gender", "score"]
    table_col_types = [VALUE_TYPE_STRING, VALUE_TYPE_STRING, VALUE_TYPE_INT]
    db.create(table_name, table_col_names, table_col_types)
    key = new_value_int64(new_int64(10))
    row = new_row(new_value_int64(new_int64(10)), [new_value_string("xiaoming"), new_value_string("m"), new_value_int(90)])
    db.set(table_name, key, row)
    result = db.get(table_name, key)
    result.show()
