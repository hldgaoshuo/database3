from const import META_PAGE_ID, BYTES_MAGIC_NUMBER, MAGIC_NUMBER_BS
from database import new_database_from_meta, new_database
from file import file_open, get_page, set_magic_number


def __main():
    fd = file_open(f'test.db')
    meta = get_page(fd, META_PAGE_ID)
    magic_number_bs = meta.read(BYTES_MAGIC_NUMBER)
    if magic_number_bs == MAGIC_NUMBER_BS:
        db = new_database_from_meta(fd, meta)
    else:
        set_magic_number(fd)
        db = new_database(fd)


if __name__ == '__main__':
    __main()
