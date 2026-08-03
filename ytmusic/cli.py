"""ytmusic 的命令列進入點。"""

from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import fields
from pathlib import Path

from . import __version__
from .config import AUDIO_FORMATS, QUALITIES, Config, coerce_value
from .downloader import DownloadAborted, Downloader, Result, Track
from .history import History, default_history_path
from .progress import ProgressReporter
from .search import (
    SelectionError, filter_by_artist, format_results, parse_selection,
)
from .subscriptions import SubscriptionError, Subscriptions
from .utils import classify_url, human_size, is_radio_playlist

VIDEO_QUALITIES = ("best", "2160", "1440", "1080", "720", "480", "360")
# 預設抓中文，抓不到就退英文；zh-Hant/zh-Hans 涵蓋繁簡自動字幕。
SUBS_USE_CONFIG = ""  # --subs 不帶值時改用設定檔的語言

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_USAGE = 2
EXIT_PRECONDITION = 3
EXIT_PARTIAL = 4
EXIT_INTERRUPTED = 130


# --------------------------------------------------------------------------
# 參數定義
# --------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ytmusic",
        description="影音下載器：支援 YouTube、Bilibili、Vimeo、微信視頻號等 1700 多個網站。\n"
                    "下載音訊或影片、轉檔、寫入標籤與封面、抓歌詞字幕，並記錄下載歷史。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "範例：\n"
            "  ytmusic menu                                   互動式選單，不用記指令\n"
            "  ytmusic dl <網址>                              下載音樂（自動辨識站台）\n"
            "  ytmusic dl <網址> --video 1080 --subs          下載影片並嵌字幕\n"
            "  ytmusic search \"歌名\"                          用歌名搜尋\n"
            "  ytmusic wechat --login                         微信視頻號：先掃碼登入\n"
            "  ytmusic sync                                   補上訂閱清單的新歌\n"
        ),
    )
    parser.add_argument("-V", "--version", action="version", version=f"ytmusic {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    _add_menu_parser(sub)
    _add_download_parser(sub)
    _add_search_parser(sub)
    _add_sync_parser(sub)
    _add_wechat_parser(sub)
    _add_history_parser(sub)
    _add_config_parser(sub)
    return parser


def _add_menu_parser(sub) -> None:
    p = sub.add_parser(
        "menu", help="開啟互動式選單（不用記指令）",
        description="用選單操作，不需要記任何指令。雙擊啟動檔開的就是這個。",
    )
    p.set_defaults(func=cmd_menu)


def cmd_menu(args: argparse.Namespace) -> int:
    from .menu import run_menu

    return run_menu()


def _add_download_parser(sub) -> None:
    p = sub.add_parser(
        "download", aliases=["dl"], help="下載一或多個影片／播放清單的音訊",
        description="下載音訊並轉檔、寫標籤，已下載過的影片預設會自動略過。",
    )
    p.add_argument("urls", nargs="+", metavar="URL", help="影片、播放清單或頻道網址")
    p.add_argument("--single", action="store_true",
                   help="網址同時含播放清單時，只下載該首")
    p.add_argument("--playlist", action="store_true",
                   help="網址同時含播放清單時，下載整張清單")
    _add_download_options(p)
    p.set_defaults(func=cmd_download)


def _add_download_options(p) -> None:
    """download / search / sync 共用的下載選項。"""
    p.add_argument("--dry-run", action="store_true",
                   help="只列出將要下載的曲目，不實際下載")
    p.add_argument("--video", nargs="?", const="best", choices=VIDEO_QUALITIES,
                   metavar="RES",
                   help="下載影片而非只要音訊；可指定畫質上限，例如 --video 1080")
    p.add_argument("--subs", nargs="?", const=SUBS_USE_CONFIG, metavar="LANG",
                   help="下載影片時一併嵌入字幕；可指定語言，例如 --subs 繁中,英")
    p.add_argument("--lyrics", nargs="?", const=SUBS_USE_CONFIG, metavar="LANG",
                   help="下載音樂時附上歌詞（存成 .lrc 並寫進標籤）")
    p.add_argument("-o", "--output", metavar="DIR", help="輸出資料夾")
    p.add_argument("-f", "--format", dest="audio_format", choices=AUDIO_FORMATS,
                   help="音訊格式（預設 mp3）")
    p.add_argument("-q", "--quality", choices=QUALITIES, help="音質，數字為 kbps（預設 192）")
    p.add_argument("-j", "--jobs", type=int, metavar="N", help="同時下載數（預設 3，上限 16）")
    p.add_argument("--playlist-folder", action="store_true", default=None,
                   help="以播放清單名稱建立子資料夾")
    p.add_argument("--no-convert", action="store_true",
                   help="不轉檔，保留 YouTube 原始音訊（不需要 ffmpeg）")
    p.add_argument("--no-tags", action="store_true", help="不寫入 ID3／中繼資料標籤")
    p.add_argument("--no-cover", action="store_true", help="不嵌入專輯封面")
    p.add_argument("--no-rename", action="store_true",
                   help="不依標籤重新命名，直接沿用 yt-dlp 檔名樣板的結果")
    p.add_argument("--no-history", action="store_true", help="這次不讀也不寫下載歷史")
    p.add_argument("--force", action="store_true", help="忽略下載歷史，重新下載")
    p.add_argument("--template", metavar="TMPL", help="yt-dlp 檔名樣板，需包含 %%(ext)s")
    p.add_argument("--cookies", metavar="FILE", help="cookies.txt 路徑（用於年齡限制／會員內容）")
    p.add_argument("--cookies-from-browser", metavar="BROWSER",
                   help="從瀏覽器讀取 cookies，例如 chrome、firefox、edge")
    p.add_argument("--proxy", metavar="URL", help="HTTP/SOCKS 代理伺服器")
    p.add_argument("--rate-limit", metavar="RATE", help="限速，例如 500K、1.5M")
    p.add_argument("--no-progress", action="store_true", help="關閉進度列，只輸出純文字")
    p.add_argument("-v", "--verbose", action="store_true",
                   help="印出 yt-dlp 的完整診斷輸出，用來查明失敗原因")


def _add_search_parser(sub) -> None:
    p = sub.add_parser(
        "search", aliases=["s"], help="用歌名搜尋並挑選要下載的曲目",
        description="輸入關鍵字搜尋 YouTube，列出結果讓你挑，選好就直接下載。",
    )
    p.add_argument("query", nargs="+", metavar="關鍵字", help="歌名、歌手，或兩者一起")
    p.add_argument("-n", "--limit", type=int, default=8, metavar="N",
                   help="顯示幾筆結果（預設 8，上限 50）")
    p.add_argument("--first", action="store_true",
                   help="不詢問，直接下載第一筆（適合寫在腳本裡）")
    p.add_argument("--site", choices=("youtube", "bilibili"), default="youtube",
                   help="要搜尋哪個站台（預設 youtube）")
    p.add_argument("-a", "--artist", action="store_true",
                   help="把關鍵字當成歌手名：只列出該歌手頻道的單曲，排除翻唱與合輯")
    _add_download_options(p)
    p.set_defaults(func=cmd_search, single=True, playlist=False)


def _add_sync_parser(sub) -> None:
    p = sub.add_parser(
        "sync", help="追蹤播放清單，之後一行指令補上新增的曲目",
        description="把播放清單加進追蹤名單，之後跑 ytmusic sync 就會只下載新增的曲目。",
    )
    ssub = p.add_subparsers(dest="action", metavar="<action>")

    add = ssub.add_parser("add", help="加入一張要追蹤的播放清單")
    add.add_argument("url", metavar="URL")
    add.add_argument("--name", metavar="NAME", help="自訂名稱，省略則自動命名")
    add.add_argument("-o", "--output", metavar="DIR", help="這張清單專用的輸出資料夾")
    add.add_argument("--video", nargs="?", const="best", choices=VIDEO_QUALITIES,
                     metavar="RES", help="這張清單固定下載影片")
    add.set_defaults(func=cmd_sync_add)

    listing = ssub.add_parser("list", help="列出追蹤中的播放清單")
    listing.set_defaults(func=cmd_sync_list)

    remove = ssub.add_parser("remove", help="取消追蹤")
    remove.add_argument("name", metavar="NAME")
    remove.set_defaults(func=cmd_sync_remove)

    rename = ssub.add_parser("rename", help="改名")
    rename.add_argument("old", metavar="舊名稱")
    rename.add_argument("new", metavar="新名稱")
    rename.set_defaults(func=cmd_sync_rename)

    run = ssub.add_parser("run", help="同步（預設動作，可省略）")
    run.add_argument("names", nargs="*", metavar="NAME",
                     help="只同步指定的清單，省略則全部")
    _add_download_options(run)
    run.set_defaults(func=cmd_sync_run)

    # 直接打 `ytmusic sync` 就等於 `ytmusic sync run`
    _add_download_options(p)
    p.set_defaults(func=cmd_sync_run, action="run", names=[])


def _add_wechat_parser(sub) -> None:
    p = sub.add_parser(
        "wechat", aliases=["wx"], help="下載微信視頻號",
        description="直接問微信的 get_feed_info API 取得影片位址並下載，多數情況"
                    "不需要瀏覽器也不需要登入。微信不給位址時可用 --resolver "
                    "改請線上服務代查，或 --browser 開瀏覽器試一次。",
    )
    p.add_argument("url", nargs="?", metavar="URL", help="視頻號網址")
    p.add_argument("--login", action="store_true",
                   help="只開瀏覽器掃碼登入，按 Enter 才關閉（第一次先做這步）")
    p.add_argument("-o", "--output", metavar="DIR", help="輸出資料夾")
    p.add_argument("--timeout", type=int, default=120, metavar="秒",
                   help="最多等多久（預設 120 秒）")
    p.add_argument("--headless", action="store_true",
                   help="不顯示瀏覽器視窗（已登入過才能用，第一次登入需要看得到畫面）")
    p.add_argument("--browser", action="store_true",
                   help="即使微信已表明網頁端拿不到影片，仍然開瀏覽器試一次")
    p.add_argument("--resolver", action="store_true",
                   help="微信不給影片位址時，改用線上解析服務代查（會把網址送給第三方）")
    p.add_argument("--no-resolver", dest="no_resolver", action="store_true",
                   help="永遠不要用線上解析服務，也不要詢問")
    p.add_argument("--resolver-url", metavar="URL",
                   help="自訂線上解析服務的位址（可自架）")
    p.add_argument("--keep-broken", action="store_true",
                   help="即使抓到的檔案看起來不能播也保留下來")
    p.add_argument("-y", "--yes", action="store_true",
                   help="需要安裝 Playwright／瀏覽器時不詢問，直接裝")
    p.set_defaults(func=cmd_wechat)


def cmd_wechat(args: argparse.Namespace) -> int:
    from .browser import BrowserUnavailable, capture_media, profile_dir
    from .wechat import (
        DEFAULT_RESOLVER, ENCRYPTED_HINT, RESOLVER_NOTICE, WEB_BLOCKED_HINT,
        MediaCandidate, CaptureResult, download_media, fetch_feed_info,
        is_wechat_url, looks_like_playable_video, resolve_via_service,
        suggest_filename,
    )

    if args.login:
        from .browser import login

        try:
            login(assume_yes=args.yes)
        except BrowserUnavailable as exc:
            print(str(exc), file=sys.stderr)
            return EXIT_PRECONDITION
        print("\n登入完成。現在可以下載了：\n"
              "  python -m ytmusic wechat \"視頻號網址\"", file=sys.stderr)
        return EXIT_OK

    if not args.url:
        print("請給我視頻號網址，或先用 --login 掃碼登入。", file=sys.stderr)
        return EXIT_USAGE

    if not is_wechat_url(args.url):
        print("這看起來不是微信視頻號的網址。一般網址請用 `ytmusic dl`。",
              file=sys.stderr)
        return EXIT_USAGE

    config = Config.load()
    output_dir = Path(args.output).expanduser() if args.output else config.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # 先直接問微信的 API：不必開瀏覽器，一秒就知道這支影片拿不拿得到。
    # 抓得到就省下整段瀏覽器流程；拿不到也能立刻說明原因，而不是等兩分鐘才失敗。
    print("正在向微信查這支影片…", file=sys.stderr)
    feed = fetch_feed_info(args.url)
    if feed is not None and (feed.title or feed.author):
        print(f"  {feed.author or '（未知作者）'}｜{feed.title or '（無標題）'}",
              file=sys.stderr)

    # 同一支 API 換個出口 IP 問就可能給影片位址，所以拿不到時先問使用者要不要
    # 讓線上服務代查——但一定要先講清楚網址會送去哪裡。
    if (feed is None or not feed.playable) and not args.no_resolver:
        service = args.resolver_url or DEFAULT_RESOLVER
        if _confirm_resolver(service, assume_yes=args.resolver):
            print("正在請線上服務代查…", file=sys.stderr)
            remote = resolve_via_service(args.url, service=service)
            if remote is not None and remote.playable:
                remote.title = remote.title or (feed.title if feed else "")
                remote.author = remote.author or (feed.author if feed else "")
                feed = remote
            else:
                print("  線上服務也沒查到。", file=sys.stderr)

    result = None
    if feed is not None:
        if feed.playable:
            result = CaptureResult(
                url=args.url, title=feed.title, author=feed.author,
                candidates=[MediaCandidate(url=u, content_type="video/mp4",
                                           from_media_host=True)
                            for u in feed.video_urls],
            )
            print("  拿到影片位址了，不用開瀏覽器。", file=sys.stderr)
        elif not args.browser:
            reason = feed.error_title or "微信沒有回傳影片位址"
            print(f"\n✖ 拿不到：{reason}\n\n{WEB_BLOCKED_HINT}", file=sys.stderr)
            return EXIT_PRECONDITION

    try:
        if result is None:
            result = capture_media(args.url, timeout=args.timeout,
                                   headless=args.headless, assume_yes=args.yes)
    except BrowserUnavailable as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_PRECONDITION
    except KeyboardInterrupt:
        print("\n已中斷。", file=sys.stderr)
        return EXIT_INTERRUPTED

    best = result.best
    if best is None:
        print(f"沒有攔截到影片。\n\n{WEB_BLOCKED_HINT}", file=sys.stderr)
        _dump_observed(result)
        print(f"登入狀態存在：{profile_dir()}", file=sys.stderr)
        return EXIT_PRECONDITION

    stem = suggest_filename(result.title, result.author)
    target = output_dir / f"{stem}.mp4"
    print(f"\n找到影片，開始下載 → {target.name}", file=sys.stderr)

    def show(done: int, total: int) -> None:
        if total:
            print(f"\r  {human_size(done)} / {human_size(total)}"
                  f"  ({done * 100 // total}%)", end="", file=sys.stderr)

    try:
        written = download_media(best, target, cookies=result.cookies,
                                 referer=args.url, progress=show)
    except Exception as exc:
        print(f"\n下載失敗：{str(exc)[:150]}", file=sys.stderr)
        return EXIT_FAILED
    print(file=sys.stderr)

    with open(target, "rb") as handle:
        head = handle.read(16)
    if not looks_like_playable_video(head):
        print(f"\n⚠ {ENCRYPTED_HINT}", file=sys.stderr)
        _dump_observed(result)
        if not args.keep_broken:
            target.unlink(missing_ok=True)
            print("\n（檔案已刪除，要保留請加 --keep-broken）", file=sys.stderr)
            return EXIT_FAILED

    print(f"\n完成　{human_size(written)}　→ {target}", file=sys.stderr)
    return EXIT_OK


def _confirm_resolver(service: str, *, assume_yes: bool) -> bool:
    """問使用者要不要把網址交給第三方服務。

    這一步會把資料送出本機，所以預設不做——`--resolver` 才是明示同意，
    非互動環境（排程、腳本）一律不問也不送。
    """
    from .wechat import RESOLVER_NOTICE

    if assume_yes:
        return True
    if not sys.stdin.isatty():
        return False
    print(f"\n{RESOLVER_NOTICE.format(service=service)}", file=sys.stderr)
    try:
        return input("要用線上解析代查嗎？ [y/N] ").strip().lower() in {"y", "yes", "要"}
    except (EOFError, KeyboardInterrupt):
        print(file=sys.stderr)
        return False


def _dump_observed(result) -> None:
    """把頁面發出的請求列出來。

    抓錯或抓不到時，這是唯一能判斷「頁面到底要了什麼」的線索；
    沒有它就只能瞎猜。
    """
    if not result.observed:
        print("\n（沒有攔截到任何請求）", file=sys.stderr)
        return
    print(f"\n頁面共發出 {len(result.observed)} 個請求，最大的幾個：",
          file=sys.stderr)
    for candidate in result.observed[:12]:
        print(f"  {candidate.describe()}", file=sys.stderr)
    print("\n如果上面看得到像影片的網址，請把這段貼給開發者。", file=sys.stderr)


def _add_history_parser(sub) -> None:
    p = sub.add_parser("history", help="檢視或維護下載歷史")
    hsub = p.add_subparsers(dest="action", metavar="<action>")

    listing = hsub.add_parser("list", help="列出最近的下載紀錄")
    listing.add_argument("-n", "--limit", type=int, default=20, help="顯示筆數（0 表示全部）")
    listing.set_defaults(func=cmd_history_list)

    remove = hsub.add_parser("remove", help="移除指定影片 ID 的紀錄")
    remove.add_argument("video_ids", nargs="+", metavar="ID")
    remove.set_defaults(func=cmd_history_remove)

    prune = hsub.add_parser("prune", help="清掉檔案已不存在的紀錄")
    prune.set_defaults(func=cmd_history_prune)

    clear = hsub.add_parser("clear", help="清空全部紀錄")
    clear.add_argument("-y", "--yes", action="store_true", help="不詢問直接清空")
    clear.set_defaults(func=cmd_history_clear)

    p.set_defaults(func=cmd_history_list, action="list", limit=20)


def _add_config_parser(sub) -> None:
    p = sub.add_parser("config", help="檢視或修改預設設定")
    csub = p.add_subparsers(dest="action", metavar="<action>")

    show = csub.add_parser("show", help="顯示目前設定與設定檔位置")
    show.set_defaults(func=cmd_config_show)

    setter = csub.add_parser("set", help="設定單一欄位")
    setter.add_argument("key", metavar="KEY")
    setter.add_argument("value", metavar="VALUE")
    setter.set_defaults(func=cmd_config_set)

    reset = csub.add_parser("reset", help="還原成預設值")
    reset.set_defaults(func=cmd_config_reset)

    p.set_defaults(func=cmd_config_show, action="show")


# --------------------------------------------------------------------------
# download
# --------------------------------------------------------------------------

def _resolve_single(args: argparse.Namespace) -> bool | None:
    """決定 ``watch?v=…&list=…`` 這類網址要當單曲還是整張清單處理。

    使用者明講就照做；沒講而且確實有歧義時，互動式詢問。無法互動（導向檔案、
    排程執行）則預設只下載單曲——誤抓整張混音清單的代價遠大於漏抓。
    回傳 None 表示使用者在提示中放棄。
    """
    if args.single and args.playlist:
        print("--single 和 --playlist 不能同時使用。", file=sys.stderr)
        return None

    if args.single:
        return True
    if args.playlist:
        return False

    ambiguous = [url for url in args.urls if classify_url(url) == "both"]
    if not ambiguous:
        return False

    if not sys.stdin.isatty():
        print("網址同時含單曲與播放清單，預設只下載單曲（要整張請加 --playlist）。",
              file=sys.stderr)
        return True

    print("\n這個網址同時包含單曲和播放清單：", file=sys.stderr)
    for url in ambiguous[:3]:
        note = "　← 自動混音清單，長度近乎無限" if is_radio_playlist(url) else ""
        print(f"  {url}{note}", file=sys.stderr)
    if len(ambiguous) > 3:
        print(f"  …另外還有 {len(ambiguous) - 3} 個", file=sys.stderr)

    try:
        answer = input("要下載哪個？[1] 只要這一首（預設）　[2] 整張播放清單 > ").strip()
    except EOFError:
        return True
    return answer != "2"


def cmd_download(args: argparse.Namespace) -> int:
    single = _resolve_single(args)
    if single is None:
        return EXIT_USAGE
    return _download_urls(args.urls, args, single=single)


def _build_config(args: argparse.Namespace) -> Config:
    return Config.load().merged(
        output_dir=args.output,
        audio_format=args.audio_format,
        quality=args.quality,
        concurrency=args.jobs,
        playlist_folder=args.playlist_folder,
        convert=False if args.no_convert else None,
        write_tags=False if args.no_tags else None,
        embed_cover=False if args.no_cover else None,
        rename_from_tags=False if args.no_rename else None,
        use_history=False if args.no_history else None,
        filename_template=args.template,
        cookies_file=args.cookies,
        cookies_from_browser=args.cookies_from_browser,
        proxy=args.proxy,
        rate_limit=args.rate_limit,
    )


def _langs(flag: str | None, config: Config) -> str | None:
    """--subs/--lyrics 沒帶語言時，改用設定檔裡的語言清單。"""
    if flag is None:
        return None
    return flag or config.subtitle_langs


def _download_urls(urls: list[str], args: argparse.Namespace, *,
                   single: bool, label: str | None = None,
                   stats: dict | None = None) -> int:
    """download / search / sync 共用的下載流程。

    ``stats`` 若有給，會被填入 ``total`` / ``downloaded``，供 sync 記錄用。
    """
    config = _build_config(args)

    try:
        _require_yt_dlp()
    except DownloadAborted as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_PRECONDITION

    history = History() if config.use_history else None
    # -v 時關掉進度列：yt-dlp 的診斷輸出會跟 ANSI 重繪互相蓋掉。
    reporter = ProgressReporter(
        total=0, enabled=not (args.no_progress or args.verbose)
    )
    downloader = Downloader(config, history=history, reporter=reporter,
                            verbose=args.verbose, video=args.video,
                            subs=_langs(args.subs, config),
                            lyrics=_langs(args.lyrics, config))

    try:
        downloader.preflight()
    except DownloadAborted as exc:
        print(str(exc), file=sys.stderr)
        if history:
            history.close()
        return EXIT_PRECONDITION

    try:
        print(f"正在解析{label or '網址'}…", file=sys.stderr)
        tracks = downloader.expand(urls, single=single)
        if not tracks:
            print("沒有找到可下載的曲目。", file=sys.stderr)
            return EXIT_PRECONDITION

        pending, skipped = downloader.filter_new(tracks, force=args.force)
        if stats is not None:
            stats["total"] = len(tracks)
            stats["downloaded"] = len(pending)
        _print_plan(config, tracks, pending, skipped, video=args.video)

        if args.dry_run:
            for track in pending:
                print(f"  · {track.label}  [{track.video_id}]")
            return EXIT_OK
        if not pending:
            return EXIT_OK

        reporter.total = len(pending)
        with reporter:
            results = downloader.run(pending)
    except KeyboardInterrupt:
        print("\n已中斷。", file=sys.stderr)
        return EXIT_INTERRUPTED
    finally:
        if history:
            history.close()

    return _summarize(results, config)


def _print_plan(config: Config, tracks, pending, skipped, video: str | None = None) -> None:
    if video:
        fmt = "mp4 影片"
        quality = " @ 最佳畫質" if video == "best" else f" @ 最高 {video}p"
    else:
        fmt = config.audio_format if config.convert else "原始音訊"
        quality = "" if not config.convert else f" @ {config.quality}"
    print(
        f"共 {len(tracks)} 首；待下載 {len(pending)} 首"
        + (f"，略過 {len(skipped)} 首（已下載過）" if skipped else ""),
        file=sys.stderr,
    )
    print(f"輸出：{config.output_dir}　格式：{fmt}{quality}　並行：{config.concurrency}",
          file=sys.stderr)


def _summarize(results: list[Result], config: Config) -> int:
    ok = [r for r in results if r.status == "ok"]
    failed = [r for r in results if r.status == "error"]
    warned = [r for r in ok if r.warnings]

    total_bytes = 0
    for result in ok:
        try:
            total_bytes += result.path.stat().st_size if result.path else 0
        except OSError:
            pass

    print(
        f"\n完成 {len(ok)} 首"
        + (f"，失敗 {len(failed)} 首" if failed else "")
        + f"　共 {human_size(total_bytes)}　→ {config.output_dir}",
        file=sys.stderr,
    )
    for result in warned:
        print(f"  ! {result.message}：{result.warnings[0]}", file=sys.stderr)
    for result in failed:
        print(f"  ✖ {result.track.label} — {result.message}", file=sys.stderr)
    if _needs_cookies(failed):
        print(
            "\n提示：403 / 需要登入 / DRM 的影片通常要帶上帳號 cookies 才能下載，"
            "\n      試試 --cookies-from-browser chrome（或 firefox、edge）。",
            file=sys.stderr,
        )

    if failed:
        return EXIT_PARTIAL if ok else EXIT_FAILED
    return EXIT_OK


# --------------------------------------------------------------------------
# search
# --------------------------------------------------------------------------

def cmd_search(args: argparse.Namespace) -> int:
    query = " ".join(args.query).strip()
    if not query:
        print("請給我要搜尋的關鍵字。", file=sys.stderr)
        return EXIT_USAGE

    try:
        _require_yt_dlp()
    except DownloadAborted as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_PRECONDITION

    config = _build_config(args)
    downloader = Downloader(config, verbose=args.verbose)  # 搜尋不需要下載設定
    mode = "歌手" if args.artist else "搜尋"
    where = "" if args.site == "youtube" else f"（{args.site}）"
    print(f"{mode}「{query}」{where}…", file=sys.stderr)
    try:
        # 歌手模式要多撈一些，因為接下來會濾掉非本人頻道的結果。
        results = downloader.search(
            query, limit=args.limit * 3 if args.artist else args.limit,
            site=args.site)
    except DownloadAborted as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_PRECONDITION

    if args.artist:
        narrowed = filter_by_artist(results, query)
        if narrowed:
            results = narrowed[:args.limit]
        else:
            print(f"找不到「{query}」名下的頻道，改用一般搜尋結果。", file=sys.stderr)
            results = results[:args.limit]

    if not results:
        print("找不到結果，換個關鍵字試試。", file=sys.stderr)
        return EXIT_PRECONDITION

    width = max(60, shutil.get_terminal_size((100, 24)).columns - 2)
    print()
    for line in format_results(results, width=width):
        print(line)
    print("\n  ♪ = 官方音源（音質通常最好）　≡ = 超過 15 分鐘，多半是合輯")

    picked = _prompt_selection(results, first_only=args.first)
    if picked is None:
        return EXIT_USAGE
    if not picked:
        print("已取消。", file=sys.stderr)
        return EXIT_OK

    urls = [results[i].url for i in picked]
    return _download_urls(urls, args, single=True, label="選取的曲目")


def _prompt_selection(results, *, first_only: bool) -> list[int] | None:
    """讓使用者挑選搜尋結果；回傳 None 代表輸入有誤，空清單代表取消。"""
    if first_only or not sys.stdin.isatty():
        if not first_only:
            print("\n（非互動環境，自動選第 1 筆）", file=sys.stderr)
        return [0]

    prompt = f"\n要下載哪幾首？[1-{len(results)}／逗號分隔／a 全部／Enter 第一首／q 取消] "
    try:
        answer = input(prompt)
    except EOFError:
        return [0]
    try:
        return parse_selection(answer, len(results))
    except SelectionError as exc:
        print(str(exc), file=sys.stderr)
        return None


# --------------------------------------------------------------------------
# sync
# --------------------------------------------------------------------------

def cmd_sync_add(args: argparse.Namespace) -> int:
    store = Subscriptions()
    try:
        item = store.add(args.url, args.name, output_dir=args.output, video=args.video)
    except SubscriptionError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_USAGE
    print(f"已加入追蹤：{item.name}")
    print(f"  {item.url}")
    print("\n之後只要跑這行就會補上新增的曲目：\n  ytmusic sync")
    return EXIT_OK


def cmd_sync_list(args: argparse.Namespace) -> int:
    store = Subscriptions()
    items = store.list()
    if not items:
        print("還沒有追蹤任何播放清單。\n\n  ytmusic sync add \"<播放清單網址>\"")
        return EXIT_OK
    for item in items:
        when = item.last_sync[:10] if item.last_sync else "從未同步"
        extra = f"　影片 {item.video}" if item.video else ""
        print(f"  {item.name:<12} {when:<12} 上次 {item.last_count:>3} 首{extra}")
        print(f"  {'':<12} {item.url}")
    print(f"\n共 {len(items)} 張（{Subscriptions().path}）")
    return EXIT_OK


def cmd_sync_remove(args: argparse.Namespace) -> int:
    store = Subscriptions()
    if not store.remove(args.name):
        print(f"找不到訂閱：{args.name}", file=sys.stderr)
        return EXIT_PRECONDITION
    print(f"已取消追蹤：{args.name}")
    return EXIT_OK


def cmd_sync_rename(args: argparse.Namespace) -> int:
    store = Subscriptions()
    try:
        item = store.rename(args.old, args.new)
    except SubscriptionError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_USAGE
    print(f"已改名為：{item.name}")
    return EXIT_OK


def cmd_sync_run(args: argparse.Namespace) -> int:
    store = Subscriptions()
    items = store.list()
    if args.names:
        wanted = {n.lower() for n in args.names}
        items = [i for i in items if i.name.lower() in wanted]
        missing = wanted - {i.name.lower() for i in items}
        for name in sorted(missing):
            print(f"找不到訂閱：{name}", file=sys.stderr)
    if not items:
        print("沒有要同步的播放清單。\n\n  ytmusic sync add \"<播放清單網址>\"",
              file=sys.stderr)
        return EXIT_PRECONDITION

    worst = EXIT_OK
    for index, item in enumerate(items, start=1):
        print(f"\n=== [{index}/{len(items)}] {item.name} ===", file=sys.stderr)
        # 訂閱時綁定的設定優先，命令列臨時指定的可覆蓋。
        scoped = argparse.Namespace(**vars(args))
        scoped.output = args.output or item.output_dir
        scoped.video = args.video or item.video
        stats: dict = {}
        code = _download_urls([item.url], scoped, single=False, label=item.name,
                              stats=stats)
        if code == EXIT_OK and not args.dry_run and "total" in stats:
            store.mark_synced(item.name, stats["total"])
        worst = max(worst, code)
    return worst


_COOKIE_HINT_MARKERS = (
    "403", "sign in", "not a bot", "drm", "age", "private video", "members-only",
)


def _needs_cookies(failed: list[Result]) -> bool:
    """判斷失敗原因是否屬於「帶 cookies 就有機會成功」的那一類。"""
    return any(
        marker in result.message.lower()
        for result in failed
        for marker in _COOKIE_HINT_MARKERS
    )


def _require_yt_dlp() -> None:
    try:
        import yt_dlp  # noqa: F401
    except ImportError as exc:
        raise DownloadAborted(
            "找不到 yt-dlp。請先安裝：pip install -r requirements.txt"
            "（或 pip install 'yt-dlp>=2024.1.1' mutagen）"
        ) from exc


# --------------------------------------------------------------------------
# history
# --------------------------------------------------------------------------

def cmd_history_list(args: argparse.Namespace) -> int:
    limit = None if getattr(args, "limit", 20) == 0 else getattr(args, "limit", 20)
    with History() as history:
        entries = history.list(limit=limit)
        total = history.count()
    if not entries:
        print(f"下載歷史是空的（{default_history_path()}）")
        return EXIT_OK

    for entry in entries:
        mark = " " if entry.exists() else "?"
        when = entry.downloaded_at[:10]
        name = f"{entry.artist} - {entry.title}" if entry.artist else entry.title
        print(f"{mark} {when}  {entry.video_id}  {name}")
    print(f"\n顯示 {len(entries)} / {total} 筆（? 表示檔案已不在原路徑）")
    return EXIT_OK


def cmd_history_remove(args: argparse.Namespace) -> int:
    removed = 0
    with History() as history:
        for video_id in args.video_ids:
            if history.remove(video_id):
                removed += 1
            else:
                print(f"找不到紀錄：{video_id}", file=sys.stderr)
    print(f"已移除 {removed} 筆紀錄。")
    return EXIT_OK if removed else EXIT_PRECONDITION


def cmd_history_prune(args: argparse.Namespace) -> int:
    with History() as history:
        stale = history.prune()
    for entry in stale:
        print(f"移除 {entry.video_id}  {entry.title}")
    print(f"已清理 {len(stale)} 筆失效紀錄。")
    return EXIT_OK


def cmd_history_clear(args: argparse.Namespace) -> int:
    if not args.yes:
        answer = input("確定要清空全部下載歷史嗎？[y/N] ").strip().lower()
        if answer not in {"y", "yes"}:
            print("已取消。")
            return EXIT_OK
    with History() as history:
        count = history.clear()
    print(f"已清空 {count} 筆紀錄。")
    return EXIT_OK


# --------------------------------------------------------------------------
# config
# --------------------------------------------------------------------------

def cmd_config_show(args: argparse.Namespace) -> int:
    config = Config.load()
    print(f"設定檔：{Config.path()}"
          + ("" if Config.path().exists() else "（尚未建立，顯示的是預設值）"))
    print(f"歷史資料庫：{default_history_path()}\n")
    for key, value in config.to_dict().items():
        print(f"  {key:<22} {value}")
    return EXIT_OK


def cmd_config_set(args: argparse.Namespace) -> int:
    config = Config.load()
    try:
        value = coerce_value(args.key, args.value)
    except KeyError:
        valid = ", ".join(f.name for f in fields(Config))
        print(f"未知的設定項 {args.key!r}。可用：{valid}", file=sys.stderr)
        return EXIT_USAGE
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_USAGE

    if args.key == "output_dir":
        value = str(Path(value).expanduser())

    # 直接改 dict 而非 merged()，因為 merged() 會忽略 None（無法清空選填欄位）。
    data = config.to_dict()
    data[args.key] = value
    updated = Config.from_dict(data)
    problems = updated.validate()
    if problems:
        print("；".join(problems), file=sys.stderr)
        return EXIT_USAGE

    path = updated.save()
    print(f"已設定 {args.key} = {updated.to_dict()[args.key]}（{path}）")
    return EXIT_OK


def cmd_config_reset(args: argparse.Namespace) -> int:
    path = Config().save()
    print(f"已還原預設設定（{path}）")
    return EXIT_OK


# --------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return EXIT_USAGE
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n已中斷。", file=sys.stderr)
        return EXIT_INTERRUPTED


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
