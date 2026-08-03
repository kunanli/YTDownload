"""互動式選單：給不想打指令的人用。

刻意把整個選單做在 Python 而不是 .bat / .sh 裡——cmd.exe 對 UTF-8 與換行格式
極度敏感，中文選單寫在批次檔裡會被切碎；放在 Python 就沒有這個問題，而且同一
份程式碼在 Windows、macOS、Linux 上表現一致，也測得到。
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Callable

BANNER = """
  ============================================
     YouTube 音樂下載器
  ============================================
"""

VIDEO_CHOICES = {"1": "720", "2": "1080", "3": "best"}

# 選單裡的字幕／歌詞語言，值直接餵給 --subs / --lyrics（lyrics.py 認得中文別名）。
LANGUAGE_CHOICES = (
    ("1", "繁中"), ("2", "簡中"), ("3", "英"),
    ("4", "日"), ("5", "韓"), ("6", "西班牙"),
)
YES = {"y", "yes", "要", "1"}


def ask_yes(ask: Callable[[str], str], question: str) -> bool:
    return ask(f"  {question}[y/Enter=不用] ").strip().lower() in YES


SEARCH_SITES = (("1", "youtube", "YouTube"), ("2", "bilibili", "Bilibili"))


def ask_site(ask: Callable[[str], str]) -> list[str]:
    """搜尋要在哪個站台。回傳可直接接在指令後面的參數。

    只有「搜尋」需要問——貼網址的情況 yt-dlp 自己認得出是哪個站台。
    """
    options = "　".join(f"[{key}] {label}" for key, _, label in SEARCH_SITES)
    answer = ask(f"\n   在哪裡搜尋：{options}\n  請選擇（直接按 Enter = YouTube）：").strip()
    if not answer:
        return []
    table = {key: value for key, value, _ in SEARCH_SITES}
    site = table.get(answer)
    return ["--site", site] if site and site != "youtube" else []


def ask_languages(ask: Callable[[str], str], what: str) -> str:
    """讓使用者挑字幕／歌詞語言，回傳像 "繁中,英" 的字串。

    直接按 Enter 代表全部語言都試（有哪個抓哪個），跟設定檔的預設一致。
    """
    options = "　".join(f"[{key}] {name}" for key, name in LANGUAGE_CHOICES)
    ask_text = (
        f"\n   {options}\n"
        f"   可複選，用逗號分隔（例如 1,3）\n"
        f"  {what}語言（直接按 Enter = 全部）："
    )
    answer = ask(ask_text).strip()
    if not answer:
        return ""  # 空字串＝沿用設定檔的語言清單

    table = dict(LANGUAGE_CHOICES)
    picked = [
        table[token.strip()]
        for token in answer.replace("，", ",").split(",")
        if table.get(token.strip())
    ]
    return ",".join(dict.fromkeys(picked))  # 去重且保留順序


@dataclass(frozen=True)
class MenuItem:
    key: str
    label: str


MENU_ITEMS = (
    MenuItem("1", "下載音樂（貼網址）"),
    MenuItem("2", "用歌名搜尋"),
    MenuItem("3", "用歌手名稱找歌"),
    MenuItem("4", "下載影片（貼網址）"),
    MenuItem("5", "下載微信視頻號（會開瀏覽器）"),
    MenuItem("6", "同步追蹤的播放清單"),
    MenuItem("7", "看下載過什麼"),
    MenuItem("8", "追蹤一張新的播放清單"),
)


class Cancelled(Exception):
    """使用者在輸入途中放棄（空輸入或 Ctrl+C）。"""


def render_menu() -> str:
    lines = [BANNER]
    for item in MENU_ITEMS:
        lines.append(f"    [{item.key}] {item.label}")
    lines.append("")
    lines.append("    [0] 離開")
    lines.append("")
    return "\n".join(lines)


def build_command(choice: str, ask: Callable[[str], str]) -> list[str] | None:
    """把選單選項轉成 ytmusic 的命令列參數。

    ``ask`` 負責跟使用者要輸入（測試時換成假的即可）。回傳 None 代表使用者
    放棄或選了無效項目，回到選單。
    """
    choice = (choice or "1").strip()

    if choice == "1":
        url = ask("  貼上網址後按 Enter：").strip()
        if not url:
            return None
        if redirect := _wechat_redirect(url, ask):
            return redirect
        command = ["dl", url]
        if ask_yes(ask, "要一起抓歌詞嗎？"):
            command += _lang_flag("--lyrics", ask_languages(ask, "歌詞"))
        return command + _playlist_flags(url, ask)

    if choice == "2":
        keyword = ask("  要找什麼歌？ ").strip()
        return ["search", keyword] + ask_site(ask) if keyword else None

    if choice == "3":
        artist = ask("  歌手名稱？ ").strip()
        if not artist:
            return None
        return ["search", "--artist", artist] + ask_site(ask)

    if choice == "4":
        url = ask("  貼上網址後按 Enter：").strip()
        if not url:
            return None
        if redirect := _wechat_redirect(url, ask):
            return redirect
        answer = ask("\n   畫質：[1] 720p　[2] 1080p　[3] 最高\n  請選擇（直接按 Enter = 720p）：")
        quality = VIDEO_CHOICES.get(answer.strip() or "1", "720")
        command = ["dl", url, "--video", quality]
        if ask_yes(ask, "要一起嵌入字幕嗎？"):
            command += _lang_flag("--subs", ask_languages(ask, "字幕"))
        return command + _playlist_flags(url, ask)

    if choice == "5":
        url = ask("  貼上視頻號網址（第一次使用請直接按 Enter 先登入）：").strip()
        if not url:
            return ["wechat", "--login"]
        return _wechat_command(url, ask)

    if choice == "6":
        return ["sync"]

    if choice == "7":
        return ["history", "list"]

    if choice == "8":
        url = ask("  貼上播放清單網址：").strip()
        if not url:
            return None
        name = ask("  取個名字（可直接按 Enter 跳過）：").strip()
        command = ["sync", "add", url]
        if name:
            command += ["--name", name]
        return command

    return None


def _wechat_command(url: str, ask: Callable[[str], str]) -> list[str]:
    """組出微信視頻號的指令；第一次要看得到視窗才能掃碼登入。"""
    headless = ask("  已經登入過了嗎？免開視窗執行 [y/Enter=顯示視窗] ")
    command = ["wechat", url]
    return command + ["--headless"] if headless.strip().lower() in YES else command


def _wechat_redirect(url: str, ask: Callable[[str], str]) -> list[str] | None:
    """使用者把微信網址貼進音樂／影片選項時，自動改走微信那條路。

    微信視頻號沒辦法用一般的網址解析下載，與其讓它失敗，不如直接轉過去——
    使用者不該需要知道哪個選單編號對應哪個平台。
    """
    from .wechat import is_wechat_url

    if not is_wechat_url(url):
        return None
    return _wechat_command(url, ask)


def _lang_flag(flag: str, languages: str) -> list[str]:
    """語言選了就帶上，沒選就只給旗標讓它用設定檔的預設。"""
    return [flag, languages] if languages else [flag]


def _playlist_flags(url: str, ask: Callable[[str], str]) -> list[str]:
    """網址是播放清單時，問要不要整張下載、要不要收進獨立資料夾。"""
    from .utils import classify_url

    kind = classify_url(url)
    if kind == "playlist":  # 純清單網址，本來就會整張下載
        return ["--playlist-folder"] if ask_yes(ask, "每張清單收進獨立資料夾嗎？") else []
    if kind != "both":
        return []

    if not ask_yes(ask, "這個網址含整張播放清單，要全部下載嗎？"):
        return ["--single"]
    flags = ["--playlist"]
    if ask_yes(ask, "收進以清單命名的資料夾嗎？"):
        flags.append("--playlist-folder")
    return flags


def run_menu(runner: Callable[[list[str]], int] | None = None, *,
             ask: Callable[[str], str] | None = None,
             out=None) -> int:
    """顯示選單並反覆執行使用者選的動作，直到選擇離開。"""
    out = out or sys.stdout
    runner = runner or _default_runner
    ask = ask or _default_ask

    last = 0
    while True:
        print(render_menu(), file=out)
        try:
            choice = ask("  請選擇（直接按 Enter = 1）：").strip()
        except (Cancelled, EOFError, KeyboardInterrupt):
            print("\n再見。", file=out)
            return last

        if choice in {"0", "q", "quit", "exit"}:
            print("\n再見。", file=out)
            return last

        try:
            command = build_command(choice, ask)
        except (Cancelled, EOFError, KeyboardInterrupt):
            print(file=out)
            continue

        if command is None:
            continue

        print(file=out)
        try:
            last = runner(command)
        except KeyboardInterrupt:
            print("\n已中斷。", file=out)
            last = 130

        print(file=out)
        try:
            ask("  按 Enter 回到選單…")
        except (Cancelled, EOFError, KeyboardInterrupt):
            return last


def _default_ask(prompt: str) -> str:
    try:
        return input(prompt)
    except EOFError:
        raise Cancelled from None


def _default_runner(argv: list[str]) -> int:
    from .cli import main  # 延後匯入，避免與 cli 互相 import

    return main(argv)
