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


@dataclass(frozen=True)
class MenuItem:
    key: str
    label: str


MENU_ITEMS = (
    MenuItem("1", "下載音樂（貼網址）"),
    MenuItem("2", "用歌名搜尋"),
    MenuItem("3", "下載影片（貼網址）"),
    MenuItem("4", "同步追蹤的播放清單"),
    MenuItem("5", "看下載過什麼"),
    MenuItem("6", "追蹤一張新的播放清單"),
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
        return ["dl", url] if url else None

    if choice == "2":
        keyword = ask("  要找什麼歌？ ").strip()
        return ["search", keyword] if keyword else None

    if choice == "3":
        url = ask("  貼上網址後按 Enter：").strip()
        if not url:
            return None
        answer = ask("\n   畫質：[1] 720p　[2] 1080p　[3] 最高\n  請選擇（直接按 Enter = 720p）：")
        quality = VIDEO_CHOICES.get(answer.strip() or "1", "720")
        return ["dl", url, "--video", quality]

    if choice == "4":
        return ["sync"]

    if choice == "5":
        return ["history", "list"]

    if choice == "6":
        url = ask("  貼上播放清單網址：").strip()
        if not url:
            return None
        name = ask("  取個名字（可直接按 Enter 跳過）：").strip()
        command = ["sync", "add", url]
        if name:
            command += ["--name", name]
        return command

    return None


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
