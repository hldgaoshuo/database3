import time


def get_oid() -> int:
    timestamp_ms = int(time.time() * 1000)
    return timestamp_ms
