from const import META_PAGE_ID, BYTES_MAGIC_NUMBER, MAGIC_NUMBER_BS, NULL_PAGE_ID
from file import file_open, get_page
from free_list import new_free_list_from_page_id
from table_list import new_table_list_from_page_id, new_table_seq_generator
from utils import from_buf


def __main():
    fd = file_open(f'test.db')
    meta = get_page(fd, META_PAGE_ID)
    magic_number_bs = meta.read(BYTES_MAGIC_NUMBER)
    if magic_number_bs == MAGIC_NUMBER_BS:
        used_page_id = from_buf(meta, int)
        head_page_id = from_buf(meta, int)
        tail_page_id = from_buf(meta, int)
        free_list = new_free_list_from_page_id(fd, used_page_id, head_page_id, tail_page_id)
        from_buf(meta, int)  # table_seq
        table_head_page_id = from_buf(meta, int)
        table_tail_page_id = from_buf(meta, int)
        table_list = new_table_list_from_page_id(fd, free_list, table_head_page_id, table_tail_page_id)
        tables = table_list.get_tables()
    else:
        pass


if __name__ == '__main__':
    __main()
