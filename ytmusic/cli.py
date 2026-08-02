"""ytmusic 的命令列進入點。"""

from __future__ import annotations

import argparse
import sys
from dataclasses import fields
from pathlib import Path

from . import __version__
from .config import AUDIO_FORMATS, QUALITIES, Config, coerce_value
from .downloader import DownloadAborted, Downloader, Result, Track
from .history import History, default_history_path
from .progress import ProgressReporter
from .utils import human_size

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
        description="YouTube 音樂下載器：下載音訊、轉檔、寫入標籤與封面，並記錄下載歷史。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "範例：\n"
            "  ytmusic dl https://youtu.be/XXXXXXXXXXX\n"
            "  ytmusic dl <播放清單網址> -f mp3 -q 320 -j 4 --playlist-folder\n"
            "  ytmusic history list\n"
            "  ytmusic config set output_dir ~/Music/YT\n"
        ),
    )
    parser.add_argument("-V", "--version", action="version", version=f"ytmusic {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    _add_download_parser(sub)
    _add_history_parser(sub)
    _add_config_parser(sub)
    return parser


def _add_download_parser(sub) -> None:
    p = sub.add_parser(
        "download", aliases=["dl"], help="下載一或多個影片／播放清單的音訊",
        description="下載音訊並轉檔、寫標籤，已下載過的影片預設會自動略過。",
    )
    p.add_argument("urls", nargs="+", metavar="URL", help="影片、播放清單或頻道網址")
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
    p.add_argument("--dry-run", action="store_true", help="只列出將要下載的曲目，不實際下載")
    p.add_argument("--template", metavar="TMPL", help="yt-dlp 檔名樣板，需包含 %%(ext)s")
    p.add_argument("--cookies", metavar="FILE", help="cookies.txt 路徑（用於年齡限制／會員內容）")
    p.add_argument("--cookies-from-browser", metavar="BROWSER",
                   help="從瀏覽器讀取 cookies，例如 chrome、firefox、edge")
    p.add_argument("--proxy", metavar="URL", help="HTTP/SOCKS 代理伺服器")
    p.add_argument("--rate-limit", metavar="RATE", help="限速，例如 500K、1.5M")
    p.add_argument("--no-progress", action="store_true", help="關閉進度列，只輸出純文字")
    p.add_argument("-v", "--verbose", action="store_true",
                   help="印出 yt-dlp 的完整診斷輸出，用來查明失敗原因")
    p.set_defaults(func=cmd_download)


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

def cmd_download(args: argparse.Namespace) -> int:
    config = Config.load().merged(
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
                            verbose=args.verbose)

    try:
        downloader.preflight()
    except DownloadAborted as exc:
        print(str(exc), file=sys.stderr)
        if history:
            history.close()
        return EXIT_PRECONDITION

    try:
        print("正在解析網址…", file=sys.stderr)
        tracks = downloader.expand(args.urls)
        if not tracks:
            print("沒有找到可下載的曲目。", file=sys.stderr)
            return EXIT_PRECONDITION

        pending, skipped = downloader.filter_new(tracks, force=args.force)
        _print_plan(config, tracks, pending, skipped)

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


def _print_plan(config: Config, tracks, pending, skipped) -> None:
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
