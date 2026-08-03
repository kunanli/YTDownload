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
    "findervideo.tc.qq.com",
    "wxapp.tc.qq.com",
)

# 同樣在騰訊 CDN 上，但放的是縮圖／封面，不是影片。
# （vweixinthumb 的 thumb 就是縮圖——曾誤列進上面那組，導致抓到 47 KB 的封面。）
WECHAT_THUMB_HOSTS = (
    "vweixinthumb.tc.qq.com",
    "wxapp.tc.qq.com/thumb",
)

# 視頻號的影片至少都有幾百 KB；比這小的幾乎一定是封面或探測請求。
MIN_VIDEO_BYTES = 300 * 1024

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

    @property
    def is_thumbnail(self) -> bool:
        """封面／縮圖：主機名稱帶 thumb，或宣告成圖片。"""
        lowered = self.url.lower()
        if any(marker in lowered for marker in WECHAT_THUMB_HOSTS):
            return True
        return self.content_type.lower().startswith("image/")

    @property
    def is_big_enough(self) -> bool:
        """大小看起來像真的影片。0 代表伺服器沒給長度，不當作否定證據。"""
        return self.size == 0 or self.size >= MIN_VIDEO_BYTES

    def describe(self) -> str:
        from .utils import human_size

        marks = []
        if self.from_media_host:
            marks.append("CDN")
        if self.is_thumbnail:
            marks.append("縮圖")
        if self.is_playlist:
            marks.append("m3u8")
        tag = f"[{'/'.join(marks)}] " if marks else ""
        size = human_size(self.size) if self.size else "未知大小"
        return f"{tag}{size}  {self.content_type or '?'}  {self.url[:110]}"


