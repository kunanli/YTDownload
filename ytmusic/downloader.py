"""下載流程核心：展開播放清單、平行下載、轉檔與標籤寫入。"""

from __future__ import annotations

import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

from .config import Config
from .history import History
from .progress import ProgressReporter
from .search import SearchResult, parse_results
from .tagger import (
    TaggingError, TrackMeta, apply_tags, build_metadata, fetch_cover,
    pick_thumbnail_url,
)
from .utils import (
    FFMPEG_HINT, find_ffmpeg, parse_browser_spec, sanitize_filename,
    strip_ansi, vimeo_player_url,
)

# mp3 的 preferredquality 若小於 10 會被當成 VBR 等級，0 代表最佳。
_BEST_VBR = "0"

# 各站台的搜尋前綴（yt-dlp 內建）。
SEARCH_PREFIXES = {"youtube": "ytsearch", "bilibili": "bilisearch"}


@dataclass
class Track:
    """待下載的單一曲目。"""

    video_id: str
    url: str
    title: str
    playlist_title: str | None = None
    playlist_index: int | None = None
    playlist_count: int | None = None

    @property
    def label(self) -> str:
        return self.title or self.video_id


@dataclass
class Result:
    track: Track
    status: str  # ok | skipped | error
    path: Path | None = None
    message: str = ""
    warnings: list[str] = field(default_factory=list)


class DownloadAborted(RuntimeError):
    """使用者中斷或前置條件不足時拋出。"""


class _CollectingLogger:
    """吞掉 yt-dlp 的一般輸出，只保留錯誤訊息供事後回報。"""

    def __init__(self) -> None:
        self.errors: list[str] = []

    def debug(self, msg: str) -> None:  # pragma: no cover - yt-dlp 介面
        pass

    def info(self, msg: str) -> None:  # pragma: no cover - yt-dlp 介面
        pass

    def warning(self, msg: str) -> None:  # pragma: no cover - yt-dlp 介面
        pass

    def error(self, msg: str) -> None:
        self.errors.append(str(msg).strip())


