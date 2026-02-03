import time
from utils import Int64


def get_oid():
    timestamp_ms = int(time.time() * 1000)
    return Int64(timestamp_ms)
