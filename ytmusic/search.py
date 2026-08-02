"""關鍵字搜尋的結果解析、顯示與選擇。

真正發出搜尋請求的是 ``Downloader.search()``（它才有 cookies、proxy 等設定）；
這裡只處理不需要網路的部分，方便測試。
"""

from __future__ import annotations

from dataclasses import dataclass

from .utils import human_time, pad_display, strip_topic, truncate


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
    def channel(self) -> str:
        return strip_topic(self.uploader) or self.uploader


def parse_results(info: dict | None) -> list[SearchResult]:
    """把 yt-dlp 的搜尋結果轉成 SearchResult 清單。"""
    if not info:
        return []
    results: list[SearchResult] = []
    for entry in info.get("entries") or []:
        if not entry:
            continue
        video_id = entry.get("id")
        if not video_id:
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
        mark = "♪" if result.is_official_audio else " "
        length = human_time(result.duration) if result.duration else "--:--"
        title = pad_display(truncate(result.title, title_width), title_width)
        lines.append(
            f"  {index:>{index_width}}. {mark} {title}  "
            f"{length:>{DURATION_WIDTH}}  {truncate(result.channel, CHANNEL_WIDTH)}"
        )
    return lines


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