class Downloader:
    """把一串網址變成硬碟上帶好標籤的音樂檔。"""

    def __init__(self, config: Config, history: History | None = None,
                 reporter: ProgressReporter | None = None,
                 verbose: bool = False, video: str | None = None,
                 subs: str | None = None, lyrics: str | None = None) -> None:
        self.config = config
        self.history = history
        self.reporter = reporter
        self.verbose = verbose
        # None 代表只要音訊；否則是影片最高解析度（"best" 或像 "1080" 的數字）。
        self.video = video
        self.subs = subs
        self.lyrics = lyrics
        # 使用者明確指定要假扮瀏覽器時，一開始就用；沒指定則只在連線失敗後才試。
        self.impersonate = config.impersonate
        self._stop = threading.Event()

    # -- 前置檢查 ---------------------------------------------------------

    def preflight(self) -> None:
        problems = self.config.validate()
        if problems:
            raise DownloadAborted("；".join(problems))
        if self.video and not find_ffmpeg():
            raise DownloadAborted(
                "下載影片需要 ffmpeg 才能把畫面和聲音合併成 mp4。\n" + FFMPEG_HINT
            )
        if self.config.convert and not self.video and not find_ffmpeg():
            raise DownloadAborted(FFMPEG_HINT)
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

    def cancel(self) -> None:
        self._stop.set()

    def _retry_network(self, opts: dict, url: str,
                       failure: Exception) -> tuple[dict | None, Exception]:
        """連線被切斷時，依序換條件重試。回傳 (結果, 最後一次的錯誤)。

        兩招針對的是不同病因，所以先後有別：IPv4 治的是路由半通不通，
        假扮瀏覽器治的是對方看 TLS 指紋擋人——後者要裝東西，所以擺後面。
        """
        attempts: list[tuple[str, callable]] = [
            ("改用 IPv4", lambda: _extract_over_ipv4(opts, url)),
        ]
        if not self.impersonate and impersonation_available():
            attempts.append(("假扮成瀏覽器的 TLS 指紋",
                             lambda: _extract_impersonating(opts, url)))

        for label, attempt in attempts:
            self._log(f"  連線被中斷，{label}，再試一次…")
            try:
                info = attempt()
            except Exception as exc:
                failure = exc
                if not _is_network_error(exc):
                    break  # 換了條件之後變成別的錯，再重試也沒意義
                continue
            if info is not None:
                return info, failure
        return None, failure

    # -- 展開網址 ---------------------------------------------------------

    def expand(self, urls: list[str], single: bool = False) -> list[Track]:
        """把播放清單／頻道網址攤平成曲目清單，並依影片 ID 去重。

        ``single`` 為真時，``watch?v=…&list=…`` 這種同時指向單曲與清單的網址
        只取那一首；純播放清單網址不受影響，仍會完整展開。
        """
        from yt_dlp import YoutubeDL

        # extract_flat="in_playlist" 只攤平清單內的影片，頻道底下的分頁清單仍會
        # 被解析，所以這裡保留 yt-dlp 的預設處理流程（process=True）。
        logger = _CollectingLogger()
        opts = self._base_opts()
        opts.update({
            "extract_flat": "in_playlist",
            "skip_download": True,
            "noplaylist": single,
        })
        if not self.verbose:
            # 攔下 yt-dlp 的錯誤輸出，改由我們統一格式化，避免同一則訊息印兩次。
            opts["logger"] = logger

        tracks: list[Track] = []
        seen: set[str] = set()
        with YoutubeDL(opts) as ydl:
            for url in urls:
                info = None
                try:
                    info = ydl.extract_info(url, download=False)
                except Exception as exc:
                    failure: Exception = exc
                    fallback = _fallback_url(url, exc)
                    if fallback:
                        try:
                            info = ydl.extract_info(fallback, download=False)
                        except Exception as retry_exc:
                            failure = retry_exc
                    if info is None and _is_network_error(failure):
                        info, failure = self._retry_network(opts, fallback or url,
                                                            failure)
                    if info is None:
                        self._log(f"✖ 無法讀取 {url}：{_short_error(failure, logger)}")
                        if _is_network_error(failure):
                            self._log(NETWORK_HINT)
                            if not self.impersonate and not impersonation_available():
                                self._log(IMPERSONATE_HINT)
                        continue
                if info is None:
                    self._log(f"✖ 無法讀取 {url}")
                    continue
                for track in _walk(info):
                    if track.video_id in seen:
                        continue
                    seen.add(track.video_id)
                    tracks.append(track)
        return tracks

    def search(self, query: str, limit: int = 8,
               site: str = "youtube") -> list[SearchResult]:
        """用關鍵字搜尋，回傳候選曲目（不下載）。

        ``site`` 決定用哪個站台的搜尋前綴；yt-dlp 對每個站台的搜尋各有一組。
        """
        from yt_dlp import YoutubeDL

        limit = max(1, min(limit, 50))
        logger = _CollectingLogger()
        opts = self._base_opts()
        opts.update({"extract_flat": True, "skip_download": True})
        if not self.verbose:
            opts["logger"] = logger

        with YoutubeDL(opts) as ydl:
            try:
                prefix = SEARCH_PREFIXES.get(site, SEARCH_PREFIXES["youtube"])
                info = ydl.extract_info(f"{prefix}{limit}:{query}", download=False)
            except Exception as exc:
                raise DownloadAborted(f"搜尋失敗：{_short_error(exc, logger)}") from exc
        return parse_results(info)

    def filter_new(self, tracks: list[Track], force: bool = False) -> tuple[list[Track], list[Track]]:
        """依下載歷史把曲目分成「要下載」與「已下載可略過」兩堆。"""
        if force or not self.config.use_history or self.history is None:
            return tracks, []
        known = self.history.known_ids([t.video_id for t in tracks])
        pending = [t for t in tracks if t.video_id not in known]
        skipped = [t for t in tracks if t.video_id in known]
        return pending, skipped

    # -- 執行 -------------------------------------------------------------

    def run(self, tracks: list[Track]) -> list[Result]:
        """平行下載所有曲目，回傳與輸入順序無關的結果清單。"""
        if not tracks:
            return []
        workers = min(self.config.concurrency, len(tracks))
        results: list[Result] = []
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="ytmusic") as pool:
            futures = {pool.submit(self._download_one, t): t for t in tracks}
            try:
                for future in as_completed(futures):
                    results.append(future.result())
            except KeyboardInterrupt:
                self.cancel()
                for future in futures:
                    future.cancel()
                raise
        return results

    # -- 單曲下載 ---------------------------------------------------------

    def _download_one(self, track: Track) -> Result:
        from yt_dlp import YoutubeDL
        from yt_dlp.utils import DownloadError

        if self._stop.is_set():
            return Result(track, "error", message="已取消")

        logger = _CollectingLogger()
        opts = self._download_opts(track, logger)

        if self.reporter:
            self.reporter.start(track.video_id, track.label)
        subtitle_warning: str | None = None
        try:
            try:
                info = _fetch(opts, track.url)
            except Exception as exc:
                # 字幕是加分項，不該讓整首歌下載失敗（缺該語言、被限流都可能）。
                if not (self.subs or self.lyrics) or not _is_subtitle_error(exc):
                    raise
                subtitle_warning = f"字幕抓不到（{_short_error(exc, logger)}），只下載了音訊"
                info = _fetch(self._without_subtitles(opts), track.url)

            if info is None:
                raise DownloadError("yt-dlp 沒有回傳任何資訊")
            path = _final_path(info)
            if path is None or not path.is_file():
                raise DownloadError("下載結束但找不到輸出檔案")
        except KeyboardInterrupt:
            self._stop.set()
            if self.reporter:
                self.reporter.finish(track.video_id, "error", f"{track.label} — 已取消")
            return Result(track, "error", message="已取消")
        except Exception as exc:
            message = _short_error(exc, logger)
            if self.reporter:
                self.reporter.finish(track.video_id, "error", f"{track.label} — {message}")
            return Result(track, "error", message=message)

        warnings: list[str] = [subtitle_warning] if subtitle_warning else []
        meta = build_metadata(
            info,
            playlist_title=track.playlist_title,
            playlist_index=track.playlist_index,
            playlist_count=track.playlist_count,
        )

        if self.config.write_tags:
            if self.reporter:
                self.reporter.update(track.video_id, stage="寫入標籤", percent=100.0)
            cover = self._maybe_cover(info)
            try:
                apply_tags(path, meta, cover)
            except TaggingError as exc:
                warnings.append(str(exc))

        downloaded_path = path  # 字幕檔是照這個名字存的，改名後要用它來找
        if self.config.rename_from_tags:
            # yt-dlp 的樣板只看得到原始欄位，檔名會留著 "(Official Video)" 這類雜訊，
            # 也常把演出者重複兩次；這裡改用整理過的中繼資料重新命名。
            path = _rename_from_meta(
                path, meta,
                number=self.config.playlist_folder,
                replaceable=self._previous_path(track.video_id),
            ) or path

        if self.lyrics and not self.video and not subtitle_warning:
            note = self._write_lyrics(path, meta, source=downloaded_path)
            if note:
                warnings.append(note)

        self._record(track, meta, path, info)

        if self.reporter:
            suffix = f"（{warnings[0]}）" if warnings else ""
            self.reporter.finish(track.video_id, "ok", f"{meta.as_display()}{suffix}")
        return Result(track, "ok", path=path, message=meta.as_display(), warnings=warnings)

    def _maybe_cover(self, info: dict) -> bytes | None:
        if not self.config.embed_cover:
            return None
        url = pick_thumbnail_url(info)
        if not url:
            return None
        return fetch_cover(url, square=self.config.square_cover)

    def _write_lyrics(self, path: Path, meta: TrackMeta,
                      source: Path | None = None) -> str | None:
        """把 yt-dlp 抓下來的字幕轉成 .lrc 並寫進標籤，回傳警告訊息或 None。

        ``source`` 是改名前的檔案路徑：字幕檔是照 yt-dlp 的原始檔名存的，
        改名後就對不上了，所以要用原本的名字去找。
        """
        from .lyrics import (
            embed_lyrics, find_subtitle_files, read_subtitle, to_lrc, to_plain,
        )

        from .lyrics import normalise_languages

        subtitle_files = find_subtitle_files(
            source or path, normalise_languages(self.lyrics or ""))
        if not subtitle_files:
            return "沒有字幕可轉成歌詞"

        cues = read_subtitle(subtitle_files[0])
        if not cues:
            return "字幕是空的"

        lrc_path = path.with_suffix(".lrc")
        try:
            lrc_path.write_text(
                to_lrc(cues, title=meta.title, artist=meta.artist, album=meta.album),
                encoding="utf-8",
            )
        except OSError as exc:
            return f"寫入 .lrc 失敗：{exc}"

        embed_lyrics(path, to_plain(cues))
        for item in subtitle_files:  # 字幕檔已轉成 .lrc，不用留著
            try:
                item.unlink()
            except OSError:
                pass
        return None

    def _previous_path(self, video_id: str) -> Path | None:
        """同一支影片上次下載到的位置（重下時用來覆寫自己而非產生副本）。"""
        if self.history is None or not self.config.use_history:
            return None
        entry = self.history.get(video_id)
        return entry.path if entry and entry.filepath else None

    def _record(self, track: Track, meta: TrackMeta, path: Path, info: dict) -> None:
        if not self.config.use_history or self.history is None:
            return
        try:
            size = path.stat().st_size
        except OSError:
            size = 0
        self.history.add(
            track.video_id,
            title=meta.title,
            artist=meta.artist,
            album=meta.album,
            url=info.get("webpage_url") or track.url,
            filepath=path,
            audio_format=path.suffix.lstrip("."),
            filesize=size,
        )

    # -- yt-dlp 選項 ------------------------------------------------------

    def _base_opts(self) -> dict:
        opts: dict = {
            "quiet": not self.verbose,
            "no_warnings": not self.verbose,
            "verbose": self.verbose,
            "noprogress": True,
            "consoletitle": False,
            "ignoreerrors": False,
            "retries": 5,
            "fragment_retries": 5,
            "socket_timeout": 30,
        }
        if self.config.proxy:
            opts["proxy"] = self.config.proxy
        if self.impersonate:
            opts["impersonate"] = impersonate_target(self.impersonate)
        if self.config.cookies_file:
            opts["cookiefile"] = str(Path(self.config.cookies_file).expanduser())
        if self.config.cookies_from_browser:
            opts["cookiesfrombrowser"] = parse_browser_spec(self.config.cookies_from_browser)
        if self.config.rate_limit:
            limit = _parse_rate(self.config.rate_limit)
            if limit:
                opts["ratelimit"] = limit
        return opts

    def _download_opts(self, track: Track, logger: _CollectingLogger) -> dict:
        opts = self._base_opts()
        opts.update({
            "format": self._format_selector(),
            "noplaylist": True,
            "outtmpl": {"default": self._outtmpl(track)},
            "postprocessors": self._postprocessors(),
            "progress_hooks": [lambda d: self._on_progress(track.video_id, d)],
            "postprocessor_hooks": [lambda d: self._on_postprocess(track.video_id, d)],
            "overwrites": True,
            "windowsfilenames": True,
            "trim_file_name": 150,
        })
        opts.update(self._subtitle_opts())
        if self.video:
            # 高畫質的影音是分開的串流，合併時統一輸出成相容性最好的 mp4。
            opts["merge_output_format"] = "mp4"
        if not self.verbose:  # -v 時讓 yt-dlp 直接印出完整診斷訊息
            opts["logger"] = logger
        return opts

    def _format_selector(self) -> str:
        """依模式挑選 yt-dlp 的 format 字串。"""
        if not self.video:
            return "bestaudio/best"
        cap = "" if self.video == "best" else f"[height<=?{self.video}]"
        # 優先挑 H.264 + AAC。YouTube 現在多半優先給 AV1／Opus，檔案是比較小，
        # 但 Windows 內建播放器、舊手機和多數剪輯軟體都放不動；挑不到才退回任意編碼。
        return (
            f"bestvideo[vcodec^=avc1]{cap}+bestaudio[acodec^=mp4a]"
            f"/bestvideo{cap}+bestaudio"
            f"/best{cap}"
            "/best"
        )

    @staticmethod
    def _without_subtitles(opts: dict) -> dict:
        """複製一份拿掉所有字幕相關設定的選項，用於重試。"""
        retry = dict(opts)
        for key in ("writesubtitles", "writeautomaticsub", "subtitleslangs",
                    "subtitlesformat"):
            retry.pop(key, None)
        retry["postprocessors"] = [
            pp for pp in retry.get("postprocessors") or []
            if "Subtitle" not in pp.get("key", "")
        ]
        return retry

    def _subtitle_opts(self) -> dict:
        """字幕下載設定。影片會把字幕燒進 mp4，音訊則留下字幕檔供轉成歌詞。"""
        from .lyrics import normalise_languages

        spec = self.subs or self.lyrics
        if not spec:
            return {}
        langs = normalise_languages(spec)
        if not langs:
            return {}
        opts: dict = {
            "writesubtitles": True,
            # 官方音源常常沒有人工字幕，自動字幕總比沒有好。
            "writeautomaticsub": True,
            "subtitleslangs": langs,
            "subtitlesformat": "srt/vtt/best",
        }
        return opts

    def _postprocessors(self) -> list[dict]:
        steps: list[dict] = []

        if self.video:
            if self.subs:
                # 統一轉成 srt 再燒進 mp4，播放器可自行開關字幕。
                steps.append({"key": "FFmpegSubtitlesConvertor", "format": "srt"})
                steps.append({"key": "FFmpegEmbedSubtitle"})
            return steps

        if self.config.convert:
            quality = _BEST_VBR if self.config.quality == "best" else self.config.quality
            steps.append({
                "key": "FFmpegExtractAudio",
                "preferredcodec": self.config.audio_format,
                "preferredquality": quality,
            })
        if self.lyrics:
            # 轉成 srt，稍後由 lyrics.py 解析成 LRC。
            steps.append({"key": "FFmpegSubtitlesConvertor", "format": "srt"})
        return steps

    def _outtmpl(self, track: Track) -> str:
        root = self.config.output_dir
        if self.config.playlist_folder and track.playlist_title:
            root = root / sanitize_filename(track.playlist_title)
            root.mkdir(parents=True, exist_ok=True)
        return str(root / self.config.filename_template)

    # -- 回呼 -------------------------------------------------------------

    def _on_progress(self, key: str, data: dict) -> None:
        if self._stop.is_set():
            raise KeyboardInterrupt
        if self.reporter is None or data.get("status") != "downloading":
            return
        total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
        downloaded = data.get("downloaded_bytes") or 0
        percent = (downloaded / total * 100) if total else 0.0
        self.reporter.update(
            key,
            percent=percent,
            speed=data.get("speed"),
            eta=data.get("eta"),
            stage="下載中",
        )

    def _on_postprocess(self, key: str, data: dict) -> None:
        if self.reporter is None or data.get("status") != "started":
            return
        name = data.get("postprocessor") or ""
        stage = "轉檔中" if "ExtractAudio" in name else "處理中"
        self.reporter.update(key, percent=100.0, speed=None, eta=None, stage=stage)

    def _log(self, message: str) -> None:
        if self.reporter:
            self.reporter.log(message)


