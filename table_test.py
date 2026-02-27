import inspect
import os

from const import META_PAGE_ID
from file import file_open
from free_list import new_free_list
from pager import new_pager
from row import new_row, new_row_from_bytes
from table import Table, new_table
from value.const import VALUE_TYPE_STRING, VALUE_TYPE_INT
from value.value_int import new_value_int
from value.value_string import new_value_string


def init_table(name: str) -> tuple[int, Table]:
    col_names = ["name", "gender", "score"]
    col_types = [VALUE_TYPE_STRING, VALUE_TYPE_STRING, VALUE_TYPE_INT]
    seq = 0
    fd = file_open(f'{name}.db')
    pager = new_pager(fd)
    pager.magic_number_set()
    free_list = new_free_list(pager, META_PAGE_ID)
    table = new_table(name, col_names, col_types, pager, free_list, seq)
    return fd, table


def close_table(fd: int, name: str) -> None:
    os.close(fd)
    os.remove(f'{name}.db')


def test_table():
    name = inspect.currentframe().f_code.co_name
    fd, table = init_table(name)
    key = 10
    row = new_row(10, [new_value_string("xiaoming"), new_value_string("m"), new_value_int(90)])
    _key = bytes(key)
    _row = bytes(row)
    key_vals = [(_key, _row)]
    table.data.add(key_vals)
    _row = table.data.get_one(_key)
    row = new_row_from_bytes(_row)
    row.show()
    close_table(fd, name)