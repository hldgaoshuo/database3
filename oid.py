import random
import time


def get_oid() -> int:
    timestamp = int(time.time() * 1000)  # 毫秒时间戳
    random_part = random.randint(0, 999)  # 3位随机数
    return timestamp * 1000 + random_part
