"""缺什麼就提醒、並幫忙裝。

雙擊啟動的人不會去看 README，也不該被要求看。缺東西時最糟的做法是等到下載到
一半才炸掉——所以選單一開啟就先檢查，缺了就當場說清楚並問要不要幫忙裝。

一律先問過再裝：擅自在別人的電腦上安裝東西不該是預設行為。非互動環境
（排程、管線）一律不問也不裝，只印出手動步驟。
"""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass

from .i18n import t


@dataclass(frozen=True)
class Dependency:
    """一項相依：缺了會怎樣，以及怎麼補。"""

    key: str
    label: str
    why_key: str                   # 缺了會少掉什麼功能（i18n 代號）
    required: bool                 # 必要的才會在啟動時主動詢問
    command: list[str] | None      # None 代表沒辦法自動裝
    manual: str                    # 自動裝不了、或裝失敗時給的手動步驟

    @property
    def why(self) -> str:
        return t(self.why_key)


def pip_command(spec: str) -> list[str]:
    """一律用 `python -m pip`：Windows 上 pip 的執行檔常常不在 PATH。"""
    return [sys.executable, "-m", "pip", "install", spec]


def ffmpeg_command(system: str, has: dict[str, bool]) -> list[str] | None:
    """依作業系統挑一個裝得動 ffmpeg 的指令；找不到套件管理器就回 None。

    Linux 上刻意不回傳指令——apt 需要 sudo，替使用者提權太超過了。
    """
    if system == "Windows" and has.get("winget"):
        return ["winget", "install", "--id", "Gyan.FFmpeg", "-e",
                "--accept-source-agreements", "--accept-package-agreements"]
    if system == "Darwin" and has.get("brew"):
        return ["brew", "install", "ffmpeg"]
    return None


FFMPEG_MANUAL = """  Windows：winget install Gyan.FFmpeg
  macOS：  brew install ffmpeg
  Linux：  sudo apt install ffmpeg
  裝完要把視窗關掉重開，電腦才找得到它。"""


def _tools() -> dict[str, bool]:
    return {name: bool(shutil.which(name)) for name in ("winget", "brew")}


def gaps(*, system: str | None = None, has: dict[str, bool] | None = None) -> list[Dependency]:
    """列出目前缺的東西。沒缺就回空清單（也就是什麼都不會打擾使用者）。"""
    from .doctor import impersonation_status
    from .utils import find_ffmpeg

    system = system or platform.system()
    has = _tools() if has is None else has
    missing: list[Dependency] = []

    try:
        import yt_dlp  # noqa: F401
    except ImportError:
        missing.append(Dependency(
            "yt-dlp", "yt-dlp", "dep.why.yt-dlp", True,
            pip_command("yt-dlp"), '  python -m pip install "yt-dlp"'))

    try:
        import mutagen  # noqa: F401
    except ImportError:
        missing.append(Dependency(
            "mutagen", "mutagen", "dep.why.mutagen", True,
            pip_command("mutagen"), '  python -m pip install "mutagen"'))

    if not find_ffmpeg():
        missing.append(Dependency(
            "ffmpeg", "ffmpeg", "dep.why.ffmpeg", True,
            ffmpeg_command(system, has), FFMPEG_MANUAL))

    if not impersonation_status()[0]:
        from .downloader import CURL_CFFI_SPEC

        missing.append(Dependency(
            "curl_cffi", "curl_cffi", "dep.why.curl_cffi", False,
            pip_command(CURL_CFFI_SPEC),
            f'  python -m pip install "{CURL_CFFI_SPEC}"'))

    return missing


def notice(missing: list[Dependency]) -> str:
    """開場提醒：缺什麼、會少掉什麼。沒缺就回空字串。"""
    if not missing:
        return ""
    lines = ["", f"  {t('deps.header')}", ""]
    for dep in missing:
        tag = t('deps.required') if dep.required else t('deps.optional')
        lines.append(f"  [{tag}] {dep.label}：{dep.why}")
    lines.append("")
    return "\n".join(lines)


def run(command: list[str], *, out) -> bool:
    """執行安裝指令，把過程直接顯示給使用者看。"""
    print(f"  {t('deps.running', command=' '.join(command))}", file=out, flush=True)
    try:
        return subprocess.run(command).returncode == 0
    except (OSError, subprocess.SubprocessError) as exc:
        print(f"  {t('deps.failed', error=exc)}", file=out)
        return False


def install_all(missing: list[Dependency], *, out) -> list[Dependency]:
    """逐一安裝，回傳仍然沒裝成功的。"""
    still: list[Dependency] = []
    for dep in missing:
        if dep.command is None:
            still.append(dep)
            continue
        print(f"\n  {t('deps.installing', name=dep.label)}", file=out)
        if not run(dep.command, out=out):
            still.append(dep)
    return still


def offer(missing: list[Dependency], *, ask, out,
          assume_yes: bool = False, include_optional: bool = False) -> list[Dependency]:
    """提醒使用者缺了什麼，問過之後幫忙裝。回傳仍然缺的項目。

    預設只主動幫裝「必要」的：選用項目照樣列出來讓使用者知道，但不追著問。
    """
    if not missing:
        return []
    print(notice(missing), file=out)

    wanted = [d for d in missing if d.required or include_optional]
    if not wanted:
        print(f"  {t('deps.optional_only')}\n", file=out)
        return missing

    if not assume_yes and not sys.stdin.isatty():
        _print_manual(wanted, out=out)  # 非互動環境不擅自安裝
        return missing

    if not assume_yes:
        try:
            answer = ask(f"  {t('deps.ask')}[Y/n] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print(file=out)
            return missing
        if answer not in {"", "y", "yes", "要"}:
            _print_manual(wanted, out=out)
            return missing

    still = install_all(wanted, out=out)
    if still:
        print(f"\n  {t('deps.still_missing')}", file=out)
        _print_manual(still, out=out)
    else:
        print(f"\n  {t('deps.done')}\n", file=out)
    return still + [d for d in missing if d not in wanted]


def _print_manual(deps: list[Dependency], *, out) -> None:
    for dep in deps:
        print(f"\n  {dep.label}：", file=out)
        print(dep.manual, file=out)
    print(file=out)