# --------------------------------------------------------------------------
# 輔助函式
# --------------------------------------------------------------------------

def _walk(info: dict, playlist_title: str | None = None,
          playlist_count: int | None = None) -> list[Track]:
    """遞迴走訪 yt-dlp 的 info 樹，攤平成 Track 清單。"""
    if info.get("_type") in {"playlist", "multi_video"}:
        title = info.get("title") or playlist_title
        entries = info.get("entries") or []
        entries = list(entries)  # entries 可能是產生器
        count = info.get("playlist_count") or len(entries)
        tracks: list[Track] = []
        for index, entry in enumerate(entries, start=1):
            if not entry:
                continue
            children = _walk(entry, playlist_title=title, playlist_count=count)
            for child in children:
                if child.playlist_index is None:
                    child.playlist_index = index
            tracks.extend(children)
        return tracks

    video_id = info.get("id")
    if not video_id:
        return []
    # 未展開的巢狀清單參照（YoutubeTab、YoutubePlaylist 等）不是曲目，直接略過。
    if info.get("_type") == "url":
        ie_key = str(info.get("ie_key") or "").lower()
        if any(token in ie_key for token in ("playlist", "tab", "channel", "user")):
            return []
    url = (
        info.get("webpage_url")
        or info.get("original_url")
        or info.get("url")
        or f"https://www.youtube.com/watch?v={video_id}"
    )
    return [Track(
        video_id=str(video_id),
        url=url,
        title=info.get("title") or str(video_id),
        playlist_title=playlist_title,
        playlist_count=playlist_count,
    )]


