import json

import pytest

from ytmusic.subscriptions import SubscriptionError, Subscriptions


@pytest.fixture()
def store(tmp_path):
    return Subscriptions(tmp_path / "subs.json")


def test_starts_empty(store):
    assert store.list() == []
    assert len(store) == 0


def test_add_and_get(store):
    item = store.add("https://youtube.com/playlist?list=PL1", "我的清單")
    assert item.name == "我的清單"
    assert item.added_at
    assert store.get("我的清單") is item
    assert len(store) == 1


def test_lookup_is_case_insensitive(store):
    store.add("https://x/1", "MyList")
    assert store.get("mylist") is not None


def test_auto_names_when_omitted(store):
    assert store.add("https://x/1").name == "清單1"
    assert store.add("https://x/2").name == "清單2"


def test_rejects_duplicate_url(store):
    store.add("https://x/1", "A")
    with pytest.raises(SubscriptionError, match="已經訂閱"):
        store.add("https://x/1", "B")


def test_rejects_duplicate_name(store):
    store.add("https://x/1", "A")
    with pytest.raises(SubscriptionError, match="已經有人用"):
        store.add("https://x/2", "A")


def test_rejects_empty_url(store):
    with pytest.raises(SubscriptionError):
        store.add("   ")


def test_name_is_sanitised(store):
    assert store.add("https://x/1", 'bad/name:here').name == "bad_name_here"


def test_remove(store):
    store.add("https://x/1", "A")
    assert store.remove("A") is True
    assert store.remove("A") is False
    assert len(store) == 0


def test_rename(store):
    store.add("https://x/1", "A")
    assert store.rename("A", "B").name == "B"
    assert store.get("A") is None
    assert store.get("B") is not None


def test_rename_to_taken_name(store):
    store.add("https://x/1", "A")
    store.add("https://x/2", "B")
    with pytest.raises(SubscriptionError):
        store.rename("A", "B")


def test_rename_missing(store):
    with pytest.raises(SubscriptionError, match="找不到"):
        store.rename("nope", "X")


def test_mark_synced(store):
    store.add("https://x/1", "A")
    store.mark_synced("A", 42)
    item = store.get("A")
    assert item.last_count == 42
    assert item.last_sync

    reloaded = Subscriptions(store.path).get("A")
    assert reloaded.last_count == 42


def test_mark_synced_unknown_is_a_no_op(store):
    store.mark_synced("nope", 1)  # 不應拋錯


def test_persists_across_instances(tmp_path):
    path = tmp_path / "subs.json"
    Subscriptions(path).add("https://x/1", "A", output_dir="/music", video="720")

    item = Subscriptions(path).get("A")
    assert item.url == "https://x/1"
    assert item.output_dir == "/music"
    assert item.video == "720"


def test_missing_file_is_empty(tmp_path):
    assert Subscriptions(tmp_path / "nope.json").list() == []


def test_corrupt_file_is_empty(tmp_path):
    path = tmp_path / "subs.json"
    path.write_text("{not json", encoding="utf-8")
    assert Subscriptions(path).list() == []


def test_drops_entries_missing_required_fields(tmp_path):
    path = tmp_path / "subs.json"
    path.write_text(json.dumps({"subscriptions": [
        {"name": "ok", "url": "https://x/1"},
        {"name": "no url"},
        {"url": "https://x/2"},
        "not a dict",
    ]}), encoding="utf-8")
    assert [s.name for s in Subscriptions(path).list()] == ["ok"]


def test_accepts_bare_list_format(tmp_path):
    path = tmp_path / "subs.json"
    path.write_text(json.dumps([{"name": "A", "url": "https://x/1"}]), encoding="utf-8")
    assert [s.name for s in Subscriptions(path).list()] == ["A"]


def test_written_file_is_human_readable(store):
    store.add("https://x/1", "我的清單")
    text = store.path.read_text(encoding="utf-8")
    assert "我的清單" in text  # 沒有被 escape 成 \uXXXX
    assert "\n" in text
