"""多執行緒下載時的終端進度顯示。"""

from __future__ import annotations

import shutil
import sys
import threading
import time
from dataclasses import dataclass, field

from .utils import display_width, human_size, human_time, pad_display, truncate

_CLEAR_LINE = "\x1b[2K"
_CURSOR_UP = "\x1b[1A"
_HIDE_CURSOR = "\x1b[?25l"
_SHOW_CURSOR = "\x1b[?25h"

_REPAINT_INTERVAL = 0.12  # 秒；限制重繪頻率，避免洗版


@dataclass
class _Task:
    label: str
    percent: float = 0.0
    speed: float | None = None
    eta: float | None = None
    stage: str = "下載中"
    updated_at: float = field(default_factory=time.monotonic)


class ProgressReporter:
    """把「已完成」訊息往上捲、「進行中」狀態釘在底部的小型顯示器。

    偵測到輸出不是終端機（例如導向到檔案或 CI）時自動退化成單行純文字，
    不會產生 ANSI 控制碼。
    """

    def __init__(self, total: int, stream=None, enabled: bool = True) -> None:
        self.total = total
        self.stream = stream or sys.stderr
        self.enabled = enabled
        self.done = 0
        self._lock = threading.RLock()
        self._tasks: dict[str, _Task] = {}
        self._drawn = 0
        self._last_paint = 0.0
        self._tty = bool(enabled and getattr(self.stream, "isatty", lambda: False)())

    # -- 生命週期 ---------------------------------------------------------

    def __enter__(self) -> "ProgressReporter":
        if self._tty:
            self.stream.write(_HIDE_CURSOR)
            self.stream.flush()
        return self

    def __exit__(self, *_exc) -> None:
        with self._lock:
            self._erase()
            if self._tty:
                self.stream.write(_SHOW_CURSOR)
            self.stream.flush()

    # -- 事件 -------------------------------------------------------------

    def start(self, key: str, label: str) -> None:
        with self._lock:
            self._tasks[key] = _Task(label=label)
            self._paint(force=True)

    def update(self, key: str, *, percent: float | None = None,
               speed: float | None = None, eta: float | None = None,
               stage: str | None = None) -> None:
        with self._lock:
            task = self._tasks.get(key)
            if task is None:
                return
            if percent is not None:
                task.percent = max(0.0, min(percent, 100.0))
            if speed is not None:
                task.speed = speed
            if eta is not None:
                task.eta = eta
            if stage is not None:
                task.stage = stage
            task.updated_at = time.monotonic()
            self._paint()

    def finish(self, key: str, status: str, message: str) -> None:
        """收掉一個進行中的項目，並在上方留下一行結果。"""
        with self._lock:
            self._tasks.pop(key, None)
            if status != "skipped":
                self.done += 1
            self.log(_status_line(status, message, self.done, self.total))

    def log(self, message: str) -> None:
        """輸出一行永久訊息，不干擾底部的進度區塊。"""
        with self._lock:
            self._erase()
            self.stream.write(message.rstrip() + "\n")
            self.stream.flush()
            self._paint(force=True)

    # -- 繪製 -------------------------------------------------------------

    def _erase(self) -> None:
        if not self._tty or self._drawn == 0:
            self._drawn = 0
            return
        self.stream.write("\r")
        for _ in range(self._drawn):
            self.stream.write(_CURSOR_UP + _CLEAR_LINE)
        self.stream.write("\r")
        self._drawn = 0

    def _paint(self, force: bool = False) -> None:
        if not self.enabled:
            return
        if not self._tty:
            return
        now = time.monotonic()
        if not force and now - self._last_paint < _REPAINT_INTERVAL:
            return
        self._last_paint = now

        # 保留最後一欄不用：游標剛好停在最右緣時，部分終端機會自動換行。
        width = max(40, shutil.get_terminal_size((100, 24)).columns - 1)
        lines = [self._render(task, width) for task in list(self._tasks.values())]
        self._erase()
        for line in lines:
            self.stream.write(truncate(line, width) + "\n")
        self._drawn = len(lines)
        self.stream.flush()

    def _render(self, task: _Task, width: int) -> str:
        bar_width = 18
        filled = int(task.percent / 100 * bar_width)
        # 刻意用 ASCII：方塊繪圖字元在中日韓終端機是雙寬，畫出來的列會超寬換行。
        bar = "#" * filled + "-" * (bar_width - filled)
        speed = f"{human_size(task.speed)}/s" if task.speed else "--"
        tail = f"[{bar}] {task.percent:5.1f}%  {speed:>11}  ETA {human_time(task.eta)}"
        label_width = max(12, width - display_width(tail) - 4)
        return f"  {pad_display(truncate(task.label, label_width), label_width)} {tail}"


def _status_line(status: str, message: str, done: int, total: int) -> str:
    icon = {"ok": "✔", "skipped": "•", "error": "✖"}.get(status, "-")
    counter = f"[{done}/{total}]" if status != "skipped" else "[略過]"
    return f"{icon} {counter} {message}"
