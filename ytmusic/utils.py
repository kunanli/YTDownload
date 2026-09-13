"""字串清理、檔名處理與格式化的小工具。"""

from __future__ import annotations

import pathlib
import re
import shutil
import unicodedata
import urllib.parse

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

# 終端機控制碼：ESC 序列（顏色）加上其他控制字元。
_ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]|\x1b[@-Z\\-_]")
_CONTROL_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")


def strip_ansi(text: str) -> str:
    """去掉顏色碼與其他控制字元。

    yt-dlp 在支援顏色的終端機（Windows Terminal 就是）會把錯誤寫成
    ``\\x1b[0;31mERROR:\\x1b[0m …``。這些碼若跟著訊息一起被切割或印出，
    畫面會被吃掉一整段——使用者看到的就只剩空白。
    """
    return _CONTROL_RE.sub("", _ANSI_RE.sub("", text or ""))


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


def display_width(text: str) -> int:
    """字串在終端機上實際佔用的欄數。

    中日韓文字是雙倍寬，用 len() 計算會讓進度列遠超出畫面寬度而自動換行；
    一換行，重繪時「往上幾列」就對不上，畫面會殘留一堆重複的舊列。

    East Asian Width 為 A（ambiguous）的字元——包括 ✔✖ 和方塊繪圖字元——在
    中日韓字型下多半也是雙寬，這裡一律保守算 2：算多了只是列稍微短一點，
    算少了就會破版。
    """
    width = 0
    for char in text:
        if unicodedata.combining(char):
            continue  # 組合用附加符號不佔位
        width += 2 if unicodedata.east_asian_width(char) in ("W", "F", "A") else 1
    return width


def truncate(text: str, width: int) -> str:
    """把文字截斷到指定的「顯示欄寬」（非字元數），尾端補上省略號。"""
    if width <= 0:
        return ""
    if display_width(text) <= width:
        return text

    ellipsis = "…"
    ellipsis_width = display_width(ellipsis)
    if width <= ellipsis_width:
        return " " * width  # 連省略號都放不下，留空白避免破版

    budget = width - ellipsis_width
    kept: list[str] = []
    used = 0
    for char in text:
        char_width = display_width(char)
        if used + char_width > budget:
            break
        kept.append(char)
        used += char_width
    return "".join(kept) + ellipsis


def pad_display(text: str, width: int) -> str:
    """依顯示欄寬靠左對齊補空白（len() 對中日韓文字會補錯）。"""
    return text + " " * max(0, width - display_width(text))


# yt-dlp 的瀏覽器 cookies 規格：BROWSER[+KEYRING][:PROFILE][::CONTAINER]
_BROWSER_SPEC_RE = re.compile(
    r"""(?x)
    (?P<name>[^+:]+)
    (?:\s*\+\s*(?P<keyring>[^:]+))?
    (?:\s*:\s*(?!:)(?P<profile>.+?))?
    (?:\s*::\s*(?P<container>.+))?
    """
)


def parse_browser_spec(value: str) -> tuple[str, str | None, str | None, str | None]:
    """把 ``chrome:Profile 1`` 這類字串拆成 yt-dlp API 要的四元組。

    yt-dlp 只在自己的命令列裡解析這個格式，透過 Python API 傳入時必須先拆好，
    否則整串會被當成瀏覽器名稱。
    """
    match = _BROWSER_SPEC_RE.fullmatch(value.strip())
    if not match:
        raise ValueError(f"無法解析瀏覽器設定 {value!r}")
    name = match.group("name").strip().lower()
    if not name:
        raise ValueError(f"無法解析瀏覽器設定 {value!r}")

    def clean(group: str) -> str | None:
        raw = match.group(group)
        return raw.strip() or None if raw else None

    keyring = clean("keyring")
    return name, clean("profile"), keyring.upper() if keyring else None, clean("container")


_YOUTUBE_HOSTS = {
    "youtube.com", "www.youtube.com", "m.youtube.com",
    "music.youtube.com", "youtu.be", "www.youtu.be",
}


# yt-dlp 認定「這份 cookies 是登入狀態」的條件：要有 LOGIN_INFO，而且 SAPISID
# 三兄弟至少有一個（見 yt_dlp/extractor/youtube/_base.py 的 _has_auth_cookies）。
# 少了任何一邊，YouTube 一律回「Sign in to confirm you're not a bot」——那句話完全
# 看不出是「你的 cookies 沒有登入」，使用者只會以為自己被當成機器人，然後跑去換 IP、
# 調速度、等退燒，全都白費。所以要在送出去之前就自己驗一遍。
_YT_LOGIN_COOKIE = "LOGIN_INFO"
_YT_SID_COOKIES = ("SAPISID", "__Secure-1PAPISID", "__Secure-3PAPISID")


def youtube_login_cookies(path) -> tuple[bool, list[str]]:
    """檢查 cookies.txt 裡有沒有 YouTube 的登入憑證。

    回傳 ``(是否算登入, 缺少的項目)``。讀不到檔案時當作「無法判斷」——回傳
    ``(True, [])``，因為這只是輔助檢查，不該擋下本來可能成功的下載。
    """
    try:
        text = pathlib.Path(path).expanduser().read_text(
            encoding="utf-8", errors="replace")
    except OSError:
        return True, []

    names = set()
    for line in text.splitlines():
        if line.startswith("#") or not line.strip():
            continue
        fields = line.split("\t")
        if len(fields) >= 6 and "youtube.com" in fields[0]:
            names.add(fields[5].strip())

    missing = []
    if _YT_LOGIN_COOKIE not in names:
        missing.append(_YT_LOGIN_COOKIE)
    if not names & set(_YT_SID_COOKIES):
        missing.append("/".join(_YT_SID_COOKIES))
    return not missing, missing