@dataclass
class CaptureResult:
    """一次擷取的結果。"""

    url: str = ""
    title: str = ""
    author: str = ""
    candidates: list[MediaCandidate] = field(default_factory=list)
    # 頁面發出的所有請求，抓不到影片時用來診斷。
    observed: list[MediaCandidate] = field(default_factory=list)
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

    先排除封面／縮圖（曾經因此抓到 47 KB 的圖片當影片），再依
    「大小像影片 > 騰訊影片 CDN > 檔案大 > 直接 mp4」排序。
    """
    usable = [c for c in candidates if c.url and not c.is_thumbnail]
    if not usable:
        return None
    # 大小夠像影片的優先；全都太小時仍回傳最大的那個，讓後續的容器檢查去擋。
    return max(usable, key=lambda c: (c.is_big_enough, c.from_media_host,
                                      c.size, not c.is_playlist))


def has_probable_video(candidates: list[MediaCandidate]) -> bool:
    """有沒有看起來真的是影片的候選——用來決定可以停止等待了。

    絕不能只看「來自影片 CDN」：封面圖也放在 finder.video.qq.com 上，
    一載入就會誤判成抓到影片，瀏覽器隨即關閉，使用者連掃碼的時間都沒有。
    """
    return any(
        c.url and not c.is_thumbnail and c.size >= MIN_VIDEO_BYTES
        for c in candidates
    )


# 視頻號頁面用這支 API 取得影片資訊，回應裡就含影片位址。
FEED_API_MARKERS = ("get_feed_info", "finder/feed", "get_object_detail")

FEED_API_URL = "https://channels.weixin.qq.com/finder-preview/api/feed/get_feed_info"
SPH_PAGE_URL = "https://channels.weixin.qq.com/finder-preview/pages/sph?id={value}"
FEED_PAGE_URL = "https://channels.weixin.qq.com/finder-preview/pages/feed?eid={value}"

# 頁面的 JS 從這幾個欄位取影片位址（h265 優先，再 h264，最後才是頂層 videoUrl）。
_VIDEO_INFO_KEYS = ("h265VideoInfo", "h264VideoInfo")

_SPH_RE = re.compile(r"/sph/([A-Za-z0-9]+)")
_EID_RE = re.compile(r"[?&]eid=([^&#]+)")


def parse_wechat_link(url: str) -> tuple[str, str] | None:
    """看出網址是哪一種視頻號連結。

    回傳 ``("sph", 短碼)`` 或 ``("eid", 匯出碼)``；認不出來就回 None。
    兩種要問 API 的方式不同，也決定了網頁端到底放不放行播放。
    """
    import urllib.parse

    text = url or ""
    if match := _EID_RE.search(text):
        return "eid", urllib.parse.unquote(match.group(1))
    if match := _SPH_RE.search(text):
        return "sph", match.group(1)
    return None


def feed_request(kind: str, value: str) -> tuple[str, dict, bytes]:
    """組出 get_feed_info 的請求（網址、標頭、內容）。

    這支 API 不需要登入也不需要簽章，用一般的 HTTP 就問得到——所以查「這支
    影片到底拿不拿得到」不必先開瀏覽器等兩分鐘。
    """
    import json
    import urllib.parse

    page = (SPH_PAGE_URL if kind == "sph" else FEED_PAGE_URL).format(
        value=urllib.parse.quote(value, safe="/")
    )
    body = {"baseReq": {"generalToken": ""}}
    body["shortUri" if kind == "sph" else "exportId"] = value
    headers = {
        "content-type": "application/json",
        "origin": "https://channels.weixin.qq.com",
        "referer": page,
        "user-agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"),
    }
    query = urllib.parse.urlencode({"_pageUrl": page})
    return f"{FEED_API_URL}?{query}", headers, json.dumps(body).encode()


@dataclass
class FeedInfo:
    """get_feed_info 回應裡我們在意的部分。"""

    title: str = ""
    author: str = ""
    cover: str = ""
    video_urls: list[str] = field(default_factory=list)
    error_type: int = 0
    error_title: str = ""
    export_id: str = ""

    @property
    def playable(self) -> bool:
        return bool(self.video_urls)


def parse_feed_info(payload: dict) -> FeedInfo:
    """把 API 回應整理成 FeedInfo。

    影片位址可能在 h265VideoInfo／h264VideoInfo 底下，也可能直接放在
    feedInfo.videoUrl——頁面的播放器三個都會看，我們也一樣。
    """
    data = (payload or {}).get("data") or {}
    feed = data.get("feedInfo") or {}
    author = data.get("authorInfo") or {}
    error = data.get("errMsg") or {}
    scene = data.get("sceneInfo") or {}

    urls: list[str] = []
    for key in _VIDEO_INFO_KEYS:
        candidate = (feed.get(key) or {}).get("videoUrl")
        if candidate:
            urls.append(candidate)
    if feed.get("videoUrl"):
        urls.append(feed["videoUrl"])

    return FeedInfo(
        title=(feed.get("description") or "").strip().split("\n")[0],
        author=(author.get("nickname") or "").strip(),
        cover=feed.get("coverUrl") or "",
        video_urls=list(dict.fromkeys(urls)),
        error_type=int(error.get("type") or 0),
        error_title=(error.get("title") or "").strip(),
        export_id=scene.get("dynamicExportId") or "",
    )


def fetch_feed_info(url: str, *, timeout: int = 20) -> FeedInfo | None:
    """直接問 API 這支影片的資訊。認不出網址或問不到就回 None。"""
    import json
    import urllib.request

    link = parse_wechat_link(url)
    if link is None:
        return None
    api, headers, body = feed_request(*link)
    request = urllib.request.Request(api, data=body, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8", "replace"))
    except Exception:
        return None
    return parse_feed_info(payload)


# 同一支 API 有時給影片位址、有時只給封面。實測：同樣的請求內容，從不同的
# 出口 IP 問，微信回的 sceneInfo.entryScene 就不一樣（64 沒有影片、51 有），
# 而 entryScene 是伺服器自己決定的，改請求內容改不動它。
WEB_BLOCKED_HINT = """微信這次沒有把影片位址送回來——只給了標題、作者與封面。

同一支影片換個網路環境問就拿得到，所以這不是「這支影片不能下載」，
比較像是微信按來源決定要不要給。可以試試：

  1. 換個網路（手機熱點、關掉 VPN／Proxy）再跑一次
  2. 加 --resolver 用線上解析服務代查（會把網址送給第三方，見下）
  3. 加 --browser 讓瀏覽器實際載入頁面試一次

真的都不行，就只剩攔截電腦版微信客戶端流量的工具
（wechatvideodownload / wx_channels_download），詳見 README 的「微信視頻號」章節。"""

# ltaoo/wx_channels_download 公開的線上解析服務。它從自己的出口去問同一支
# get_feed_info，因此常常拿得到我們這邊拿不到的影片位址。
DEFAULT_RESOLVER = "https://sph.litao.workers.dev/api/fetch_video_profile"

RESOLVER_NOTICE = """線上解析會把這個網址送給第三方服務：
  {service}

