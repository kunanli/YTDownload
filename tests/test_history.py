import threading

import pytest

from ytmusic.history import History


@pytest.fixture()
def history(tmp_path):
    with History(tmp_path / "history.db") as h:
        yield h


def test_starts_empty(history):
    assert history.count() == 0
    assert history.list() == []
    assert not history.has("abc")


def test_add_and_get(history, tmp_path):
    song = tmp_path / "song.mp3"
    song.write_bytes(b"data")
    history.add(
        "vid1", title="Song", artist="Artist", album="Album",
        url="https://example.com/v", filepath=song, audio_format="mp3", filesize=4,
    )

    entry = history.get("vid1")
    assert entry is not None
    assert (entry.title, entry.artist, entry.album) == ("Song", "Artist", "Album")
    assert entry.filesize == 4
    assert entry.exists()
    assert history.has("vid1")
    assert history.count() == 1


def test_add_is_idempotent_and_updates(history):
    history.add("vid1", title="Old")
    history.add("vid1", title="New")
    assert history.count() == 1
    assert history.get("vid1").title == "New"


def test_known_ids_filters(history):
    history.add("a")
    history.add("c")
    assert history.known_ids(["a", "b", "c", "d"]) == {"a", "c"}


def test_known_ids_handles_empty_and_large_batches(history):
    assert history.known_ids([]) == set()
    for i in range(1200):
        history.add(f"id{i}")
    found = history.known_ids([f"id{i}" for i in range(1200)] + ["missing"])
    assert len(found) == 1200
    assert "missing" not in found


def test_remove(history):
    history.add("vid1")
    assert history.remove("vid1") is True
    assert history.remove("vid1") is False
    assert history.count() == 0


def test_clear(history):
    history.add("a")
    history.add("b")
    assert history.clear() == 2
    assert history.count() == 0


def test_prune_drops_missing_files(history, tmp_path):
    present = tmp_path / "here.mp3"
    present.write_bytes(b"x")
    history.add("keep", filepath=present)
    history.add("drop", filepath=tmp_path / "gone.mp3")

    stale = history.prune()
    assert [e.video_id for e in stale] == ["drop"]
    assert history.has("keep")
    assert not history.has("drop")


def test_list_respects_limit(history):
    for i in range(5):
        history.add(f"id{i}")
    assert len(history.list(limit=2)) == 2
    assert len(history.list(limit=None)) == 5


def test_concurrent_writes_are_safe(tmp_path):
    with History(tmp_path / "h.db") as history:
        def worker(start):
            for i in range(start, start + 50):
                history.add(f"id{i}", title=f"t{i}")

        threads = [threading.Thread(target=worker, args=(n * 50,)) for n in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert history.count() == 200
