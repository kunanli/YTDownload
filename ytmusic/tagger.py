"""從 yt-dlp 的 info dict 推導歌曲中繼資料，並寫入音檔標籤與封面。"""

from __future__ import annotations

import io
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from .utils import clean_title, split_artist_title, strip_topic

_USER_AGENT = "Mozilla/5.0 (compatible; ytmusic/0.1)"
_COVER_TIMEOUT = 20


@dataclass
class TrackMeta:
    """要寫進音檔的欄位。"""

    title: str = ""
    artist: str = ""
    album: str = ""
    album_artist: str = ""
    date: str = ""
    genre: str = ""
    track_number: int | None = None
    track_total: int | None = None
    comment: str = ""

    def as_display(self) -> str:
        return f"{self.artist} - {self.title}" if self.artist else self.title


# --------------------------------------------------------------------------
# 中繼資料推導
# --------------------------------------------------------------------------

def build_metadata(info: dict, *, playlist_title: str | None = None,
                   playlist_index: int | None = None,
                   playlist_count: int | None = None) -> TrackMeta:
    """把 yt-dlp 的 info dict 轉成 TrackMeta。

    YouTube Music 的曲目自帶 ``track`` / ``artist`` / ``album`` 欄位，優先採用；
    一般影片則退而從標題解析 "Artist - Song"。
    """
    raw_title = info.get("title") or ""
    uploader = strip_topic(info.get("uploader") or info.get("channel") or "")

    track = (info.get("track") or "").strip()
    artist = (info.get("artist") or info.get("creator") or "").strip()

    if not track or not artist:
        parsed_artist, parsed_title = split_artist_title(raw_title)
        track = track or parsed_title or clean_title(raw_title) or raw_title
        artist = artist or parsed_artist or uploader

    # yt-dlp 的 artist 可能是 "A, B" 或 "A、B"，保留原樣即可，多數播放器看得懂。
    album = (info.get("album") or "").strip()
    if not album and playlist_title:
        album = playlist_title.strip()

    date = ""
    if info.get("release_year"):
        date = str(info["release_year"])
    elif info.get("release_date"):
        date = str(info["release_date"])[:4]
    elif info.get("upload_date"):
        date = str(info["upload_date"])[:4]

    album_artist = (info.get("album_artist") or "").strip() or artist

    return TrackMeta(
        title=track.strip(),
        artist=artist.strip(),
        album=album,
        album_artist=album_artist,
        date=date,
        genre=(info.get("genre") or "").strip(),
        track_number=playlist_index,
        track_total=playlist_count,
        comment=info.get("webpage_url") or info.get("original_url") or "",
    )


# --------------------------------------------------------------------------
# 封面
# --------------------------------------------------------------------------

def pick_thumbnail_url(info: dict) -> str | None:
    """挑一張解析度最高的 JPEG 縮圖。

    刻意避開 webp：部分播放器不認 webp 封面，而 YouTube 對每支影片都有 jpg。
    """
    candidates = []
    for thumb in info.get("thumbnails") or []:
        url = thumb.get("url") or ""
        if not url:
            continue
        base = url.split("?")[0].lower()
        if not (base.endswith(".jpg") or base.endswith(".jpeg")):
            continue
        area = (thumb.get("width") or 0) * (thumb.get("height") or 0)
        candidates.append((area, thumb.get("preference") or 0, url))

    if candidates:
        candidates.sort(key=lambda c: (c[0], c[1]))
        return candidates[-1][2]

    url = info.get("thumbnail") or ""
    if url:
        # 非 YouTube 站台（Bilibili 等）的縮圖常是 webp／無副檔名，照收即可，
        # 交給 mutagen 依實際位元組判斷 MIME。
        return url

    # 只有 YouTube 能從影片 ID 推出縮圖網址，別的站台硬湊會得到死連結。
    video_id = info.get("id")
    if video_id and _is_youtube(info):
        return f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"
    return None


