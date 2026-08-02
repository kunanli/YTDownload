"""下載歷史：以 SQLite 記錄已下載的影片，重跑時自動略過。"""

from __future__ import annotations

import sqlite3
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .config import config_home

_SCHEMA = """
CREATE TABLE IF NOT EXISTS downloads (
    video_id      TEXT PRIMARY KEY,
    title         TEXT NOT NULL DEFAULT '',
    artist        TEXT NOT NULL DEFAULT '',
    album         TEXT NOT NULL DEFAULT '',
    url           TEXT NOT NULL DEFAULT '',
    filepath      TEXT NOT NULL DEFAULT '',
    audio_format  TEXT NOT NULL DEFAULT '',
    filesize      INTEGER NOT NULL DEFAULT 0,
    downloaded_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_downloads_time ON downloads (downloaded_at DESC);
"""


@dataclass(frozen=True)
class Entry:
    video_id: str
    title: str
    artist: str
    album: str
    url: str
    filepath: str
    audio_format: str
    filesize: int
    downloaded_at: str

    @property
    def path(self) -> Path:
        return Path(self.filepath)

    def exists(self) -> bool:
        return bool(self.filepath) and self.path.is_file()


def default_history_path() -> Path:
    return config_home() / "history.db"


class History:
    """已下載影片的持久化紀錄。

    連線開在多執行緒模式並由一把鎖保護，讓平行下載的 worker 可以共用同一個
    History 實例。
    """

    def __init__(self, path: Path | str | None = None) -> None:
        self.path = Path(path) if path else default_history_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        with self._lock:
            self._conn.executescript(_SCHEMA)
            self._conn.commit()

    # -- 生命週期 ---------------------------------------------------------

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def __enter__(self) -> "History":
        return self

    def __exit__(self, *_exc) -> None:
        self.close()

    # -- 查詢 -------------------------------------------------------------

    def has(self, video_id: str) -> bool:
        return self.get(video_id) is not None

    def get(self, video_id: str) -> Entry | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM downloads WHERE video_id = ?", (video_id,)
            ).fetchone()
        return _to_entry(row) if row else None

    def known_ids(self, video_ids: list[str]) -> set[str]:
        """一次查出多個 ID 中已存在的部分，避免逐筆查詢。"""
        if not video_ids:
            return set()
        found: set[str] = set()
        with self._lock:
            # SQLite 的參數上限預設是 999，分批查。
            for start in range(0, len(video_ids), 500):
                chunk = video_ids[start : start + 500]
                placeholders = ",".join("?" * len(chunk))
                rows = self._conn.execute(
                    f"SELECT video_id FROM downloads WHERE video_id IN ({placeholders})",
                    chunk,
                ).fetchall()
                found.update(r["video_id"] for r in rows)
        return found

    def list(self, limit: int | None = 50) -> list[Entry]:
        query = "SELECT * FROM downloads ORDER BY downloaded_at DESC"
        params: tuple = ()
        if limit is not None:
            query += " LIMIT ?"
            params = (limit,)
        with self._lock:
            rows = self._conn.execute(query, params).fetchall()
        return [_to_entry(r) for r in rows]

    def count(self) -> int:
        with self._lock:
            return self._conn.execute("SELECT COUNT(*) FROM downloads").fetchone()[0]

    # -- 寫入 -------------------------------------------------------------

    def add(
        self,
        video_id: str,
        *,
        title: str = "",
        artist: str = "",
        album: str = "",
        url: str = "",
        filepath: str | Path = "",
        audio_format: str = "",
        filesize: int = 0,
    ) -> None:
        """新增或更新一筆紀錄（同一支影片重下會覆蓋舊紀錄）。"""
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO downloads
                    (video_id, title, artist, album, url, filepath,
                     audio_format, filesize, downloaded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(video_id) DO UPDATE SET
                    title=excluded.title, artist=excluded.artist,
                    album=excluded.album, url=excluded.url,
                    filepath=excluded.filepath, audio_format=excluded.audio_format,
                    filesize=excluded.filesize, downloaded_at=excluded.downloaded_at
                """,
                (
                    video_id, title, artist, album, url, str(filepath),
                    audio_format, int(filesize),
                    datetime.now(timezone.utc).isoformat(timespec="seconds"),
                ),
            )
            self._conn.commit()

    def remove(self, video_id: str) -> bool:
        with self._lock:
            cur = self._conn.execute(
                "DELETE FROM downloads WHERE video_id = ?", (video_id,)
            )
            self._conn.commit()
        return cur.rowcount > 0

    def clear(self) -> int:
        with self._lock:
            cur = self._conn.execute("DELETE FROM downloads")
            self._conn.commit()
        return cur.rowcount

    def prune(self) -> list[Entry]:
        """刪除檔案已不存在的紀錄，回傳被刪掉的項目。"""
        stale = [e for e in self.list(limit=None) if not e.exists()]
        if stale:
            with self._lock:
                self._conn.executemany(
                    "DELETE FROM downloads WHERE video_id = ?",
                    [(e.video_id,) for e in stale],
                )
                self._conn.commit()
        return stale


def _to_entry(row: sqlite3.Row) -> Entry:
    return Entry(
        video_id=row["video_id"],
        title=row["title"],
        artist=row["artist"],
        album=row["album"],
        url=row["url"],
        filepath=row["filepath"],
        audio_format=row["audio_format"],
        filesize=row["filesize"],
        downloaded_at=row["downloaded_at"],
    )
