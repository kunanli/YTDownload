"""短網址展開。

會做這個是因為：使用者的 LinkedIn 一直失敗，而**每一次失敗的都是 `lnkd.in`
短網址**——完整的 `linkedin.com` 網址從來沒被測過。

`lnkd.in` 是 LinkedIn 的轉址服務，也因此出現在大量的追蹤器封鎖清單裡
（廣告阻擋、DNS 過濾、防毒的網頁防護都會擋它）。這類封鎖多半是看 SNI 的網域
名稱直接把連線切掉，症狀正是 UNEXPECTED_EOF——而同一台機器連 `linkedin.com`
可能完全正常。

所以與其想辦法「連上 lnkd.in」，不如**繞過它**：把短網址換成它指向的完整網址。
"""

from __future__ import annotations

# 常見的轉址服務。刻意不含 youtu.be——它是 YouTube 自家的，yt-dlp 直接認得，
# 而且從來不是連不上的原因。
SHORTENER_HOSTS = (
    "lnkd.in",
    "bit.ly",
    "t.co",
    "tinyurl.com",
    "ow.ly",
    "buff.ly",
    "goo.gl",
    "rebrand.ly",
    "is.gd",
    "cutt.ly",
)

DEFAULT_EXPANDER = "https://unshorten.me/json/{url}"

EXPANDER_NOTICE = """短網址展開會把這個網址送給第三方服務：
  {service}

送出去的只有網址本身，不會送出你的 cookies 或登入資訊。
（為什麼要這樣做：擋住你的很可能就是短網址那個網域本身，
  所以得由別人幫忙問出它指向哪裡。）"""


def short_host(url: str) -> str:
    """如果是已知的轉址服務，回傳它的網域；否則回空字串。"""
    lowered = (url or "").lower()
    if not lowered.startswith(("http://", "https://")):
        return ""
    host = lowered.split("//", 1)[-1].split("/", 1)[0].split(":")[0]
    host = host[4:] if host.startswith("www.") else host
    return host if host in SHORTENER_HOSTS else ""


def is_short_url(url: str) -> bool:
    return bool(short_host(url))


def parse_expanded(payload: dict, original: str) -> str:
    """從展開服務的回應裡取出完整網址。

    回傳空字串代表沒展開成功——包含「展開後還是同一個網址」這種情況，
    那等於沒幫上忙，不值得再拿去重試一次。
    """
    if not isinstance(payload, dict) or not payload.get("success", True):
        return ""
    resolved = (payload.get("resolved_url") or payload.get("url") or "").strip()
    if not resolved.startswith(("http://", "https://")):
        return ""
    return "" if resolved.rstrip("/") == (original or "").rstrip("/") else resolved


def expand(url: str, *, service: str = DEFAULT_EXPANDER, timeout: int = 20) -> str:
    """問展開服務這個短網址指向哪裡。失敗就回空字串。"""
    import json
    import urllib.request

    target = service.format(url=url) if "{url}" in service else f"{service}{url}"
    request = urllib.request.Request(target, headers={
        "accept": "application/json",
        "user-agent": "ytmusic (+https://github.com/kunanli/YTDownload)",
    })
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8", "replace"))
    except Exception:
        return ""
    return parse_expanded(payload, url)
