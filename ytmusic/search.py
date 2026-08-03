"""關鍵字搜尋的結果解析、顯示與選擇。

真正發出搜尋請求的是 ``Downloader.search()``（它才有 cookies、proxy 等設定）；
這裡只處理不需要網路的部分，方便測試。
"""

from __future__ import annotations

from dataclasses import dataclass

from .utils import human_time, pad_display, strip_topic, truncate

LONG_SECONDS = 15 * 60


@dataclass
class SearchResult:
    video_id: str
    title: str
    uploader: str
    duration: float | None
    url: str

    @property
    def is_official_audio(self) -> bool:
        """YouTube Music 自動產生的「Artist - Topic」頻道＝官方音源。"""
        return self.uploader.strip().lower().endswith("- topic")

    @property
    def is_long(self) -> bool:
        """超過 15 分鐘的多半是合輯或演唱會全場，不是單曲。"""
        return bool(self.duration and self.duration > LONG_SECONDS)

    @property
    def channel(self) -> str:
        return strip_topic(self.uploader) or self.uploader


def parse_results(info: dict | None) -> list[SearchResult]:
    """把 yt-dlp 的搜尋結果轉成 SearchResult 清單。

    YouTube 的搜尋結果裡會混進頻道與播放清單，它們沒有長度、選下去會把整個
    頻道抓下來，所以在這裡就濾掉，只留真正的影片。
    """
    if not info:
        return []
    results: list[SearchResult] = []
    for entry in info.get("entries") or []:
        if not entry:
            continue
        video_id = entry.get("id")
        if not video_id or not _is_video(entry):
            continue
        results.append(SearchResult(
            video_id=str(video_id),
            title=entry.get("title") or str(video_id),
            uploader=entry.get("uploader") or entry.get("channel") or "",
            duration=entry.get("duration"),
            url=(entry.get("url") or entry.get("webpage_url")
                 or f"https://www.youtube.com/watch?v={video_id}"),
        ))
    return results


CHANNEL_WIDTH = 20
DURATION_WIDTH = 6

# 非影片的搜尋結果（頻道、播放清單分頁）在 ie_key 裡都帶這些字。
_NON_VIDEO_IE_KEYS = ("tab", "playlist", "channel", "user")


def _is_video(entry: dict) -> bool:
    ie_key = str(entry.get("ie_key") or entry.get("_type") or "").lower()
    if any(token in ie_key for token in _NON_VIDEO_IE_KEYS):
        return False
    # YouTube 的頻道 ID 是 UC 開頭的 24 碼、影片 ID 是 11 碼，可用長度分辨。
    # 這個規則只對 YouTube 成立——Bilibili 的 BV 號就有 12 碼，套上去會被誤刪。
    video_id = str(entry.get("id") or "")
    is_youtube = "youtube" in ie_key or not ie_key
    if is_youtube and entry.get("duration") is None:
        if video_id.startswith("UC") or len(video_id) > 11:
            return False
    return True


def format_results(results: list[SearchResult], width: int = 100) -> list[str]:
    """排版成「編號 / 標記 / 標題 / 長度 / 頻道」的對齊表格，官方音源標上 ♪。

    標題與頻道都用顯示欄寬對齊——中日韓歌名用 len() 會排得參差不齊。
    """
    if not results:
        return []
    index_width = len(str(len(results)))
    # 版面："  12. ♪ 標題……  03:36  頻道"
    prefix = 2 + index_width + 2 + 2  # 縮排 + 編號 + ". " + "♪ "
    title_width = max(20, width - prefix - DURATION_WIDTH - CHANNEL_WIDTH - 4)

    lines = []
    for index, result in enumerate(results, start=1):
        if result.is_official_audio:
            mark = "♪"
        elif result.is_long:
            mark = "≡"
        else:
            mark = " "
        length = human_time(result.duration) if result.duration else "--:--"
        title = pad_display(truncate(result.title, title_width), title_width)
        lines.append(
            f"  {index:>{index_width}}. {mark} {title}  "
            f"{length:>{DURATION_WIDTH}}  {truncate(result.channel, CHANNEL_WIDTH)}"
        )
    return lines


def _normalise(text: str) -> str:
    """比對頻道名用：去掉空白、破折號與大小寫差異。"""
    return "".join(text.lower().split()).replace("-", "").replace("–", "")


def filter_by_artist(results: list[SearchResult], artist: str) -> list[SearchResult]:
    """只留下該歌手頻道上傳的單曲。

    直接搜歌手名字會混進別人做的歌詞版、翻唱與數小時的合輯；比對頻道名稱就能
    篩出官方上傳的內容。若篩完什麼都不剩（冷門歌手、頻道名與搜尋字不同），
    回傳空清單讓呼叫端自行決定退路。
    """
    wanted = _normalise(artist)
    if not wanted:
        return []

    matched = []
    for result in results:
        channel = _normalise(result.channel)
        if not channel:
            continue
        if wanted in channel or channel in wanted:
            matched.append(result)

    # 合輯與演唱會全場不是「一首歌」，但如果全部都是就別把清單清空。
    singles = [r for r in matched if not r.is_long]
    return singles or matched


class SelectionError(ValueError):
    pass


def parse_selection(text: str, count: int) -> list[int]:
    """把使用者輸入解析成 0-based 的索引清單。

    接受 ``3``、``1,3,5``、``2-4``、``all``（全選）與空字串（預設第一筆）。
    輸入 ``q`` 代表取消，回傳空清單。
    """
    raw = text.strip().lower()
    if raw in {"q", "quit", "n", "no", "取消"}:
        return []
    if not raw:
        return [0]
    if raw in {"a", "all", "全部"}:
        return list(range(count))

    picked: list[int] = []
    for part in raw.replace("，", ",").split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part.lstrip("-"):
            start_text, _, end_text = part.partition("-")
            start, end = _one_based(start_text, count), _one_based(end_text, count)
            if start > end:
                start, end = end, start
            picked.extend(range(start, end + 1))
        else:
            picked.append(_one_based(part, count))

    # 去重但保留使用者輸入的順序
    seen: set[int] = set()
    ordered = []
    for index in picked:
        if index not in seen:
            seen.add(index)
            ordered.append(index)
    if not ordered:
        raise SelectionError("沒有選到任何項目")
    return ordered


def _one_based(text: str, count: int) -> int:
    try:
        number = int(text.strip())
    except ValueError:
        raise SelectionError(f"看不懂的編號：{text.strip()!r}") from None
    if not 1 <= number <= count:
        raise SelectionError(f"編號 {number} 超出範圍（1–{count}）")
    return number - 1
