from oid import get_oid


def test():
    for i in range(100):
        r = get_oid()
        print(r.val)