那是 ltaoo/wx_channels_download 提供的公開服務，不屬於本工具，也不受我們控制。
送出去的是影片網址本身；不會送出你的 cookies 或登入資訊。"""


def resolve_via_service(url: str, *, service: str = DEFAULT_RESOLVER,
                        timeout: int = 30) -> "FeedInfo | None":
    """請線上服務代查影片位址，回應形狀跟微信原本的 API 一樣。

    刻意做成要明講、要同意才走：這一步會把使用者手上的網址交給第三方。
    """
    import json
    import urllib.request

    request = urllib.request.Request(
        service, data=json.dumps({"url": url}).encode(),
        headers={"content-type": "application/json",
                 "user-agent": "ytmusic (+https://github.com/kunanli/YTDownload)"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8", "replace"))
    except Exception:
        return None
    return parse_feed_info(payload)


def is_feed_api(url: str) -> bool:
    lowered = (url or "").lower()
    return any(marker in lowered for marker in FEED_API_MARKERS)


def extract_video_urls(data) -> list[str]:
    """從 API 回應裡遞迴找出影片位址。

    比起猜「頁面下載了什麼」，直接讀 API 給的答案可靠得多——影片還沒開始播放
    時也拿得到。
    """
    found: list[str] = []

    def walk(node) -> None:
        if isinstance(node, dict):
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
        elif isinstance(node, str) and node.startswith(("http://", "https://")):
            host = node.split("//", 1)[-1].split("/", 1)[0].split(":")[0]
            if any(host.endswith(h) for h in WECHAT_MEDIA_HOSTS) or ".mp4" in node.lower():
                if not any(marker in node.lower() for marker in WECHAT_THUMB_HOSTS):
                    found.append(node)

    walk(data)
    return list(dict.fromkeys(found))  # 去重且保留順序


def looks_like_playable_video(head: bytes) -> bool:
    """檢查檔案開頭是不是已知的影片容器。

    微信客戶端的串流是加密的（前 128 KB 被 XOR 過）。如果瀏覽器這條路拿到的
    也是加密內容，檔頭就不會是 ftyp，這時要明確告訴使用者，而不是留一個
    打不開的檔案。
    """
    if not head or len(head) < 8:
        return False
    return any(head[offset:offset + len(sig)] == sig for offset, sig in _VIDEO_SIGNATURES)


# 視頻號沒有「標題」欄位，只有整段貼文說明——直接拿來當檔名會長到看不完。
_HASHTAG_RE = re.compile(r"#\S+")
_TITLE_MAX = 40


def trim_title(text: str) -> str:
    """把整段貼文說明收成像標題的長度。

    先砍掉結尾那串 hashtag（`#UE #虛幻引擎 #黑科技…` 佔掉半個檔名卻沒有資訊），
    再從標點處截斷，實在沒有標點才硬切。
    """
    text = _HASHTAG_RE.sub(" ", (text or "").split("\n")[0])
    text = " ".join(text.split()).strip(" ，,。.、|-")
    if len(text) <= _TITLE_MAX:
        return text
    head = text[:_TITLE_MAX]
    for mark in ("，", "。", "、", ",", ".", " "):
        cut = head.rfind(mark)
        if cut >= _TITLE_MAX // 2:
            return head[:cut].strip()
    return head.strip()


def suggest_filename(title: str, author: str) -> str:
    """依標題與作者組出檔名（不含副檔名）。"""
    from .utils import sanitize_filename

    title = trim_title(title)
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

# 一律用 `python -m playwright`：pip 裝的 playwright.exe 在 Windows 上多半
# 不在 PATH，直接打 `playwright` 會得到 CommandNotFoundException。
PLAYWRIGHT_HINT = """微信視頻號需要 Playwright 才能運作（要開一個真正的瀏覽器）。

手動安裝：
  python -m pip install playwright
  python -m playwright install chromium

注意是 `python -m playwright`，不是 `playwright`——pip 裝的執行檔在 Windows
上通常不在 PATH，直接打會說「不是內部或外部命令」。"""

# Playwright 找不到瀏覽器時的錯誤訊息特徵。
_MISSING_BROWSER_MARKERS = (
    "executable doesn't exist",
    "please run the following command to download new browsers",
    "playwright install",
)


def is_missing_browser_error(exc: BaseException) -> bool:
    """判斷失敗是不是「套件有裝但瀏覽器沒下載」——這種可以自動補。"""
    message = str(exc).lower()
    return any(marker in message for marker in _MISSING_BROWSER_MARKERS)


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
