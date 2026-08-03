"""用 Playwright 開瀏覽器，攔截頁面自己發出的請求。

這一層直接操作瀏覽器，沒辦法在沒有微信帳號的環境測試，所以刻意寫得很薄——
所有判斷邏輯都放在 ``wechat.py``，這裡只負責「開瀏覽器、等、收集」。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from .config import config_home
from .wechat import (
    PLAYWRIGHT_HINT, CaptureResult, MediaCandidate, WECHAT_MEDIA_HOSTS,
    is_missing_browser_error, looks_like_media,
)

# 登入狀態存在這裡，掃碼一次之後就不用再掃。
def profile_dir() -> Path:
    return config_home() / "browser-profile"


class BrowserUnavailable(RuntimeError):
    """沒裝 Playwright 或瀏覽器啟動失敗。"""


def pip_install_command(package: str) -> list[str]:
    """一律用 `python -m pip`，才不會受 PATH 有沒有 Scripts 目錄影響。"""
    return [sys.executable, "-m", "pip", "install", package]


def browser_install_command() -> list[str]:
    """同理：`python -m playwright`，不是 `playwright`。"""
    return [sys.executable, "-m", "playwright", "install", "chromium"]


def _run(command: list[str], out) -> bool:
    import subprocess

    print(f"  執行：{' '.join(command[1:])}", file=out)
    try:
        return subprocess.run(command).returncode == 0
    except Exception as exc:
        print(f"  失敗：{exc}", file=out)
        return False


def _confirm(question: str, *, assume_yes: bool, ask, out) -> bool:
    if assume_yes:
        return True
    if not sys.stdin.isatty():
        return False  # 非互動環境不該擅自安裝東西
    try:
        return ask(f"{question} [Y/n] ").strip().lower() in {"", "y", "yes", "是"}
    except (EOFError, KeyboardInterrupt):
        print(file=out)
        return False


def ensure_playwright(*, assume_yes: bool = False, ask=input, out=None):
    """確保 Playwright 套件在；缺的話徵得同意後自動安裝。

    刻意先問過再裝——擅自在使用者機器上安裝套件不是該預設做的事。
    """
    out = out or sys.stderr
    try:
        from playwright.sync_api import sync_playwright
        return sync_playwright
    except ImportError:
        pass

    print("\n這個功能需要 Playwright（用來開瀏覽器），目前沒有安裝。", file=out)
    if not _confirm("要現在自動安裝嗎？", assume_yes=assume_yes, ask=ask, out=out):
        raise BrowserUnavailable(PLAYWRIGHT_HINT)

    if not _run(pip_install_command("playwright"), out):
        raise BrowserUnavailable(f"自動安裝失敗。\n\n{PLAYWRIGHT_HINT}")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise BrowserUnavailable(
            f"裝好了但仍然匯入不到，可能要重開視窗再試一次。\n\n{PLAYWRIGHT_HINT}"
        ) from exc
    print("  Playwright 安裝完成。\n", file=out)
    return sync_playwright


def ensure_browser(*, assume_yes: bool = False, ask=input, out=None) -> bool:
    """下載 Chromium。回傳是否成功。"""
    out = out or sys.stderr
    print("\n還缺瀏覽器本體（Chromium，約 150 MB）。", file=out)
    if not _confirm("要現在下載嗎？", assume_yes=assume_yes, ask=ask, out=out):
        return False
    return _run(browser_install_command(), out)


def capture_media(url: str, *, timeout: int = 120, headless: bool = False,
                  proxy: str | None = None, assume_yes: bool = False,
                  out=None) -> CaptureResult:
    """開瀏覽器載入頁面，回傳攔截到的影片來源。

    ``headless=False`` 是預設值：第一次使用時需要看得到畫面才能掃碼登入。
    登入狀態會存在設定目錄下，之後就不用再掃。
    """
    out = out or sys.stderr
    sync_playwright = ensure_playwright(assume_yes=assume_yes, out=out)

    result = CaptureResult(url=url)
    seen: dict[str, MediaCandidate] = {}

    def on_response(response) -> None:
        try:
            headers = response.headers
            content_type = headers.get("content-type", "")
            if not looks_like_media(response.url, content_type):
                return
            host = response.url.split("//", 1)[-1].split("/", 1)[0].split(":")[0]
            seen[response.url] = MediaCandidate(
                url=response.url,
                content_type=content_type,
                size=int(headers.get("content-length") or 0),
                from_media_host=any(host.endswith(h) for h in WECHAT_MEDIA_HOSTS),
            )
        except Exception:
            pass  # 攔截失敗不該中斷整個流程

    directory = profile_dir()
    directory.mkdir(parents=True, exist_ok=True)
    # 有些環境的 Chromium 不在 Playwright 預期的位置，留一個覆寫入口。
    executable = os.environ.get("YTMUSIC_CHROMIUM") or None
    # 需要透過代理才能連外的環境（公司網路、沙箱）也要能用。
    proxy = proxy or os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")

    launch_kwargs = {
        "user_data_dir": str(directory),
        "executable_path": executable,
        "headless": headless,
        "proxy": {"server": proxy, "bypass": "localhost,127.0.0.1"} if proxy else None,
        "ignore_https_errors": bool(proxy),  # 代理多半用自簽憑證
        "args": ["--autoplay-policy=no-user-gesture-required"],
    }

    with sync_playwright() as playwright:
        try:
            context = playwright.chromium.launch_persistent_context(**launch_kwargs)
        except Exception as exc:
            if not is_missing_browser_error(exc):
                raise BrowserUnavailable(
                    f"瀏覽器啟動失敗：{exc}\n\n{PLAYWRIGHT_HINT}") from exc
            if not ensure_browser(assume_yes=assume_yes, out=out):
                raise BrowserUnavailable(PLAYWRIGHT_HINT) from exc
            try:
                context = playwright.chromium.launch_persistent_context(**launch_kwargs)
            except Exception as retry_exc:
                raise BrowserUnavailable(
                    f"瀏覽器啟動失敗：{retry_exc}\n\n{PLAYWRIGHT_HINT}") from retry_exc

        try:
            page = context.pages[0] if context.pages else context.new_page()
            page.on("response", on_response)

            print("正在開啟頁面…", file=out)
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60_000)
            except Exception as exc:
                print(f"頁面載入有問題：{str(exc)[:120]}", file=out)

            result.title = _text(page, "h1, .video-title, .feed-desc") or page.title()
            result.author = _text(page, ".nickname, .account-nickname, .finder-nickname")

            print(f"\n請在開啟的瀏覽器視窗裡：", file=out)
            print("  1. 若出現 QR code，用手機微信掃碼登入（只需一次）", file=out)
            print("  2. 讓影片開始播放", file=out)
            print(f"\n最多等 {timeout} 秒，抓到影片就會自動繼續…\n", file=out)

            deadline = timeout * 1000
            step = 2000
            waited = 0
            while waited < deadline:
                page.wait_for_timeout(step)
                waited += step
                if any(c.from_media_host for c in seen.values()):
                    break
                if waited % 20000 == 0:
                    print(f"  仍在等待…（已等 {waited // 1000} 秒，"
                          f"目前攔到 {len(seen)} 個候選）", file=out)

            # 標題可能是影片開始播放後才填上的，這裡再讀一次
            result.title = _text(page, "h1, .video-title, .feed-desc") or result.title
            result.author = _text(page, ".nickname, .account-nickname, .finder-nickname") or result.author
            result.cookies = {c["name"]: c["value"] for c in context.cookies()}
        finally:
            context.close()

    result.candidates = list(seen.values())
    return result


def _text(page, selector: str) -> str:
    """讀取第一個符合選擇器的元素文字；讀不到就回空字串。"""
    try:
        locator = page.locator(selector).first
        if locator.count() == 0:
            return ""
        return (locator.inner_text(timeout=2000) or "").strip().split("\n")[0]
    except Exception:
        return ""
