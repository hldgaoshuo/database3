from pager import Pager


class TableSeqGenerator:
    def __init__(self):
        self.pager: Pager | None = None
        self.next_seq: int = 0

    def get_next_seq(self):
        r = self.next_seq
        self.next_seq += 1
        self.pager.table_seq_set(self.next_seq)
        return r


def new_table_seq_generator(pager: Pager, init_seq: int):
    r = TableSeqGenerator()
    r.pager = pager
    r.next_seq = init_seq
    return r
