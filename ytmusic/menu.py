"""互動式選單：給不想打指令的人用。

刻意把整個選單做在 Python 而不是 .bat / .sh 裡——cmd.exe 對 UTF-8 與換行格式
極度敏感，中文選單寫在批次檔裡會被切碎；放在 Python 就沒有這個問題，而且同一
份程式碼在 Windows、macOS、Linux 上表現一致，也測得到。介面語言切換也是同樣
的理由做在這裡：批次檔連中文都印不好，更別說六種語言。
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Callable

from .i18n import t

VIDEO_CHOICES = {"1": "720", "2": "1080", "3": "best"}

# 字幕／歌詞語言。值直接餵給 --subs / --lyrics（lyrics.py 認得這些中文別名），
# 所以**不能**跟著介面語言變；只有畫面上顯示的名稱會翻譯。
LANGUAGE_CHOICES = (
    ("1", "繁中"), ("2", "簡中"), ("3", "英"),
    ("4", "日"), ("5", "韓"), ("6", "西班牙"),
)
_LANGUAGE_LABELS = {
    "繁中": "sublang.zh-Hant", "簡中": "sublang.zh-Hans", "英": "sublang.en",
    "日": "sublang.ja", "韓": "sublang.ko", "西班牙": "sublang.es",
}
YES = {"y", "yes", "要", "1", "はい", "예", "sí", "si", "kyllä"}


def paste_hint() -> str:
    return t("paste.hint")


def ask_required(ask: Callable[[str], str], prompt: str, *, tries: int = 3) -> str:
    """要一個非空的輸入，空白就再問一次。

    貼上失敗、或貼到的內容夾帶換行時，使用者會送出空字串。原本一收到空值就
    踢回選單，等於連重貼的機會都沒有——重問才是對的。
    """
    for attempt in range(tries):
        answer = ask(prompt).strip()
        if answer:
            return "" if answer.lower() in {"q", "quit", "取消"} else answer
        if attempt < tries - 1:
            prompt = f"  {t('retry.blank')}\n  {paste_hint()}\n{prompt}"
    return ""


def ask_yes(ask: Callable[[str], str], question_key: str) -> bool:
    return ask(f"  {t(question_key)}{t('yesno.suffix')} ").strip().lower() in YES


SEARCH_SITES = (("1", "youtube", "YouTube"), ("2", "bilibili", "Bilibili"))


def ask_site(ask: Callable[[str], str]) -> list[str]:
    """搜尋要在哪個站台。回傳可直接接在指令後面的參數。

    只有「搜尋」需要問——貼網址的情況 yt-dlp 自己認得出是哪個站台。
    """
    options = "　".join(f"[{key}] {label}" for key, _, label in SEARCH_SITES)
    answer = ask(f"\n   {t('site.where')}{options}\n  {t('site.choose')}").strip()
    if not answer:
        return []
    table = {key: value for key, value, _ in SEARCH_SITES}
    site = table.get(answer)
    return ["--site", site] if site and site != "youtube" else []


def ask_languages(ask: Callable[[str], str], kind: str) -> str:
    """讓使用者挑字幕／歌詞語言，回傳像 "繁中,英" 的字串。

    ``kind`` 是 "subs" 或 "lyrics"，只影響提示文字。直接按 Enter 代表全部語言
    都試，跟設定檔的預設一致。
    """
    options = "　".join(f"[{key}] {t(_LANGUAGE_LABELS[value])}"
                        for key, value in LANGUAGE_CHOICES)
    answer = ask(f"\n   {options}\n   {t('lang.multi')}\n  {t(f'lang.{kind}')}").strip()
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
    label_key: str

    @property
    def label(self) -> str:
        return t(self.label_key)


MENU_ITEMS = (
    MenuItem("1", "menu.music"),
    MenuItem("2", "menu.search_song"),
    MenuItem("3", "menu.search_artist"),
    MenuItem("4", "menu.video"),
    MenuItem("5", "menu.wechat"),
    MenuItem("6", "menu.sync"),
    MenuItem("7", "menu.history"),
    MenuItem("8", "menu.subscribe"),
    MenuItem("9", "menu.doctor"),
    MenuItem("L", "menu.language"),
)


class Cancelled(Exception):
    """使用者在輸入途中放棄（空輸入或 Ctrl+C）。"""


def render_menu() -> str:
    width = 48
    lines = ["", "  " + "=" * width,
             f"     {t('app.title')}", f"     {t('app.subtitle')}",
             "  " + "=" * width, ""]
    for item in MENU_ITEMS:
        lines.append(f"    [{item.key}] {item.label}")
    lines.append("")
    lines.append(f"    [0] {t('menu.quit')}")
    lines.append("")
    return "\n".join(lines)


def build_command(choice: str, ask: Callable[[str], str]) -> list[str] | None:
    """把選單選項轉成 ytmusic 的命令列參數。

    ``ask`` 負責跟使用者要輸入（測試時換成假的即可）。回傳 None 代表使用者
    放棄或選了無效項目，回到選單。
    """
    choice = (choice or "1").strip()

    if choice == "1":
        url = ask_required(ask, f"  {t('prompt.url')}")
        if not url:
            return None
        if redirect := _wechat_redirect(url, ask):
            return redirect
        command = ["dl", url]
        if ask_yes(ask, "ask.lyrics"):
            command += _lang_flag("--lyrics", ask_languages(ask, "lyrics"))
        return command + _playlist_flags(url, ask)

    if choice == "2":
        keyword = ask_required(ask, f"  {t('prompt.keyword')}")
        return ["search", keyword] + ask_site(ask) if keyword else None

    if choice == "3":
        artist = ask_required(ask, f"  {t('prompt.artist')}")
        if not artist:
            return None
        return ["search", "--artist", artist] + ask_site(ask)

    if choice == "4":
        url = ask_required(ask, f"  {t('prompt.url')}")
        if not url:
            return None
        if redirect := _wechat_redirect(url, ask):
            return redirect
        answer = ask(f"\n   {t('quality.label')}[1] 720p　[2] 1080p　"
                     f"[3] {t('quality.best')}\n  {t('quality.choose')}")
        quality = VIDEO_CHOICES.get(answer.strip() or "1", "720")
        command = ["dl", url, "--video", quality]
        if ask_yes(ask, "ask.subs"):
            command += _lang_flag("--subs", ask_languages(ask, "subs"))
        return command + _playlist_flags(url, ask)

    if choice == "5":
        url = ask(f"  {t('prompt.wechat_url')}").strip()
        if not url:
            return ["wechat", "--login"]
        return _wechat_command(url, ask)

    if choice == "6":
        return ["sync"]

    if choice == "7":
        return ["history", "list"]

    if choice == "8":
        url = ask_required(ask, f"  {t('prompt.playlist_url')}")
        if not url:
            return None
        name = ask(f"  {t('prompt.playlist_name')}").strip()
        command = ["sync", "add", url]
        if name:
            command += ["--name", name]
        return command

    if choice == "9":
        # 網址可留空：只想看裝了什麼的時候不該被逼著貼網址。
        url = ask(f"  {t('prompt.doctor_url')}").strip()
        return ["doctor", url] if url else ["doctor"]

    return None


def render_language_menu() -> str:
    from .i18n import available, language

    current = language()
    lines = ["", f"   {t('ui.title')}", ""]
    for index, (code, name) in enumerate(available(), start=1):
        mark = "*" if code == current else " "
        lines.append(f"    [{index}]{mark}{name}")
    lines.append("")
    return "\n".join(lines)


def choose_language(ask: Callable[[str], str], out) -> str:
    """顯示語言清單並套用選擇，回傳生效的語言代號。

    選完立刻寫進設定檔——使用者換語言的意思顯然是「以後都用這個」，
    再要他去記一個 config 指令太不近人情。
    """
    from .config import Config
    from .i18n import available, language, language_name, set_language

    print(render_language_menu(), file=out)
    answer = ask(f"  {t('ui.choose')}").strip()
    options = available()
    if not answer.isdigit() or not 1 <= int(answer) <= len(options):
        return language()

    code = options[int(answer) - 1][0]
    set_language(code)
    try:
        Config.load().merged(ui_language=code).save()
    except OSError as exc:
        print(f"  {t('ui.save_failed', error=exc)}", file=out)
    else:
        print(f"  {t('ui.saved', name=language_name(code))}", file=out)
    return code


def _wechat_command(url: str, ask: Callable[[str], str]) -> list[str]:
    """組出微信視頻號的指令。

    不再問畫質、登入或視窗——現在是直接問微信的 API 拿影片位址，
    多數情況下連瀏覽器都不會開。真的拿不到時，指令自己會問要不要線上解析。
    """
    return ["wechat", url]


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
        return ["--playlist-folder"] if ask_yes(ask, "ask.folder_each") else []
    if kind != "both":
        return []

    if not ask_yes(ask, "ask.playlist_all"):
        return ["--single"]
    flags = ["--playlist"]
    if ask_yes(ask, "ask.folder_named"):
        flags.append("--playlist-folder")
    return flags


def run_menu(runner: Callable[[list[str]], int] | None = None, *,
             ask: Callable[[str], str] | None = None,
             out=None) -> int:
    """顯示選單並反覆執行使用者選的動作，直到選擇離開。"""
    out = out or sys.stdout
    runner = runner or _default_runner
    ask = ask or _default_ask

    _first_run_language(ask, out)
    _check_dependencies(ask, out)

    last = 0
    while True:
        print(render_menu(), file=out)
        try:
            choice = ask(f"  {t('prompt.choice')}").strip()
        except (Cancelled, EOFError, KeyboardInterrupt):
            print(f"\n{t('bye')}", file=out)
            return last

        if choice in {"0", "q", "quit", "exit"}:
            print(f"\n{t('bye')}", file=out)
            return last

        if choice.lower() == "l":
            try:
                choose_language(ask, out)
            except (Cancelled, EOFError, KeyboardInterrupt):
                print(file=out)
            continue

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
            print(f"\n{t('interrupted')}", file=out)
            last = 130

        print(file=out)
        try:
            ask(f"  {t('prompt.back')}")
        except (Cancelled, EOFError, KeyboardInterrupt):
            return last


def _first_run_language(ask: Callable[[str], str], out) -> None:
    """第一次執行時問一次介面語言，選過就不再問。"""
    from .config import Config
    from .i18n import set_language

    try:
        config = Config.load()
    except Exception:
        return
    if config.ui_language:
        set_language(config.ui_language)
        return
    if not sys.stdin.isatty():
        return  # 排程／管線裡沒有人可以回答，別把流程卡住
    try:
        choose_language(ask, out)
    except (Cancelled, EOFError, KeyboardInterrupt):
        print(file=out)


def _check_dependencies(ask: Callable[[str], str], out) -> None:
    """開場先看缺什麼，缺了就問要不要幫忙裝。

    雙擊啟動的人不會去看 README，也不該被要求看；缺東西時最糟的是等到下載到
    一半才炸掉。沒缺的話這裡完全不會出聲。
    """
    from .installer import gaps, offer

    try:
        missing = gaps()
    except Exception:
        return  # 檢查本身出錯不該擋住整個選單
    if missing:
        offer(missing, ask=ask, out=out)


def _default_ask(prompt: str) -> str:
    try:
        return input(prompt)
    except EOFError:
        raise Cancelled from None


def _default_runner(argv: list[str]) -> int:
    from .cli import main  # 延後匯入，避免與 cli 互相 import

    return main(argv)