def _rename_from_meta(path: Path, meta: TrackMeta, *, number: bool = False,
                      replaceable: Path | None = None) -> Path | None:
    """依中繼資料把檔案改名成「演出者 - 歌名」，失敗時回傳 None 保留原檔名。"""
    if not meta.title:
        return None
    stem = f"{meta.artist} - {meta.title}" if meta.artist else meta.title
    if number and meta.track_number:
        # 專輯／清單資料夾裡加上曲序，檔案總管排序才會對。
        stem = f"{meta.track_number:02d} - {stem}"
    stem = sanitize_filename(stem)
    if stem == "untitled":
        return None

    target = path.with_name(stem + path.suffix)
    if target == path:  # 名字已經對了，別讓 _unique_path 誤加 (2)
        return path
    target = _unique_path(target, replaceable)
    try:
        path.replace(target)
    except OSError:
        return None
    return target


def _unique_path(target: Path, replaceable: Path | None = None) -> Path:
    """在檔名後加 (2)、(3)… 直到不與既有檔案衝突。

    ``replaceable`` 是同一支影片上次下載的檔案；覆寫自己不算衝突，否則重下同一首歌
    會不斷產生 (2)、(3)。
    """
    if not target.exists():
        return target
    if replaceable is not None and target == replaceable:
        return target
    for index in range(2, 1000):
        candidate = target.with_name(f"{target.stem} ({index}){target.suffix}")
        if not candidate.exists():
            return candidate
    return target


