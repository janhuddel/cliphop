import pytest

from cliphop.db import Store


def make_store(ttl=3600, max_items=50):
    return Store(":memory:", ttl, max_items)


def test_add_and_read_newest_first():
    store = make_store()
    first = store.add("erst", now=1)
    second = store.add("dann", now=2)
    items = store.list_items(now=2)
    assert [item.id for item in items] == [second.id, first.id]
    assert [item.content for item in items] == ["dann", "erst"]


@pytest.mark.parametrize("content", ["", "   ", "\n\t"])
def test_add_rejects_empty(content):
    store = make_store()
    with pytest.raises(ValueError):
        store.add(content, now=1)
    assert store.list_items(now=1) == []


def test_toggle_pin():
    store = make_store()
    item = store.add("text", now=1)
    assert store.list_items(now=1)[0].pinned is False
    pinned = store.toggle_pin(item.id, now=1)
    assert pinned is not None and pinned.pinned is True
    assert store.list_items(now=1)[0].pinned is True
    assert store.toggle_pin(item.id, now=1).pinned is False


def test_toggle_pin_missing_returns_none():
    store = make_store()
    assert store.toggle_pin(999, now=1) is None


def test_delete_removes_pinned_too():
    store = make_store()
    item = store.add("text", now=1)
    store.toggle_pin(item.id, now=1)
    assert store.delete(item.id, now=1) is True
    assert store.list_items(now=1) == []
    assert store.delete(item.id, now=1) is False


def test_ttl_removes_expired_unpinned():
    store = make_store(ttl=100)
    store.add("alt", now=0)
    assert store.list_items(now=200) == []


def test_pin_survives_ttl():
    store = make_store(ttl=100)
    item = store.add("wichtig", now=0)
    store.toggle_pin(item.id, now=0)
    assert [i.content for i in store.list_items(now=10_000)] == ["wichtig"]


def test_unpinning_expired_item_removes_it():
    store = make_store(ttl=100)
    item = store.add("x", now=0)
    store.toggle_pin(item.id, now=0)
    assert store.toggle_pin(item.id, now=10_000) is None


def test_cap_removes_oldest_unpinned():
    store = make_store(max_items=2)
    store.add("a", now=1)
    store.add("b", now=2)
    store.add("c", now=3)
    assert [i.content for i in store.list_items(now=3)] == ["c", "b"]


def test_cap_keeps_pinned_and_drops_oldest_unpinned():
    store = make_store(max_items=2)
    a = store.add("a", now=1)
    store.toggle_pin(a.id, now=1)
    store.add("b", now=2)
    store.add("c", now=3)
    store.add("d", now=4)
    contents = {i.content for i in store.list_items(now=4)}
    assert contents == {"a", "c", "d"}


def test_clear_only_unpinned():
    store = make_store()
    store.add("weg", now=1)
    keep = store.add("bleibt", now=2)
    store.toggle_pin(keep.id, now=2)
    removed = store.clear(include_pinned=False, now=2)
    assert removed == 1
    assert [i.content for i in store.list_items(now=2)] == ["bleibt"]


def test_clear_including_pinned():
    store = make_store()
    store.add("eins", now=1)
    keep = store.add("zwei", now=2)
    store.toggle_pin(keep.id, now=2)
    assert store.clear(include_pinned=True, now=2) == 2
    assert store.list_items(now=2) == []
