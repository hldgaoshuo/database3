from lru_replacer import LRUReplacer


def test_evict_order():
    replacer = LRUReplacer()
    replacer.record_access(1)
    replacer.record_access(2)
    replacer.record_access(3)
    assert replacer.evict() == 1
    assert replacer.evict() == 2
    assert replacer.evict() == 3
    assert replacer.evict() is None


def test_record_access_refresh():
    replacer = LRUReplacer()
    replacer.record_access(1)
    replacer.record_access(2)
    replacer.record_access(1)
    assert replacer.evict() == 2
    assert replacer.evict() == 1


def test_evict_empty():
    replacer = LRUReplacer()
    assert replacer.evict() is None


def test_size():
    replacer = LRUReplacer()
    assert replacer.size() == 0
    replacer.record_access(1)
    replacer.record_access(2)
    assert replacer.size() == 2
    replacer.record_access(1)
    assert replacer.size() == 2
    replacer.evict()
    assert replacer.size() == 1