def _is_youtube(info: dict) -> bool:
    extractor = str(info.get("extractor_key") or info.get("extractor") or "").lower()
    return extractor.startswith("youtube")


# 真正的專輯封面不可能這麼小；比這小的多半是佔位圖或追蹤像素。
MIN_COVER_BYTES = 2048
MIN_COVER_PIXELS = 100


def fetch_cover(url: str, *, square: bool = True) -> bytes | None:
    """抓取封面圖；``square`` 為真且裝了 Pillow 時會裁成正方形。

    有些站台在影片沒有縮圖時會回一張 1×1 的透明佔位圖（例如 Bilibili 的
    transparent.png），這種東西不該被寫成專輯封面，所以會先驗證再回傳。
    """
    data = _http_get(url)
    if data is None and "maxresdefault" in url:
        # maxresdefault 不是每支影片都有，退回一定存在的 hqdefault。
        data = _http_get(url.replace("maxresdefault", "hqdefault"))
    if not data or not _looks_like_cover(data):
        return None
    if square:
        data = _crop_square(data) or data
    return data


def _looks_like_cover(data: bytes) -> bool:
    """擋掉佔位圖與破損檔案。"""
    if len(data) < MIN_COVER_BYTES:
        return False
    try:
        from PIL import Image  # type: ignore
    except ImportError:
        return True  # 沒有 Pillow 就只能靠檔案大小判斷
    try:
        with Image.open(io.BytesIO(data)) as image:
            width, height = image.size
    except Exception:
        return False
    return width >= MIN_COVER_PIXELS and height >= MIN_COVER_PIXELS


def _http_get(url: str) -> bytes | None:
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=_COVER_TIMEOUT) as response:
            if response.status != 200:
                return None
            return response.read()
    except (urllib.error.URLError, OSError, ValueError):
        return None


def _crop_square(data: bytes) -> bytes | None:
    """把 16:9 縮圖置中裁成正方形；沒有 Pillow 就原樣放行。"""
    try:
        from PIL import Image  # type: ignore
    except ImportError:
        return None
    try:
        with Image.open(io.BytesIO(data)) as image:
            image = image.convert("RGB")
            width, height = image.size
            if width == height:
                return None
            side = min(width, height)
            left, top = (width - side) // 2, (height - side) // 2
            cropped = image.crop((left, top, left + side, top + side))
            buffer = io.BytesIO()
            cropped.save(buffer, format="JPEG", quality=90)
            return buffer.getvalue()
    except Exception:
        return None


# --------------------------------------------------------------------------
# 寫入標籤
# --------------------------------------------------------------------------

class TaggingError(RuntimeError):
    pass


def apply_tags(path: Path, meta: TrackMeta, cover: bytes | None = None) -> None:
    """依副檔名選擇對應的標籤格式寫入。

    未支援的容器（例如 wav）會直接跳過，不視為錯誤。
    """
    suffix = path.suffix.lower().lstrip(".")
    writer = {
        "mp3": _tag_mp3,
        "m4a": _tag_mp4,
        "mp4": _tag_mp4,
        "flac": _tag_flac,
        "opus": _tag_vorbis,
        "ogg": _tag_vorbis,
    }.get(suffix)
    if writer is None:
        return
    try:
        writer(path, meta, cover)
    except ImportError as exc:  # pragma: no cover - 缺套件時的路徑
        raise TaggingError(f"缺少 mutagen，無法寫入標籤：{exc}") from exc
    except Exception as exc:
        raise TaggingError(f"寫入標籤失敗：{exc}") from exc


