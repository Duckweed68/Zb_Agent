"""记忆系统测试"""
import pytest
from zb_agent.memory.short_term import ShortTermMemory
from zb_agent.memory.long_term import LongTermMemory


# ── ShortTermMemory ──────────────────────────────────────────
def test_short_term_store_retrieve():
    mem = ShortTermMemory()
    mem.store("key1", "value1")
    assert mem.retrieve("key1") == "value1"


def test_short_term_overwrite():
    mem = ShortTermMemory()
    mem.store("k", "v1")
    mem.store("k", "v2")
    assert mem.retrieve("k") == "v2"


def test_short_term_max_size():
    mem = ShortTermMemory(max_size=3)
    for i in range(5):
        mem.store(f"key{i}", f"val{i}")
    assert len(mem) <= 3


def test_short_term_search():
    mem = ShortTermMemory()
    mem.store("python_tip", "使用列表推导式")
    mem.store("java_tip", "使用流式API")
    results = mem.search("python")
    assert any("python" in k for k, _ in results)


def test_short_term_clear():
    mem = ShortTermMemory()
    mem.store("k", "v")
    mem.clear()
    assert mem.retrieve("k") is None
    assert len(mem) == 0


def test_short_term_retrieve_missing():
    mem = ShortTermMemory()
    assert mem.retrieve("nonexistent") is None


# ── LongTermMemory ───────────────────────────────────────────
def test_long_term_store_retrieve():
    mem = LongTermMemory(db_path=":memory:")
    mem.store("fact1", "Python 由 Guido 创建")
    assert mem.retrieve("fact1") == "Python 由 Guido 创建"


def test_long_term_overwrite():
    mem = LongTermMemory(db_path=":memory:")
    mem.store("k", "old")
    mem.store("k", "new")
    assert mem.retrieve("k") == "new"


def test_long_term_search_by_key():
    mem = LongTermMemory(db_path=":memory:")
    mem.store("python_fact", "Python 是解释型语言")
    results = mem.search("python")
    assert len(results) >= 1


def test_long_term_search_by_value():
    mem = LongTermMemory(db_path=":memory:")
    mem.store("lang", "Python 是解释型语言")
    results = mem.search("解释型")
    assert len(results) == 1
    assert results[0][0] == "lang"


def test_long_term_search_by_tags():
    mem = LongTermMemory(db_path=":memory:")
    mem.store("note1", "重要备注", tags="工作,紧急")
    results = mem.search("紧急")
    assert len(results) == 1


def test_long_term_clear():
    mem = LongTermMemory(db_path=":memory:")
    mem.store("k", "v")
    mem.clear()
    assert mem.retrieve("k") is None


def test_long_term_retrieve_missing():
    mem = LongTermMemory(db_path=":memory:")
    assert mem.retrieve("missing") is None
