from pager import Pager


class BPlusTreeSeqGenerator:

    def __init__(self):
        self.pager: Pager | None = None
        self.next_seq: int = 0

    def get_next_seq(self):
        r = self.next_seq
        self.next_seq += 1
        self.pager.b_plus_tree_seq_set(self.next_seq)
        return r


def new_b_plus_tree_seq_generator(pager: Pager, init_seq: int):
    r = BPlusTreeSeqGenerator()
    r.pager = pager
    r.next_seq = init_seq
    return r