def _final_path(info: dict) -> Path | None:
    """從 info dict 找出後處理完成後的實際檔案路徑。"""
    for entry in info.get("requested_downloads") or []:
        path = entry.get("filepath") or entry.get("_filename")
        if path:
            return Path(path)
    path = info.get("filepath") or info.get("_filename")
    return Path(path) if path else None


def _parse_rate(value: str) -> int | None:
    """把 "500K"、"1.5M" 之類的限速字串轉成每秒位元組數。"""
    text = value.strip().upper().rstrip("B")
    if not text:
        return None
    multiplier = 1
    if text[-1] in {"K", "M", "G"}:
        multiplier = {"K": 1024, "M": 1024 ** 2, "G": 1024 ** 3}[text[-1]]
        text = text[:-1]
    try:
        return int(float(text) * multiplier)
    except ValueError:
        return None


_SUBTITLE_ERROR_MARKERS = ("subtitle", "字幕")


def _fallback_url(url: str, exc: Exception) -> str | None:
    """某些站台換條路就能通，這裡回傳可以重試的替代網址。

    目前只處理 Vimeo：一般頁面要先換 OAuth token，部分網路環境會被回 401，
    改用播放器網址就不必經過那道手續。
    """
    message = str(exc).lower()
    if "vimeo" in message and ("oauth" in message or "401" in message):
        return vimeo_player_url(url)
    return None


