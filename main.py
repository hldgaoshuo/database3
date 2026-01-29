import io

from b_plus_tree import BPlusTree, new_b_plus_tree, new_b_plus_tree_from_root_page_id
from free_list import new_free_list, new_free_list_from_page_id
from const import META_PAGE_ID, BYTES_MAGIC_NUMBER, MAGIC_NUMBER_BS
from file import file_open, get_page, set_magic_number
from utils import from_bytes


def init() -> BPlusTree:
    fd = file_open('test.db')
    meta_bs = get_page(fd, META_PAGE_ID)
    meta_buf = io.BytesIO(meta_bs)
    magic_number_bs = meta_buf.read(BYTES_MAGIC_NUMBER)
    if magic_number_bs == MAGIC_NUMBER_BS:
        used_page_id = from_bytes(meta_buf, int)
        head_page_id = from_bytes(meta_buf, int)
        tail_page_id = from_bytes(meta_buf, int)
        free_list = new_free_list_from_page_id(fd, used_page_id, head_page_id, tail_page_id)
        root_page_id = from_bytes(meta_buf, int)
        b_plus_tree = new_b_plus_tree_from_root_page_id(fd, free_list, root_page_id)
    else:
        set_magic_number(fd)
        id_generator = new_free_list(fd, META_PAGE_ID)
        b_plus_tree = new_b_plus_tree(fd, id_generator)
    return b_plus_tree


def __main():
    tree = init()


if __name__ == '__main__':
    __main()