# 上傳者常在標題前後塞自己的名字、頻道名、畫質標記，所以比對前要先刮掉一層。
_TITLE_NOISE = re.compile(
    r"""(?ix)
    \[[^\]]*\]                      # [Official] [HD] [4K] …
    | \([^)]*(?:official|mv|music\s*video|full|hd|4k|audio|lyrics?|字幕|完整)[^)]*\)
    | 【[^】]*】
    | (?:official\s*)?(?:music\s*)?video
    | full\s*version | full
    | mv | hd | 4k | remastered
    """,
)


def _title_tokens(title: str) -> set[str]:
    """把標題壓成可比對的詞集合。"""
    cleaned = _TITLE_NOISE.sub(" ", title or "")
    cleaned = re.sub(r"[^\w\u3040-\u30ff\u4e00-\u9fff]+", " ", cleaned.lower())
    return {tok for tok in cleaned.split() if len(tok) > 1 or not tok.isascii()}


def same_song(wanted: str, candidate: str) -> bool:
    """判斷搜尋結果是不是同一首歌。

    寧可漏掉也不要抓錯：下載到同名的翻唱、演唱會版或整張專輯，比「這首沒下到」
    更糟——使用者不會發現，直到播放清單裡冒出一段四十分鐘的東西。所以要求原標題
    的詞有大半都出現在候選標題裡，而不是只看相似度。
    """
    want = _title_tokens(wanted)
    if not want:
        return False
    got = _title_tokens(candidate)
    overlap = len(want & got)
    return overlap >= max(1, round(len(want) * 0.6))


def classify_url(url: str) -> str:
    """判斷網址指向單曲、播放清單，還是兩者皆有。

    回傳 ``video`` / ``playlist`` / ``both`` / ``unknown``。``both`` 就是
    ``watch?v=…&list=…`` 這種有歧義的網址——使用者可能只想要那一首，也可能
    想要整張清單，光看網址無從得知。
    """
    try:
        parsed = urllib.parse.urlparse(url.strip())
    except ValueError:
        return "unknown"

    host = parsed.netloc.lower()
    if host not in _YOUTUBE_HOSTS:
        return "unknown"  # 非 YouTube 網址交給 yt-dlp 自行判斷

    params = urllib.parse.parse_qs(parsed.query)
    has_list = bool(params.get("list"))
    if host.endswith("youtu.be"):
        has_video = bool(parsed.path.strip("/"))
    else:
        has_video = bool(params.get("v"))

    if has_video and has_list:
        return "both"
    if has_list:
        return "playlist"
    if has_video:
        return "video"
    return "unknown"


def is_radio_playlist(url: str) -> bool:
    """判斷是否為 YouTube 自動產生的混音清單（RD / RDAMVM 開頭，長度近乎無限）。"""
    try:
        params = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    except ValueError:
        return False
    return any(value.startswith("RD") for value in params.get("list", []))


_VIMEO_RE = re.compile(
    r"^https?://(?:www\.)?vimeo\.com/(?P<id>\d+)(?P<hash>/[0-9a-f]+)?/?(?:[?#].*)?$",
    re.IGNORECASE,
)


def vimeo_player_url(url: str) -> str | None:
    """把 ``vimeo.com/<id>`` 轉成 ``player.vimeo.com/video/<id>``。

    Vimeo 的一般頁面要先換 OAuth token，某些網路環境會被回 401；改走播放器
    網址就不需要那道手續。無法轉換時回傳 None。
    """
    match = _VIMEO_RE.match((url or "").strip())
    if not match:
        return None
    player = f"https://player.vimeo.com/video/{match.group('id')}"
    unlisted = match.group("hash")
    if unlisted:  # 未公開影片的雜湊要保留，否則會變成無權觀看
        player += f"?h={unlisted.lstrip('/')}"
    return player


def find_ffmpeg() -> str | None:
    """回傳 ffmpeg 可執行檔路徑，找不到則回傳 None。"""
    return shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")


# yt-dlp 認得的 JavaScript runtime，依偏好排序。deno 擺第一是因為 yt-dlp 預設
# 只自動啟用它，其餘的要明講才會用（我們在 _base_opts 裡替使用者講）。
JS_RUNTIMES = ("deno", "node", "bun", "quickjs")


def find_js_runtimes() -> dict[str, str]:
    """列出這台機器上找得到的 JS runtime：``{名稱: 執行檔路徑}``。

    YouTube 會把播放網址裡的 n 參數用 JavaScript 打亂，要真的跑得動那段 JS 才
    解得開。解不開的下場不是一句清楚的錯誤：可選畫質少掉一大半，或者解析成功、
    下載到一半被回 403——訊息只說 unable to download video data，完全看不出
    缺的其實是一個執行檔。
    """
    found: dict[str, str] = {}
    for name in JS_RUNTIMES:
        path = shutil.which(name) or shutil.which(f"{name}.exe")
        if path:
            found[name] = path
    return found



FFMPEG_HINT = """找不到 ffmpeg，音訊轉檔需要它。安裝方式：
  macOS         brew install ffmpeg
  Ubuntu/Debian sudo apt install ffmpeg
  Windows       winget install Gyan.FFmpeg
或改用 --no-convert 直接保留 YouTube 原始音訊（通常是 m4a／webm，不轉檔）。"""
