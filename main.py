from buffer_pool_manager import new_buffer_pool_manager
from const import META_PAGE_ID, BYTES_MAGIC_NUMBER, MAGIC_NUMBER_BS, BUFFER_POOL_SIZE
from database import new_database_from_meta, new_database
from file import file_open
from pager import new_pager


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
    pager.flush_all_pages()


if __name__ == '__main__':
    __main()
