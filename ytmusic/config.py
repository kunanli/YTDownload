"""使用者設定：預設值、設定檔讀寫，以及命令列覆寫。"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, fields
from pathlib import Path

AUDIO_FORMATS = ("mp3", "m4a", "opus", "flac", "wav")
QUALITIES = ("best", "320", "256", "192", "160", "128", "96")

DEFAULT_TEMPLATE = "%(artist,uploader)s - %(track,title)s.%(ext)s"


def config_home() -> Path:
    """設定檔與下載紀錄的存放目錄（可用 YTMUSIC_HOME 覆寫）。"""
    override = os.environ.get("YTMUSIC_HOME")
    if override:
        return Path(override).expanduser()
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg).expanduser() / "ytmusic"
    return Path.home() / ".config" / "ytmusic"


def default_output_dir() -> Path:
    return Path.home() / "Music" / "ytmusic"


@dataclass
class Config:
    """一次下載所需的全部設定。"""

    output_dir: Path = None  # type: ignore[assignment]
    audio_format: str = "mp3"
    quality: str = "192"
    concurrency: int = 3
    convert: bool = True
    write_tags: bool = True
    embed_cover: bool = True
    square_cover: bool = True
    use_history: bool = True
    playlist_folder: bool = False
    rename_from_tags: bool = True
    # 短網址連不上時自動展開成完整網址。會把網址送給第三方服務，
    # 所以預設關閉——要嘛使用者當場同意，要嘛自己打開。
    expand_short_urls: bool = False
    subtitle_langs: str = "zh-TW,zh-Hans,en,ja,ko,es"
    filename_template: str = DEFAULT_TEMPLATE
    cookies_file: str | None = None
    cookies_from_browser: str | None = None
    proxy: str | None = None
    rate_limit: str | None = None
    # 假扮瀏覽器的 TLS 指紋（需要 curl_cffi），例如 chrome、firefox。
    impersonate: str | None = None

    def __post_init__(self) -> None:
        self.output_dir = Path(self.output_dir).expanduser() if self.output_dir else default_output_dir()
        self.audio_format = self.audio_format.lower()
        self.quality = str(self.quality).lower()
        self.concurrency = max(1, min(int(self.concurrency), 16))

    # -- 驗證 -------------------------------------------------------------

    def validate(self) -> list[str]:
        """回傳設定中的問題描述，全部合法時回傳空 list。"""
        problems: list[str] = []
        if self.audio_format not in AUDIO_FORMATS:
            problems.append(
                f"不支援的音訊格式 {self.audio_format!r}，可用：{', '.join(AUDIO_FORMATS)}"
            )
        if self.quality not in QUALITIES:
            problems.append(f"不支援的音質 {self.quality!r}，可用：{', '.join(QUALITIES)}")
        if "%(ext)s" not in self.filename_template:
            problems.append("filename_template 必須包含 %(ext)s，否則副檔名會遺失")
        if self.cookies_file and not Path(self.cookies_file).expanduser().is_file():
            problems.append(f"找不到 cookies 檔案：{self.cookies_file}")
        if self.cookies_from_browser:
            problems.extend(_check_browser_spec(self.cookies_from_browser))
        return problems

    # -- 序列化 -----------------------------------------------------------

    def to_dict(self) -> dict:
        data = asdict(self)
        data["output_dir"] = str(self.output_dir)
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})

    # -- 檔案 -------------------------------------------------------------

    @classmethod
    def path(cls) -> Path:
        return config_home() / "config.json"

    @classmethod
    def load(cls, path: Path | None = None) -> "Config":
        """讀取設定檔；檔案不存在或損壞時回傳預設值。"""
        target = path or cls.path()
        try:
            raw = json.loads(target.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return cls()
        if not isinstance(raw, dict):
            return cls()
        return cls.from_dict(raw)

    def save(self, path: Path | None = None) -> Path:
        target = path or self.path()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return target

    # -- 覆寫 -------------------------------------------------------------

    def merged(self, **overrides) -> "Config":
        """套用非 None 的覆寫值後回傳新的 Config（原物件不變）。"""
        data = self.to_dict()
        known = {f.name for f in fields(type(self))}
        for key, value in overrides.items():
            if value is None or key not in known:
                continue
            data[key] = value
        return type(self).from_dict(data)


def _check_browser_spec(spec: str) -> list[str]:
    """在真的開始下載前先驗證 --cookies-from-browser 的寫法與瀏覽器名稱。"""
    from .utils import parse_browser_spec

    try:
        name, _profile, _keyring, _container = parse_browser_spec(spec)
    except ValueError as exc:
        return [str(exc)]

    try:  # yt-dlp 未安裝時就跳過名稱檢查，讓下載階段自己報錯。
        from yt_dlp.cookies import SUPPORTED_BROWSERS
    except ImportError:
        return []
    if name not in SUPPORTED_BROWSERS:
        return [
            f"不支援的瀏覽器 {name!r}，可用："
            f"{', '.join(sorted(SUPPORTED_BROWSERS))}"
        ]
    return []


def coerce_value(field_name: str, raw: str):
    """把 ``config set`` 傳進來的字串轉成該欄位的正確型別。"""
    types = {f.name: f.type for f in fields(Config)}
    if field_name not in types:
        raise KeyError(field_name)

    lowered = raw.strip().lower()
    bool_fields = {
        "convert", "write_tags", "embed_cover", "square_cover",
        "use_history", "playlist_folder", "rename_from_tags",
        "expand_short_urls",
    }
    if field_name in bool_fields:
        if lowered in {"1", "true", "yes", "on", "y"}:
            return True
        if lowered in {"0", "false", "no", "off", "n"}:
            return False
        raise ValueError(f"{field_name} 需要布林值（true/false），收到 {raw!r}")
    if field_name == "concurrency":
        return int(raw)
    if lowered in {"none", "null", ""} and field_name in {
        "cookies_file", "cookies_from_browser", "proxy", "rate_limit",
        "impersonate",
    }:
        return None
    return raw