def _tag_mp3(path: Path, meta: TrackMeta, cover: bytes | None) -> None:
    from mutagen.id3 import (
        APIC, COMM, ID3, TALB, TCON, TDRC, TIT2, TPE1, TPE2, TRCK,
    )
    from mutagen.mp3 import MP3

    audio = MP3(path)
    if audio.tags is None:
        audio.add_tags()
    tags: ID3 = audio.tags  # type: ignore[assignment]
    tags.delall("APIC")

    if meta.title:
        tags.setall("TIT2", [TIT2(encoding=3, text=meta.title)])
    if meta.artist:
        tags.setall("TPE1", [TPE1(encoding=3, text=meta.artist)])
    if meta.album:
        tags.setall("TALB", [TALB(encoding=3, text=meta.album)])
    if meta.album_artist:
        tags.setall("TPE2", [TPE2(encoding=3, text=meta.album_artist)])
    if meta.date:
        tags.setall("TDRC", [TDRC(encoding=3, text=meta.date)])
    if meta.genre:
        tags.setall("TCON", [TCON(encoding=3, text=meta.genre)])
    if meta.track_number:
        track = str(meta.track_number)
        if meta.track_total:
            track = f"{track}/{meta.track_total}"
        tags.setall("TRCK", [TRCK(encoding=3, text=track)])
    if meta.comment:
        tags.setall("COMM", [COMM(encoding=3, lang="eng", desc="", text=meta.comment)])
    if cover:
        tags.add(APIC(encoding=3, mime=_mime(cover), type=3, desc="Cover", data=cover))

    audio.save(v2_version=3)


def _tag_mp4(path: Path, meta: TrackMeta, cover: bytes | None) -> None:
    from mutagen.mp4 import MP4, MP4Cover

    audio = MP4(path)
    if audio.tags is None:
        audio.add_tags()
    tags = audio.tags
    assert tags is not None

    if meta.title:
        tags["\xa9nam"] = [meta.title]
    if meta.artist:
        tags["\xa9ART"] = [meta.artist]
    if meta.album:
        tags["\xa9alb"] = [meta.album]
    if meta.album_artist:
        tags["aART"] = [meta.album_artist]
    if meta.date:
        tags["\xa9day"] = [meta.date]
    if meta.genre:
        tags["\xa9gen"] = [meta.genre]
    if meta.track_number:
        tags["trkn"] = [(meta.track_number, meta.track_total or 0)]
    if meta.comment:
        tags["\xa9cmt"] = [meta.comment]
    if cover:
        fmt = MP4Cover.FORMAT_PNG if _mime(cover) == "image/png" else MP4Cover.FORMAT_JPEG
        tags["covr"] = [MP4Cover(cover, imageformat=fmt)]

    audio.save()


def _tag_flac(path: Path, meta: TrackMeta, cover: bytes | None) -> None:
    from mutagen.flac import FLAC, Picture

    audio = FLAC(path)
    _write_vorbis_fields(audio, meta)
    audio.clear_pictures()
    if cover:
        picture = Picture()
        picture.type = 3
        picture.mime = _mime(cover)
        picture.desc = "Cover"
        picture.data = cover
        audio.add_picture(picture)
    audio.save()


def _tag_vorbis(path: Path, meta: TrackMeta, cover: bytes | None) -> None:
    import base64

    from mutagen import File as MutagenFile
    from mutagen.flac import Picture

    audio = MutagenFile(path)
    if audio is None or not hasattr(audio, "tags") or audio.tags is None:
        raise TaggingError(f"無法讀取 {path.name} 的標籤區塊")
    _write_vorbis_fields(audio, meta)
    if cover:
        picture = Picture()
        picture.type = 3
        picture.mime = _mime(cover)
        picture.desc = "Cover"
        picture.data = cover
        audio["metadata_block_picture"] = [
            base64.b64encode(picture.write()).decode("ascii")
        ]
    audio.save()


def _write_vorbis_fields(audio, meta: TrackMeta) -> None:
    mapping = {
        "title": meta.title,
        "artist": meta.artist,
        "album": meta.album,
        "albumartist": meta.album_artist,
        "date": meta.date,
        "genre": meta.genre,
        "tracknumber": str(meta.track_number) if meta.track_number else "",
        "tracktotal": str(meta.track_total) if meta.track_total else "",
        "comment": meta.comment,
    }
    for key, value in mapping.items():
        if value:
            audio[key] = [value]


def _mime(data: bytes) -> str:
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    return "image/jpeg"
