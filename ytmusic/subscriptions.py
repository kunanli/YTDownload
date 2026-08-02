"""訂閱的播放清單：記住清單網址，之後一行指令就能補上新增的曲目。"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, fields
from datetime import datetime, timezone
from pathlib import Path

from .config import config_home
from .utils import sanitize_filename


def default_store_path() -> Path:
    return config_home() / "subscriptions.json"


@dataclass
class Subscription:
    """一張被追蹤的播放清單。"""

    name: str
    url: str
    added_at: str = ""
    last_sync: str = ""
    last_count: int = 0
    output_dir: str | None = None
    video: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Subscription":
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})


class SubscriptionError(ValueError):
    pass


class Subscriptions:
    """存在 JSON 檔裡的訂閱清單。

    刻意不用 SQLite：這份資料使用者會想直接打開來看、手動編輯。
    """

    def __init__(self, path: Path | str | None = None) -> None:
        self.path = Path(path) if path else default_store_path()
        self._items: list[Subscription] = []
        self._load()

    # -- 讀寫 -------------------------------------------------------------

    def _load(self) -> None:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            self._items = []
            return
        entries = raw.get("subscriptions") if isinstance(raw, dict) else raw
        if not isinstance(entries, list):
            self._items = []
            return
        self._items = [
            Subscription.from_dict(e) for e in entries
            if isinstance(e, dict) and e.get("name") and e.get("url")
        ]

    def save(self) -> Path:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"subscriptions": [s.to_dict() for s in self._items]}
        self.path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        return self.path

    # -- 查詢 -------------------------------------------------------------

    def list(self) -> list[Subscription]:
        return list(self._items)

    def get(self, name: str) -> Subscription | None:
        target = name.strip().lower()
        for item in self._items:
            if item.name.lower() == target:
                return item
        return None

    def __len__(self) -> int:
        return len(self._items)

    # -- 修改 -------------------------------------------------------------

    def add(self, url: str, name: str | None = None, *,
            output_dir: str | None = None, video: str | None = None) -> Subscription:
        url = url.strip()
        if not url:
            raise SubscriptionError("網址不能是空的")
        for item in self._items:
            if item.url == url:
                raise SubscriptionError(f"這個網址已經訂閱了，名稱是 {item.name!r}")

        chosen = sanitize_filename(name.strip()) if name and name.strip() else None
        if chosen and self.get(chosen):
            raise SubscriptionError(f"名稱 {chosen!r} 已經有人用了")
        if not chosen:
            chosen = self._auto_name()

        subscription = Subscription(
            name=chosen, url=url, added_at=_now(),
            output_dir=output_dir, video=video,
        )
        self._items.append(subscription)
        self.save()
        return subscription

    def rename(self, old: str, new: str) -> Subscription:
        item = self.get(old)
        if item is None:
            raise SubscriptionError(f"找不到訂閱：{old}")
        cleaned = sanitize_filename(new.strip())
        if not cleaned or cleaned == "untitled":
            raise SubscriptionError("新名稱不合法")
        if cleaned.lower() != item.name.lower() and self.get(cleaned):
            raise SubscriptionError(f"名稱 {cleaned!r} 已經有人用了")
        item.name = cleaned
        self.save()
        return item

    def remove(self, name: str) -> bool:
        item = self.get(name)
        if item is None:
            return False
        self._items.remove(item)
        self.save()
        return True

    def mark_synced(self, name: str, count: int) -> None:
        item = self.get(name)
        if item is None:
            return
        item.last_sync = _now()
        item.last_count = count
        self.save()

    def _auto_name(self) -> str:
        existing = {i.name.lower() for i in self._items}
        for index in range(1, 1000):
            candidate = f"清單{index}"
            if candidate.lower() not in existing:
                return candidate
        raise SubscriptionError("訂閱數量已達上限")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
