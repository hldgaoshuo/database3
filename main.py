# from const import META_PAGE_ID, BYTES_MAGIC_NUMBER
# from file import file_open, get_page
#
#
# def __main():
#     fd = file_open(f'test.db')
#     mete = get_page(fd, META_PAGE_ID)
#     magic_number_bs = mete.read(BYTES_MAGIC_NUMBER)
#     if magic_number_bs == MAGIC_NUMBER_BS:
#         used_page_id = from_buf(mete, int)
#         head_page_id = from_buf(mete, int)
#         tail_page_id = from_buf(mete, int)
#         free_list = new_free_list_from_page_id(fd, used_page_id, head_page_id, tail_page_id)
#         root_page_id = from_buf(mete, int)
#         b_plus_tree = new_b_plus_tree_from_root_page_id(fd, seq, free_list, root_page_id)
#     else:
#         pass
#
#
# if __name__ == '__main__':
#     __main()
