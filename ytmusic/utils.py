"""字串清理、檔名處理與格式化的小工具。"""

from __future__ import annotations

import re
import shutil
import unicodedata

# 影片標題常見的宣傳雜訊，移除後才拿來當歌名。
_NOISE_PATTERNS = [
    r"\(\s*[^()]*\b(?:official|lyric|lyrics|audio|visuali[sz]er|mv|m/v|hd|hq|4k|8k|"
    r"full\s*version|explicit|clean|remaster(?:ed)?)\b[^()]*\)",
    r"\[\s*[^\[\]]*\b(?:official|lyric|lyrics|audio|visuali[sz]er|mv|m/v|hd|hq|4k|8k|"
    r"full\s*version|explicit|clean|remaster(?:ed)?)\b[^\[\]]*\]",
    r"【[^【】]*(?:MV|M/V|official|Official|OFFICIAL|官方|完整版|高音質|音樂錄影帶)[^【】]*】",
    r"「\s*(?:official|官方)[^「」]*」",
    r"\|\s*[^|]*\b(?:official|lyric|lyrics|audio)\b[^|]*$",
    r"[-–—]\s*(?:official\s*)?(?:music\s*)?(?:video|audio|lyric\s*video)\s*$",
]
_NOISE_RE = [re.compile(p, re.IGNORECASE) for p in _NOISE_PATTERNS]

# "Artist - Title" 的分隔符，含各種破折號與全形冒號。
_SPLIT_RE = re.compile(r"\s+[-–—]\s+|\s*[｜|]\s*")

# YouTube Music 會把官方頻道標成 "<Artist> - Topic"。
_TOPIC_RE = re.compile(r"\s*-\s*Topic\s*$", re.IGNORECASE)

_ILLEGAL_FS_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_WINDOWS_RESERVED = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def clean_title(title: str) -> str:
    """移除標題中的 (Official Video)、[MV]、【官方】等宣傳字樣。"""
    if not title:
        return ""
    out = title
    for pattern in _NOISE_RE:
        out = pattern.sub(" ", out)
    out = re.sub(r"\s+", " ", out)
    # 清掉清理後殘留在頭尾的分隔符與空括號。
    out = re.sub(r"[\(\[【]\s*[\)\]】]", " ", out)
    out = out.strip(" -–—|｜·、,")
    return out.strip() or title.strip()


def strip_topic(name: str) -> str:
    """把 YouTube Music 自動產生的 "Artist - Topic" 還原成 "Artist"。"""
    return _TOPIC_RE.sub("", name or "").strip()


def split_artist_title(title: str) -> tuple[str | None, str]:
    """從 "Artist - Song" 形式的標題拆出演出者與歌名。

    拆不出來時回傳 ``(None, 原標題)``，讓呼叫端自行決定退路。
    """
    cleaned = clean_title(title)
    if not cleaned:
        return None, ""

    parts = [p.strip() for p in _SPLIT_RE.split(cleaned) if p.strip()]
    if len(parts) >= 2:
        artist, song = parts[0], " - ".join(parts[1:])
        # 純數字前綴（"01 - Song"）是曲序不是演出者；過長的前段多半也是誤判。
        if song and len(artist) <= 60 and not artist.isdigit():
            return artist, song

    # 「歌名」括在全形引號裡：Artist「Song」
    quoted = re.match(r"^(.{1,60}?)\s*[「『《]([^」』》]+)[」』》]\s*$", cleaned)
    if quoted:
        return quoted.group(1).strip(), quoted.group(2).strip()

    return None, cleaned


def sanitize_filename(name: str, max_length: int = 120, replacement: str = "_") -> str:
    """把任意字串轉成各平台都能安全使用的檔名片段。"""
    if not name:
        return "untitled"
    out = unicodedata.normalize("NFC", name)
    out = _ILLEGAL_FS_CHARS.sub(replacement, out)
    out = re.sub(r"\s+", " ", out).strip(" .")
    if not out:
        return "untitled"
    if out.split(".")[0].upper() in _WINDOWS_RESERVED:
        out = f"{replacement}{out}"
    if len(out) > max_length:
        out = out[:max_length].rstrip(" .")
    return out or "untitled"


def human_size(num_bytes: float | None) -> str:
    """把位元組數格式化成 1.2 MiB 這種易讀寫法。"""
    if not num_bytes or num_bytes < 0:
        return "--"
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    size = float(num_bytes)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TiB"


def human_time(seconds: float | None) -> str:
    """把秒數格式化成 mm:ss 或 h:mm:ss。"""
    if seconds is None or seconds < 0:
        return "--:--"
    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def truncate(text: str, width: int) -> str:
    """把過長的文字截斷成固定寬度，尾端補上省略號。"""
    if width <= 1 or len(text) <= width:
        return text
    return text[: width - 1] + "…"


def find_ffmpeg() -> str | None:
    """回傳 ffmpeg 可執行檔路徑，找不到則回傳 None。"""
    return shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")


FFMPEG_HINT = """找不到 ffmpeg，音訊轉檔需要它。安裝方式：
  macOS         brew install ffmpeg
  Ubuntu/Debian sudo apt install ffmpeg
  Windows       winget install Gyan.FFmpeg
或改用 --no-convert 直接保留 YouTube 原始音訊（通常是 m4a／webm，不轉檔）。"""