def _is_subtitle_error(exc: Exception) -> bool:
    """判斷這個失敗是不是只跟字幕有關（音訊本身其實抓得到）。"""
    message = str(exc).lower()
    return any(marker in message for marker in _SUBTITLE_ERROR_MARKERS)


def _fetch(opts: dict, url: str):
    from yt_dlp import YoutubeDL

    with YoutubeDL(opts) as ydl:
        return ydl.extract_info(url, download=True)


def _clean_error_text(raw: str) -> str:
    """去掉 yt-dlp 錯誤訊息的前綴與冗長的補充說明。

    第一步一定要先清掉顏色碼：yt-dlp 的錯誤在支援顏色的終端機上長得像
    ``\\x1b[0;31mERROR:\\x1b[0m …``，而下面的切割條件裡就有 ``;``——不先清掉的話
    整句會被切成 ``\\x1b[0``，印出去被終端機當成未完成的控制序列吃掉，
    使用者看到的就是「無法讀取 <網址>：」後面一片空白。
    """
    message = strip_ansi(raw).strip()
    message = re.sub(r"^\s*(ERROR|WARNING)\s*:\s*", "", message).strip()
    for marker in (";", " Please report", "\n"):
        if marker in message:
            head = message.split(marker)[0].strip()
            if head:  # 切完若整句沒了就保留原文，別留下一片空白
                message = head
    return message[:200]


# 連不上、連到一半被切斷的特徵。這類失敗跟網址、跟 yt-dlp 版本都無關，
# 給的建議也完全不同——不該跟「這支影片不能下載」混在一起。
_NETWORK_MARKERS = (
    "ssl", "eof occurred", "handshake", "connection reset", "connection aborted",
    "connection refused", "timed out", "timeout", "temporary failure in name resolution",
    "name or service not known", "network is unreachable", "getaddrinfo",
    "remote end closed connection",
)

