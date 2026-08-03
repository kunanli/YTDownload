"""環境與連線檢查。

會做這個是因為：使用者回報「還是不行」，但我看不到他的機器。靠截圖來回猜
（裝了沒？版本對不對？是網址的問題還是網路的問題？）既慢又常猜錯。

這裡把「該問的都問一遍」變成一行指令：裝了什麼、版本對不對，以及同一個網址
用不同的連線方式試會怎樣——哪一招能通，答案就自己跳出來了。
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

OK = "✔"
BAD = "✖"
WARN = "!"


@dataclass(frozen=True)
class Check:
    """一項檢查的結果。"""

    label: str
    mark: str
    detail: str

    def line(self) -> str:
        from .utils import pad_display

        return f"  {self.mark} {pad_display(self.label, 12)}{self.detail}"


def impersonation_status() -> tuple[bool, str]:
    """curl_cffi 到底是沒裝、版本不對、還是好的。

    這三種情況的下一步完全不同，但 yt-dlp 一律只說「target 不可用」，
    所以得自己分辨——否則使用者只會反覆執行同一行沒用的安裝指令。
    """
    from .downloader import CURL_CFFI_SPEC

    try:
        import curl_cffi
    except ImportError:
        return False, f'沒有安裝　→　python -m pip install "{CURL_CFFI_SPEC}"'

    version = getattr(curl_cffi, "__version__", "?")
    try:
        from yt_dlp.networking._curlcffi import CurlCFFIRH  # noqa: F401
    except Exception as exc:
        return False, f"{version}　但 yt-dlp 載入失敗：{str(exc)[:60]}"

    marked = getattr(curl_cffi, "_yt_dlp__version", "")
    if "unsupported" in marked:
        return False, (f'{version} 不在 yt-dlp 支援範圍　→　'
                       f'python -m pip install "{CURL_CFFI_SPEC}"')
    return True, f"{version}　可用（{_targets() or '沒有可用目標'}）"


def _targets(limit: int = 4) -> str:
    """列出幾個可用的 impersonate 目標，證明它是真的能用。"""
    try:
        from yt_dlp.networking.impersonate import ImpersonateTarget  # noqa: F401
        from yt_dlp.networking._curlcffi import CurlCFFIRH

        names = [str(t) for t in CurlCFFIRH._SUPPORTED_IMPERSONATE_TARGET_MAP]
    except Exception:
        return ""
    shown = ", ".join(names[:limit])
    return f"{shown}…" if len(names) > limit else shown


def environment() -> list[Check]:
    """列出跟下載有關的每一項相依。"""
    from .utils import find_ffmpeg

    checks = [Check("Python", OK, sys.version.split()[0])]

    try:
        import yt_dlp

        checks.append(Check("yt-dlp", OK, yt_dlp.version.__version__))
    except Exception as exc:  # pragma: no cover - yt-dlp 是必要相依
        checks.append(Check("yt-dlp", BAD, f"匯入失敗：{exc}"))

    ffmpeg = find_ffmpeg()
    checks.append(Check("ffmpeg", OK, ffmpeg) if ffmpeg
                  else Check("ffmpeg", BAD, "找不到　→　轉檔與影片合併會失敗"))

    try:
        import mutagen

        checks.append(Check("mutagen", OK, mutagen.version_string))
    except Exception:
        checks.append(Check("mutagen", WARN, "沒有安裝　→　寫不了標籤與封面"))

    available, detail = impersonation_status()
    checks.append(Check("curl_cffi", OK if available else WARN, detail))

    try:
        import playwright  # noqa: F401

        checks.append(Check("playwright", OK, "已安裝（微信瀏覽器模式可用）"))
    except ImportError:
        checks.append(Check("playwright", WARN, "沒有安裝（只有微信瀏覽器模式需要）"))

    return checks


# 連線測試的三種方式，順序跟實際重試的順序一致。
def probes(config) -> list[tuple[str, str, dict]]:
    """回傳 (名稱, 說明, 要疊加到 yt-dlp 選項上的東西)。"""
    from .downloader import impersonate_target

    result = [
        ("一般連線", "跟平常一樣", {}),
        ("強制 IPv4", "治路由半通不通", {"source_address": "0.0.0.0"}),
    ]
    if impersonation_status()[0]:
        result.append(("假扮瀏覽器", "治對方看 TLS 指紋擋人",
                       {"impersonate": impersonate_target("chrome")}))
    return result


def probe_url(url: str, config, *, out=None) -> list[Check]:
    """同一個網址用每一種方式各試一次，回報哪一種通。"""
    from yt_dlp import YoutubeDL

    from .downloader import Downloader, _CollectingLogger, _short_error

    out = out or sys.stderr
    base = Downloader(config)._base_opts()
    base.update({"extract_flat": "in_playlist", "skip_download": True,
                 "noplaylist": True})
    # 設定檔可能已經固定了 impersonate，那會讓「一般連線」根本不是一般連線。
    base.pop("impersonate", None)

    def attempt(name: str, target: str, extra: dict) -> Check:
        logger = _CollectingLogger()
        print(f"  測試 {name}…", file=out, flush=True)
        try:
            with YoutubeDL({**base, **extra, "logger": logger}) as ydl:
                info = ydl.extract_info(target, download=False)
        except Exception as exc:
            return Check(name, BAD, _short_error(exc, logger)[:110])
        title = (info or {}).get("title") or (info or {}).get("id") or "（沒有標題）"
        return Check(name, OK, f"讀得到：{title[:60]}")

    results = [attempt(name, url, extra) for name, _, extra in probes(config)]

    # 短網址本身被擋是很常見的情況（lnkd.in 在不少封鎖清單上），而它跟
    # 「整個站台連不上」的處置完全不同——分開測才分得出來。
    full = _expanded(url, out=out)
    if full:
        results.append(attempt("完整網址", full, {}))
    return results


def _expanded(url: str, *, out) -> str:
    """短網址就展開成完整網址（先徵得同意）。不是短網址就回空字串。"""
    from .shorturl import EXPANDER_NOTICE, DEFAULT_EXPANDER, expand, short_host

    host = short_host(url)
    if not host:
        return ""
    print(f"\n  這是 {host} 短網址——它本身被擋的話，完整網址可能沒問題。",
          file=out)
    print(EXPANDER_NOTICE.format(service=DEFAULT_EXPANDER), file=out)
    if not sys.stdin.isatty():
        return ""
    try:
        if input("  要展開來一起測嗎？ [Y/n] ").strip().lower() not in {"", "y", "yes", "要"}:
            return ""
    except (EOFError, KeyboardInterrupt):
        return ""
    full = expand(url)
    print(f"  → {full}" if full else "  展開失敗。", file=out)
    return full


def conclusion(results: list[Check]) -> str:
    """把測試結果變成一句「所以你該做什麼」。"""
    if not results:
        return ""
    winners = [c for c in results if c.mark == OK]
    if not winners:
        return ("三種方式都連不上。這條網路到這個站台是不通的——"
                "換個網路（手機熱點）再跑一次 doctor，就能確定是網路還是站台的問題。")
    labels = {c.label for c in winners}
    blocked_short = "完整網址" in labels and not (labels - {"完整網址"})
    if blocked_short:
        return ("只有完整網址通得了——被擋的是短網址那個網域本身，不是這個站台。\n"
                "  下載時加 --expand 會自動換成完整網址，或自己在瀏覽器開一次短網址、"
                "複製網址列那串長的。")
    first = winners[0].label
    if first == "一般連線":
        return "一般連線就通了。剛才的失敗多半是暫時的，直接重跑下載即可。"
    if first == "強制 IPv4":
        return "強制 IPv4 才通，代表 IPv6 那條路有問題——下載時會自動改走，不用特別設定。"
    return ("只有假扮瀏覽器才通，代表對方在看 TLS 指紋擋非瀏覽器。\n"
            "  固定用這招：python -m ytmusic config set impersonate chrome")


def missing_advice(checks: list[Check]) -> list[str]:
    """環境檢查裡真正需要動手的項目。"""
    return [f"{c.label}：{c.detail}" for c in checks if c.mark == BAD]
