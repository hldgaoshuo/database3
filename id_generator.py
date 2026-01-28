from file import set_used_page_id


class IDGenerator:
    def __init__(self, fd: int, init_page_id: int):
        self.fd: int = fd
        self.used_page_id: int = init_page_id

    def get_used_page_id(self):
        return self.used_page_id

    def get_next_page_id(self):
        self.used_page_id += 1
        set_used_page_id(self.fd, self.used_page_id)
        return self.used_page_id


def new_id_generator(fd: int, init_page_id: int):
    return IDGenerator(fd, init_page_id)