NETWORK_HINT = """  這是連線的問題，不是那支影片的問題——連到一半被切斷了。依序試：
    1. 直接再跑一次（這種斷線常常是暫時的）
    2. 短網址（lnkd.in、bit.ly…）換成完整網址：在瀏覽器開啟後複製網址列
    3. 暫時關掉防毒軟體的「HTTPS／SSL 掃描」——它會拆開 TLS，常造成這個錯誤
    4. 關掉 VPN／Proxy，或反過來用 --proxy 指定一個
    5. 換個網路（手機熱點）"""


def _is_network_error(exc: BaseException) -> bool:
    """判斷失敗是不是卡在連線，而不是內容本身。"""
    from .utils import strip_ansi

    message = strip_ansi(str(exc)).lower()
    return any(marker in message for marker in _NETWORK_MARKERS)


# curl_cffi 的版本區間是 yt-dlp 寫死的：不在區間內時 yt-dlp 只會說「target
# 不可用」，完全不提版本，很難查。所以提示一定要把版本範圍寫進去。
CURL_CFFI_SPEC = "curl_cffi>=0.10,<0.16"

IMPERSONATE_HINT = f"""  想再試一招：**假扮成瀏覽器的 TLS 指紋**。

  有些站台（LinkedIn 是其中之一）會依 TLS 握手的特徵判斷對方是不是瀏覽器，
  不像就直接把連線切斷——症狀正是 UNEXPECTED_EOF / Connection reset。
  瀏覽器打得開、程式打不開，多半就是這個。

  安裝（版本範圍不能省，裝到太新的 yt-dlp 會說「target 不可用」）：
    python -m pip install "{CURL_CFFI_SPEC}"

  裝好後重跑就會自動用上，也可以自己指定：
    python -m ytmusic dl "網址" --impersonate chrome"""


def impersonate_target(name: str = "chrome"):
    """把 `chrome`、`chrome-136` 這種字串轉成 yt-dlp 的 ImpersonateTarget。"""
    try:
        from yt_dlp.networking.impersonate import ImpersonateTarget

        return ImpersonateTarget.from_str(name)
    except Exception:
        return None


def impersonation_available() -> bool:
    """有沒有裝好可用的 curl_cffi。

    只看 `import curl_cffi` 不夠——yt-dlp 對版本有硬性區間，裝了太新的一樣不能用。
    """
    try:
        from yt_dlp.networking._curlcffi import CurlCFFIRH  # noqa: F401
        import curl_cffi

        return "unsupported" not in getattr(curl_cffi, "_yt_dlp__version", "")
    except Exception:
        return False


def _extract_impersonating(opts: dict, url: str, target: str = "chrome"):
    """假扮瀏覽器的 TLS 指紋再解析一次。"""
    from yt_dlp import YoutubeDL

    retry_opts = dict(opts)
    retry_opts["impersonate"] = impersonate_target(target)
    with YoutubeDL(retry_opts) as ydl:
        return ydl.extract_info(url, download=False)


def _extract_over_ipv4(opts: dict, url: str):
    """強制走 IPv4 再解析一次（等同 yt-dlp 的 -4）。

    IPv6 路由半通不通、或中間設備只擋 IPv6 時，症狀就是連線被無故切斷；
    這時改走 IPv4 往往直接就過了。
    """
    from yt_dlp import YoutubeDL

    retry_opts = dict(opts)
    retry_opts["source_address"] = "0.0.0.0"
    with YoutubeDL(retry_opts) as ydl:
        return ydl.extract_info(url, download=False)


# 短於這個長度的訊息幾乎無法判斷原因，補上例外型別才有線索。
_UNINFORMATIVE_LENGTH = 12


def _short_error(exc: Exception, logger: _CollectingLogger | None = None) -> str:
    """把錯誤壓成一行；確保永遠有內容可顯示。

    某些情況下例外本身沒有訊息（yt-dlp 已經把細節送去 logger 了），此時改用
    logger 收到的最後一則錯誤。訊息短到無法判斷原因時補上例外型別——曾發生
    使用者看到「無法讀取 <網址>：」後面一片空白，完全無從查起。
    """
    message = _clean_error_text(str(exc))
    if len(message) < _UNINFORMATIVE_LENGTH and logger is not None and logger.errors:
        message = _clean_error_text(logger.errors[-1]) or message
    if len(message) < _UNINFORMATIVE_LENGTH:
        kind = type(exc).__name__
        message = f"{message} [{kind}]".strip() if message else f"{kind}（沒有訊息）"
    return message
