# ytmusic — YouTube 音樂下載器

以 [yt-dlp](https://github.com/yt-dlp/yt-dlp) 為核心的命令列工具：把 YouTube 影片或播放清單
下載成音樂檔，自動轉檔、寫入 ID3 標籤與專輯封面，並記錄下載歷史避免重複下載。

```
$ ytmusic dl "https://www.youtube.com/playlist?list=PL..." -f mp3 -q 320 -j 4
正在解析網址…
共 12 首；待下載 9 首，略過 3 首（已下載過）
輸出：/home/you/Music/ytmusic　格式：mp3 @ 320　並行：4
✔ [1/9] Rick Astley - Never Gonna Give You Up
✔ [2/9] Rick Astley - Together Forever
  周杰倫 - 告白氣球           [████████████░░░░░░]  67.2%     2.4 MiB/s  ETA 00:03
  五月天 - 溫柔               [█████░░░░░░░░░░░░░]  28.9%     1.1 MiB/s  ETA 00:11
```

## 功能

- **音訊下載與轉檔** — mp3 / m4a / opus / flac / wav，音質可選 96–320 kbps 或 `best`
- **播放清單批次下載** — 支援播放清單與頻道網址，可設定同時下載數
- **ID3 標籤與封面** — 自動寫入歌名、演出者、專輯、年份與正方形專輯封面
- **下載歷史** — 記住下載過的影片，重跑播放清單時自動略過
- **檔名整理** — 從整理過的中繼資料重新命名，去掉 `(Official Music Video)` 這類雜訊

## 安裝

需要 Python 3.9 以上，以及 **ffmpeg**（轉檔用）。

```bash
git clone <此倉庫網址> && cd YTDownload
pip install -e .
```

或不安裝套件、直接跑原始碼：

```bash
pip install -r requirements.txt
python -m ytmusic --help
```

安裝 ffmpeg：

| 平台 | 指令 |
| --- | --- |
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Windows | `winget install Gyan.FFmpeg` |

沒有 ffmpeg 也能用 `--no-convert` 直接保留 YouTube 原始音訊（通常是 m4a 或 webm）。

`Pillow` 是選用的：裝了封面會裁成正方形，沒裝則維持原本的 16:9。

## 使用方式

### 下載

```bash
# 單曲
ytmusic dl "https://youtu.be/dQw4w9WgXcQ"

# 播放清單，320 kbps，同時下載 4 首，各自收進以清單命名的資料夾
ytmusic dl "https://www.youtube.com/playlist?list=PL..." -q 320 -j 4 --playlist-folder

# 多個網址一次下載，輸出成 flac
ytmusic dl URL1 URL2 URL3 -f flac -o ~/Music/Lossless

# 先看看會下載哪些，不實際下載
ytmusic dl "https://www.youtube.com/playlist?list=PL..." --dry-run
```

主要選項：

| 選項 | 說明 |
| --- | --- |
| `-o, --output DIR` | 輸出資料夾 |
| `-f, --format` | `mp3`（預設）/ `m4a` / `opus` / `flac` / `wav` |
| `-q, --quality` | `96`–`320` kbps 或 `best`（預設 `192`） |
| `-j, --jobs N` | 同時下載數，預設 3，上限 16 |
| `--playlist-folder` | 以播放清單名稱建立子資料夾，並在檔名前加曲序 |
| `--force` | 忽略下載歷史，重新下載 |
| `--dry-run` | 只列出將要下載的曲目 |
| `--no-convert` | 不轉檔（不需要 ffmpeg） |
| `--no-tags` / `--no-cover` | 不寫標籤 / 不嵌入封面 |
| `--no-rename` | 沿用 yt-dlp 檔名樣板，不依標籤改名 |
| `--no-history` | 這次不讀也不寫下載歷史 |
| `--cookies-from-browser` | 從瀏覽器讀 cookies，例如 `chrome`、`firefox`、`edge` |
| `--cookies FILE` | 指定 `cookies.txt` |
| `--proxy URL` / `--rate-limit RATE` | 代理伺服器 / 限速（例如 `500K`） |

### 下載歷史

```bash
ytmusic history list          # 列出最近 20 筆（-n 0 顯示全部）
ytmusic history remove <ID>   # 移除某支影片的紀錄，之後可重新下載
ytmusic history prune         # 清掉檔案已被刪除的紀錄
ytmusic history clear         # 清空全部
```

`history list` 開頭的 `?` 表示紀錄還在、但檔案已不在原本的路徑。

### 設定

把常用選項存成預設值，之後就不用每次都打：

```bash
ytmusic config show
ytmusic config set output_dir ~/Music/YT
ytmusic config set quality 320
ytmusic config set playlist_folder true
ytmusic config reset
```

命令列參數永遠優先於設定檔。

設定檔與歷史資料庫放在 `~/.config/ytmusic/`（可用 `XDG_CONFIG_HOME` 或 `YTMUSIC_HOME`
環境變數改位置）。

## 標籤是怎麼判斷的

1. YouTube Music 的曲目自帶 `track` / `artist` / `album` 欄位，優先採用。
2. 一般影片則從標題解析：先移除 `(Official Music Video)`、`[Lyrics]`、`【官方MV】` 這類
   宣傳字樣，再依 `演出者 - 歌名` 拆解；拆不出來就用頻道名稱當演出者。
3. 下載播放清單時，清單名稱會當成專輯、清單順序會當成曲序。
4. 封面取解析度最高的 JPEG 縮圖（刻意避開 webp，部分播放器不認）。

檔名同樣用整理後的結果，所以會拿到 `Rick Astley - Never Gonna Give You Up.mp3`
而不是 `Rick Astley - Rick Astley - Never Gonna Give You Up (Official Video) (4K...).mp3`。

## 離開狀態碼

| 碼 | 意義 |
| --- | --- |
| 0 | 全部成功 |
| 1 | 全部失敗 |
| 2 | 參數或設定有誤 |
| 3 | 前置條件不足（缺 ffmpeg、缺 yt-dlp、找不到曲目） |
| 4 | 部分成功、部分失敗 |
| 130 | 使用者中斷 |

## 疑難排解

**`HTTP Error 403` 或「需要登入」** — 這類影片（年齡限制、會員限定、DRM 保護）要帶帳號
cookies 才下載得動：

```bash
ytmusic dl <URL> --cookies-from-browser chrome
```

**下載一直失敗或速度異常** — yt-dlp 需要跟著 YouTube 的改動更新，先試 `pip install -U yt-dlp`。

**已經下載過但想重下** — 用 `--force`，或 `ytmusic history remove <影片ID>`。

## 開發

```bash
pip install -e ".[dev]"
python -m pytest
```

測試不需要網路，涵蓋標題解析、設定讀寫、歷史資料庫、播放清單攤平與檔名重新命名。

## 使用須知

本工具僅供下載你有權利取得的內容，例如自己的作品、公共領域素材，或授權允許離線
使用的音樂。下載受版權保護的內容可能違反 YouTube 服務條款與當地法律，請自行確認
你的使用方式合法。

## 授權

MIT
