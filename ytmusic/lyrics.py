"""字幕轉歌詞：把 YouTube 的 SRT／VTT 字幕轉成 LRC，並寫進音檔標籤。

這裡全部是純文字處理，不碰網路，方便測試。抓字幕檔的是 yt-dlp。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# 00:01:23,456 / 00:01:23.456 都要吃得下；小時可省略。
_TIME_RE = re.compile(r"(?:(\d+):)?(\d{1,2}):(\d{2})[.,](\d{1,3})")
_CUE_RE = re.compile(r"(.+?)\s*-->\s*(\S+)")

# VTT 內嵌的樣式標記，例如 <00:00:01.000><c>字</c>
_TAG_RE = re.compile(r"<[^>]+>")

SUBTITLE_SUFFIXES = (".srt", ".vtt")

# 使用者可以打中文，也可以直接打語言代碼。
LANGUAGE_ALIASES = {
    "繁中": "zh-TW", "繁體": "zh-TW", "正體": "zh-TW", "中文": "zh-TW",
    "簡中": "zh-Hans", "簡體": "zh-Hans",
    "英": "en", "英文": "en",
    "日": "ja", "日文": "ja",
    "韓": "ko", "韓文": "ko",
    "西": "es", "西班牙": "es", "西班牙文": "es",
}

# 預設順序＝挑歌詞時的偏好順序。
DEFAULT_LANGUAGES = ("zh-TW", "zh-Hans", "en", "ja", "ko", "es")


def normalise_languages(spec: str) -> list[str]:
    """把 "繁中,英" 或 "zh-TW,en" 轉成 yt-dlp 用的語言代碼清單。"""
    out: list[str] = []
    for part in (spec or "").replace("，", ",").split(","):
        token = part.strip()
        if not token:
            continue
        code = LANGUAGE_ALIASES.get(token, token)
        if code not in out:
            out.append(code)
    return out


def language_of(path: Path) -> str:
    """從 ``歌名.zh-TW.srt`` 這種檔名取出語言代碼。"""
    parts = path.name.rsplit(".", 2)
    return parts[-2] if len(parts) == 3 else ""


@dataclass(frozen=True)
class Cue:
    start: float  # 秒
    text: str


def parse_timestamp(text: str) -> float | None:
    match = _TIME_RE.search(text)
    if not match:
        return None
    hours, minutes, seconds, fraction = match.groups()
    return (
        int(hours or 0) * 3600
        + int(minutes) * 60
        + int(seconds)
        + int(fraction.ljust(3, "0")) / 1000
    )


def parse_subtitles(text: str) -> list[Cue]:
    """解析 SRT 或 VTT，回傳依時間排序、去除重複的字幕。

    自動字幕會為了做「逐字浮現」效果而重複整行，因此這裡會把連續相同的內容
    合併，只保留第一次出現的時間。
    """
    cues: list[Cue] = []
    block: list[str] = []
    start: float | None = None

    def flush() -> None:
        nonlocal start, block
        if start is not None:
            body = " ".join(line.strip() for line in block if line.strip())
            body = _TAG_RE.sub("", body).strip()
            if body:
                cues.append(Cue(start, body))
        start, block = None, []

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            flush()
            continue
        if "-->" in line:
            flush()
            match = _CUE_RE.match(line)
            start = parse_timestamp(match.group(1)) if match else None
            continue
        if start is None:
            continue  # 序號、WEBVTT 標頭、NOTE 等等
        block.append(line)
    flush()

    cues.sort(key=lambda c: c.start)
    return _dedupe(cues)


def _dedupe(cues: list[Cue]) -> list[Cue]:
    out: list[Cue] = []
    for cue in cues:
        if out and cue.text == out[-1].text:
            continue  # 自動字幕的滾動重複
        out.append(cue)
    return out


def to_lrc(cues: list[Cue], *, title: str = "", artist: str = "",
           album: str = "") -> str:
    """輸出標準 LRC（含時間軸），可被多數播放器讀取。"""
    lines = []
    for tag, value in (("ti", title), ("ar", artist), ("al", album)):
        if value:
            lines.append(f"[{tag}:{value}]")
    if lines:
        lines.append("")
    for cue in cues:
        minutes, seconds = divmod(cue.start, 60)
        lines.append(f"[{int(minutes):02d}:{seconds:05.2f}]{cue.text}")
    return "\n".join(lines) + "\n"


def to_plain(cues: list[Cue]) -> str:
    """輸出純文字歌詞（沒有時間軸），給不支援 LRC 的播放器。"""
    return "\n".join(cue.text for cue in cues)


def find_subtitle_files(media_path: Path,
                        preferred: list[str] | None = None) -> list[Path]:
    """找出 yt-dlp 放在音檔旁邊的字幕檔（檔名為 <同名>.<語言>.srt）。

    依 ``preferred`` 的語言順序排序，讓呼叫端取第一個就是最想要的語言；
    照檔名排序會讓 en 永遠贏過 zh-TW。
    """
    parent = media_path.parent
    if not parent.is_dir():
        return []
    stem = media_path.stem
    found = [
        item for item in parent.iterdir()
        if item.is_file()
        and item.suffix.lower() in SUBTITLE_SUFFIXES
        and item.name.startswith(stem)
    ]

    order = [lang.lower() for lang in (preferred or DEFAULT_LANGUAGES)]

    def rank(path: Path) -> tuple[int, str]:
        lang = language_of(path).lower()
        for index, wanted in enumerate(order):
            # zh-TW 也該對得上 yt-dlp 產生的 zh-Hant-TW 這類代碼
            if lang == wanted or lang.startswith(wanted) or wanted.startswith(lang):
                return index, path.name
        return len(order), path.name

    return sorted(found, key=rank)


def read_subtitle(path: Path) -> list[Cue]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    return parse_subtitles(text)


def embed_lyrics(media_path: Path, plain: str, *, language: str = "und") -> bool:
    """把純文字歌詞寫進音檔標籤（MP3 用 USLT、MP4 用 ©lyr）。"""
    if not plain.strip():
        return False
    suffix = media_path.suffix.lower()
    try:
        if suffix == ".mp3":
            from mutagen.id3 import USLT
            from mutagen.mp3 import MP3

            audio = MP3(media_path)
            if audio.tags is None:
                audio.add_tags()
            audio.tags.delall("USLT")
            audio.tags.add(USLT(encoding=3, lang=language[:3], desc="", text=plain))
            audio.save(v2_version=3)
            return True
        if suffix in {".m4a", ".mp4"}:
            from mutagen.mp4 import MP4

            audio = MP4(media_path)
            if audio.tags is None:
                audio.add_tags()
            audio.tags["\xa9lyr"] = [plain]
            audio.save()
            return True
        if suffix in {".flac", ".opus", ".ogg"}:
            from mutagen import File as MutagenFile

            audio = MutagenFile(media_path)
            if audio is None or audio.tags is None:
                return False
            audio["lyrics"] = [plain]
            audio.save()
            return True
    except Exception:
        return False
    return False
