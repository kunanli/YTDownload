"""微信視頻號：用瀏覽器自動化取得影片位址。

微信視頻號的分享頁只是一層 JS 外殼，影片位址要等頁面自己去換才拿得到，
所以 yt-dlp 那套「解析網址」的做法在這裡行不通。

這裡改成開一個真正的瀏覽器把頁面載入，攔截**頁面自己發出的**請求來取得影片
位址。好處是不必安裝根憑證、也不必代理整台電腦的流量——瀏覽器本來就看得到
自己的請求。代價是要有人掃碼登入一次。

本模組只放不需要瀏覽器的純邏輯（判斷網址、挑最佳來源、驗證檔案），
實際開瀏覽器的部分在 ``browser.py``，方便測試。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# 分享短連結會轉址到 channels.weixin.qq.com。
WECHAT_PAGE_HOSTS = (
    "weixin.qq.com",
    "channels.weixin.qq.com",
    "channels.weixin.qq.com.cn",
)

# 影片實際放在騰訊的 CDN 上，網域跟頁面不同。
WECHAT_MEDIA_HOSTS = (
    "finder.video.qq.com",
    "wxapp.tc.qq.com",
    "findervideo.tc.qq.com",
    "vweixinthumb.tc.qq.com",
)

_MEDIA_EXT_RE = re.compile(r"\.(mp4|m4v|mov|flv|m3u8|ts)(\?|$)", re.IGNORECASE)
_MEDIA_TYPE_RE = re.compile(r"^(video|application/(x-mpegurl|vnd\.apple\.mpegurl|octet-stream))",
                            re.IGNORECASE)

# 常見容器的檔頭，用來判斷抓到的是不是能播的影片。
_VIDEO_SIGNATURES = (
    (4, b"ftyp"),   # MP4／MOV：前 4 bytes 是長度，接著 ftyp
    (0, b"FLV"),
    (0, b"\x1aE\xdf\xa3"),  # Matroska / WebM
    (0, b"#EXTM3U"),        # HLS 播放清單
)


@dataclass
class MediaCandidate:
    """瀏覽器載入頁面時看到的一個可能的影片來源。"""

    url: str
    content_type: str = ""
    size: int = 0
    from_media_host: bool = False

    @property
    def is_playlist(self) -> bool:
        return ".m3u8" in self.url.lower()


@dataclass
class CaptureResult:
    """一次擷取的結果。"""

    url: str = ""
    title: str = ""
    author: str = ""
    candidates: list[MediaCandidate] = field(default_factory=list)
    cookies: dict = field(default_factory=dict)
    needs_login: bool = False

    @property
    def best(self) -> MediaCandidate | None:
        return pick_best_media(self.candidates)


def is_wechat_url(url: str) -> bool:
    """判斷是不是微信視頻號的網址。"""
    lowered = (url or "").lower()
    if not lowered.startswith(("http://", "https://")):
        return False
    host = lowered.split("//", 1)[-1].split("/", 1)[0].split(":")[0]
    if host in WECHAT_PAGE_HOSTS or host.endswith(".weixin.qq.com"):
        # 只有 /sph/ 短連結與視頻號頁面算數，公眾號文章不算
        return "/sph/" in lowered or "channels." in host or "finder" in lowered
    return False


def looks_like_media(url: str, content_type: str = "") -> bool:
    """判斷一個請求是不是影片本體。"""
    lowered = (url or "").lower()
    if not lowered.startswith(("http://", "https://")):
        return False
    if _MEDIA_EXT_RE.search(lowered):
        return True
    if content_type and _MEDIA_TYPE_RE.match(content_type.strip()):
        return True
    host = lowered.split("//", 1)[-1].split("/", 1)[0].split(":")[0]
    return any(host.endswith(h) for h in WECHAT_MEDIA_HOSTS)


def pick_best_media(candidates: list[MediaCandidate]) -> MediaCandidate | None:
    """從擷取到的來源中挑最可能是「完整影片」的那一個。

    優先序：騰訊影片 CDN > 檔案大 > 直接的 mp4（而非 m3u8 分段清單）。
    縮圖和預覽圖通常很小，會自然排到後面。
    """
    usable = [c for c in candidates if c.url]
    if not usable:
        return None
    return max(usable, key=lambda c: (c.from_media_host, c.size, not c.is_playlist))


def looks_like_playable_video(head: bytes) -> bool:
    """檢查檔案開頭是不是已知的影片容器。

    微信客戶端的串流是加密的（前 128 KB 被 XOR 過）。如果瀏覽器這條路拿到的
    也是加密內容，檔頭就不會是 ftyp，這時要明確告訴使用者，而不是留一個
    打不開的檔案。
    """
    if not head or len(head) < 8:
        return False
    return any(head[offset:offset + len(sig)] == sig for offset, sig in _VIDEO_SIGNATURES)


def suggest_filename(title: str, author: str) -> str:
    """依標題與作者組出檔名（不含副檔名）。"""
    from .utils import sanitize_filename

    title = (title or "").strip()
    author = (author or "").strip()
    if author and title:
        stem = f"{author} - {title}"
    else:
        stem = title or author or "wechat-video"
    return sanitize_filename(stem)


ENCRYPTED_HINT = """抓到的檔案不是可播放的影片，開頭不是已知的容器格式。

微信視頻號的串流有加密版本（前 128 KB 被處理過）。如果你拿到的是這種檔案，
本工具無法解密——請改用 wx_video_download，它會攔截客戶端流量並解密。
詳見 README 的「微信視頻號」章節。"""

PLAYWRIGHT_HINT = """微信視頻號需要 Playwright 才能運作（要開一個真正的瀏覽器）。

安裝：
  pip install playwright
  playwright install chromium

裝好之後再跑一次同樣的指令。"""


def download_media(candidate: "MediaCandidate", target, *, cookies: dict | None = None,
                   referer: str = "", progress=None) -> int:
    """把攔到的影片下載到 ``target``，回傳寫入的位元組數。

    刻意不經過 yt-dlp：這裡拿到的已經是最終的檔案位址，直接串流寫檔即可，
    也才能帶上頁面的 cookies 與 Referer（少了它們 CDN 會回 403）。
    """
    import urllib.request

    headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"),
        "Referer": referer or "https://channels.weixin.qq.com/",
        "Accept": "*/*",
    }
    if cookies:
        headers["Cookie"] = "; ".join(f"{k}={v}" for k, v in cookies.items())

    request = urllib.request.Request(candidate.url, headers=headers)
    written = 0
    with urllib.request.urlopen(request, timeout=60) as response:
        total = int(response.headers.get("content-length") or candidate.size or 0)
        with open(target, "wb") as handle:
            while True:
                chunk = response.read(256 * 1024)
                if not chunk:
                    break
                handle.write(chunk)
                written += len(chunk)
                if progress:
                    progress(written, total)
    return written
