from buffer_pool_manager import new_buffer_pool_manager
from const import META_PAGE_ID, BYTES_MAGIC_NUMBER, MAGIC_NUMBER_BS, BUFFER_POOL_SIZE
from database import new_database_from_meta, new_database
from file import file_open
from pager import new_pager
from sql.engine import execute_sql


def __main():
    fd = file_open(f'test.db')
    pager = new_buffer_pool_manager(new_pager(fd), BUFFER_POOL_SIZE)
    meta = pager.page_get(META_PAGE_ID)
    magic_number_bs = meta.read(BYTES_MAGIC_NUMBER)
    if magic_number_bs == MAGIC_NUMBER_BS:
        db = new_database_from_meta(pager, meta)
    else:
        pager.magic_number_set()
        db = new_database(pager)

    if db.tables['data'] is None:
        execute_sql(db, "CREATE TABLE data (name STRING, gender STRING, score INT)")
        execute_sql(db, "INSERT INTO data VALUES ('xiaoming', 'm', 90)")
        execute_sql(db, "INSERT INTO data VALUES ('xiaohong', 'f', 85)")
    rows = execute_sql(db, "SELECT * FROM data WHERE score > 80")
    for row in rows:
        row.show()
    pager.flush_all_pages()


if __name__ == '__main__':
    __main()
