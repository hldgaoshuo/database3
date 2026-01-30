import threading


class OIDGenerator:

    def __init__(self):
        self.id_: int = 1
        self.lock: threading.Lock = threading.Lock()

    def get_oid(self):
        with self.lock:
            r = self.id_
            self.id_ += 1
            return r


default_oid_generator = OIDGenerator()


def get_oid():
    return default_oid_generator.get_oid()
