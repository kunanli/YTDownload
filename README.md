# YTDownload

**v1.19.0** ｜ [更新紀錄](CHANGELOG.md) ｜ [English](README.en.md)

把 YouTube、YouTube Music、Bilibili、Vimeo、Facebook 等 1700 多個網站的影片和音樂下載到電腦裡。歌曲會自動整理好歌名、歌手和專輯封面。

**完全不懂電腦也沒關係**，照著下面做就行。安裝只要做一次，大概 10 分鐘。

---

## 這個工具能做什麼

| 你想要 | 做得到嗎 |
| --- | --- |
| 下載一首歌變成 MP3 | ✅ |
| 下載整張播放清單 | ✅ |
| 下載影片（MP4） | ✅ |
| 自動填好歌名、歌手、專輯封面 | ✅ |
| 記住下載過什麼，不會重複下載 | ✅ |
| 下載歌詞（.lrc 同步歌詞） | ✅ |
| 下載影片字幕（內嵌字幕軌） | ✅ |
| 用歌手名稱找歌 | ✅ |
| YouTube Music 的網址 | ✅ |
| Bilibili（含搜尋、合集、收藏夾） | ✅ |
| Vimeo | ✅ |
| Facebook（影片、Reels） | ✅ 公開內容 |
| Instagram（貼文、Reels、限動） | ✅ 需登入 |
| LinkedIn（貼文影片、Learning） | ✅ 需登入 |
| 微信視頻號 | ✅ [不用裝憑證、不用解密](#微信視頻號) |
| 介面支援多國語言 | ✅ [中文 · 日本語 · English · 한국어 · Español · Suomi](#介面語言) |

---

## 🔍 快速查表

### 我想要…

| 我想要 | 打這行 | 說明 |
| --- | --- | --- |
| **完全不想打指令** | 雙擊 `下載.bat` | [看這裡](#最簡單的用法雙擊啟動選單) |
| 下載一首歌 | `python -m ytmusic dl "網址"` | [看這裡](#下載一首歌) |
| 不知道網址，用歌名找 | `python -m ytmusic search "歌名"` | [看這裡](#用歌名搜尋) |
| 找某個歌手的歌 | `python -m ytmusic search "歌手" -a` | [看這裡](#用歌手名稱找歌) |
| 下載 Bilibili 影片 | `python -m ytmusic dl "B站網址"` | [看這裡](#bilibili) |
| 在 Bilibili 搜尋 | `python -m ytmusic search "關鍵字" --site bilibili` | [看這裡](#bilibili) |
| 下載 Vimeo / Facebook | `python -m ytmusic dl "網址"` | [看這裡](#vimeofacebookinstagram-與其他站台) |
| 下載 Instagram / LinkedIn | `... --cookies-from-browser chrome` | [看這裡](#vimeofacebookinstagram-與其他站台) |
| 下載微信視頻號 | `python -m ytmusic wechat "網址"` | [看這裡](#微信視頻號) |
| 下載整張播放清單 | `python -m ytmusic dl "網址" --playlist` | [看這裡](#下載整張播放清單) |
| 每首歌收進清單資料夾 | 再加 `--playlist-folder` | [看這裡](#下載整張播放清單) |
| 下載影片 | `python -m ytmusic dl "網址" --video 1080` | [看這裡](#下載影片) |
| 一併抓歌詞 | 加 `--lyrics` | [看這裡](#歌詞與字幕) |
| 影片一併嵌字幕 | 加 `--subs` | [看這裡](#歌詞與字幕) |
| 指定字幕／歌詞語言 | `--subs 繁中,英`、`--lyrics 日` | [看這裡](#語言) |
| 整張清單下載影片＋字幕 | `... --playlist --video 1080 --subs 繁中,英` | [看這裡](#歌詞與字幕) |
| 清單有新歌自動補 | `python -m ytmusic sync` | [看這裡](#追蹤播放清單自動補新歌) |
| 重新下載已下載過的 | 加 `--force` | [看這裡](#下載過的我還想再下載一次) |
| 看下載過什麼 | `python -m ytmusic history list` | [看這裡](#下載歷史) |
| 需要登入才能下載的影片 | 加 `--cookies-from-browser chrome` | [看這裡](#http-error-403或需要登入) |
| 只想先看會下載什麼 | 加 `--dry-run` | [看這裡](#第四部分完整選項進階) |

### 想改預設值（設定一次，永久生效）

| 我想改 | 打這行 |
| --- | --- |
| 存檔位置 | `python -m ytmusic config set output_dir "D:\音樂"` |
| 音質 | `python -m ytmusic config set quality 320` |
| 歌詞語言 | `python -m ytmusic config set subtitle_langs "繁中,英"` |
| 同時下載幾首 | `python -m ytmusic config set concurrency 5` |
| 短網址自動展開（不再詢問） | `python -m ytmusic config set expand_short_urls true` |
| 介面語言 | `python -m ytmusic config set ui_language ja` |
| 看目前設定 | `python -m ytmusic config show` |

### 出問題了？照畫面上的字找

| 畫面上寫 | 怎麼辦 |
| --- | --- |
| `'ytmusic' is not recognized` | [指令要用 `python -m` 開頭](#找不到-ytmusic-這個指令) |
| `找不到 ffmpeg` | [裝 ffmpeg，裝完重開視窗](#找不到-ffmpeg) |
| `Video unavailable` | [那支影片本身有問題](#video-unavailable影片無法使用) |
| `Instagram sent an empty media response` | [Instagram 要登入](#vimeofacebookinstagram-與其他站台) |
| `HTTP Error 403`、需要登入 | [要帶瀏覽器登入資訊](#http-error-403或需要登入) |
| `HTTP Error 404`（`list=LM`） | [私人清單一定要登入](#我喜歡的音樂或私人清單下載不了) |
| 雙擊 `.bat` 狂洗畫面 | [舊版問題，更新就好](#雙擊-下載bat-一直跳錯或狂洗畫面) |
| `Python was not found` / Store 跳出來 | [那是 Windows 的假 python](#第一次雙擊會自動把東西裝好) |
| 下載很慢、一直失敗 | [更新 yt-dlp](#下載很慢或一直失敗) |
| 「沒有字幕可轉成歌詞」 | [那支影片沒字幕，正常現象](#歌詞與字幕) |
| 想看完整錯誤訊息 | [指令後面加 `-v`](#我想看到底出了什麼事) |
| `'playwright' is not recognized` | [要用 `python -m playwright`](#微信視頻號) |
| LinkedIn「Copy video address」是灰的 | [要複製貼文網址](#linkedin-的影片網址怎麼複製) |
| 選單裡貼上網址沒反應 | [Windows Terminal 按 Ctrl+V，舊版 PowerShell 按右鍵](#最簡單的用法雙擊啟動選單) |
| `無法讀取 <網址>：` 後面一片空白 | [1.10.0 修掉了，`git pull` 更新](#我想看到底出了什麼事) |
| 微信視頻號「沒有回傳影片位址」 | [換個網路，或加 `--resolver`](#如果它說微信沒有回傳影片位址) |
| `[SSL: UNEXPECTED_EOF_WHILE_READING]` | [連線被切斷，不是影片的問題](#ssl-連線被切斷) |
| 只有 LinkedIn 連不上，其他站台正常 | [裝 curl_cffi 假扮瀏覽器指紋](#只有-linkedin-這樣那多半是-tls-指紋) |
| **不知道問題出在哪** | [`python -m ytmusic doctor "網址"`](#先跑-doctor-讓它告訴你問題在哪) |
| 只有 `lnkd.in`／`bit.ly` 短網址連不上 | [短網址網域被擋，加 `--expand`](#短網址被擋住) |
| `curl: (35) TLS connect error ... invalid library` | [curl_cffi 在 Windows 上的已知問題](#短網址被擋住) |

---

## 最簡單的用法：雙擊啟動選單

### 第一次雙擊會自動把東西裝好

`下載.bat` 不只是開選單，它會**先確認你有沒有能跑的環境**：

| 順序 | 它做什麼 | 缺了會怎樣 |
| --- | --- | --- |
| 1 | 找一個**真的跑得起來**的 Python | 沒有就進入引導安裝（見下） |
| 2 | 檢查 `ytmusic` 套件本身 | 沒裝就**自動** `pip install -e .`（第一次雙擊會看到這步） |
| 3 | 開選單，選單再檢查 yt-dlp / mutagen / ffmpeg / curl_cffi | 缺了會列出來，並問要不要幫你裝 |

#### 沒有 Python 的話：兩步就好

```
  ================================================
     Setup - step 1 of 2:  install Python
  ================================================

  NOTE: Windows has a placeholder called "python" that is not a real
  Python. That is why you may have seen:
      "Python was not found; run without arguments to install from
       the Microsoft Store"
  Installing the real thing below fixes it.

  I can install it for you now with winget.

  Install Python 3.12 now? [Y/n] Y
```

裝完之後它會告訴你**第二步**：

```
  ================================================
     Setup - step 2 of 2:  reopen this window
  ================================================

  Python is installed, but THIS window still does not know where it is.

    1. Close this window.
    2. Double-click the same file again.
```

> ### ⚠️ 「明明裝了 Python，它卻說找不到」
>
> Windows 內建一支**假的 `python`**（App Execution Alias）放在 PATH 裡。
> 名字找得到，執行卻只會印一句
> `Python was not found; run without arguments to install from the Microsoft Store`。
>
> 所以啟動檔**不是只檢查名字，而是真的跑一次**才算數。若你想徹底關掉那支假的：
> 「設定 › 應用程式 › 進階應用程式設定 › 應用程式執行別名」，把兩個 `python` 都關掉。

沒有 winget 的話會給你手動步驟，並特別提醒安裝程式第一頁那個最常被漏勾的
**`Add python.exe to PATH`**。

#### 相依套件缺了會怎樣

第 3 步長這樣 —— **只有缺東西時才會出現**，都齊全的話直接進選單：

```
  ── 缺少一些東西 ──

  [必要] ffmpeg：轉不了 MP3，也合併不了影片的畫面與聲音
  [選用] curl_cffi：部分站台（如 LinkedIn）會擋非瀏覽器的連線，裝了才連得上

  要現在幫你裝嗎？ [Y/n]
```

- **[必要]** 的才會主動問你要不要裝；**[選用]** 的只列出來，不會追著你問
- ffmpeg 會用 `winget`（Windows）或 `brew`（macOS）裝；Linux 只給指令請你自己跑
  （那需要 sudo，不該替你提權）
- 答 `n` 就會印出手動步驟，不會硬裝
- 裝完如果還說找不到，**把視窗關掉重開** —— 新裝的程式要重開才進得了 PATH

Mac 的 `下載.command` 流程完全一樣（改用 Homebrew）。

### 選單長什麼樣

裝好之後，**不想打指令的話，直接在資料夾裡雙擊
[`下載.bat`](%E4%B8%8B%E8%BC%89.bat)**（Mac 是
[`下載.command`](%E4%B8%8B%E8%BC%89.command)），會跳出選單：

```
  ================================================
     影音下載器
     YouTube · Bilibili · Vimeo · 微信視頻號 …
  ================================================

    [1] 下載音樂（任何網站，貼網址）
    [2] 用歌名搜尋
    [3] 用歌手名稱找歌
    [4] 下載影片（任何網站，貼網址）
    [5] 下載微信視頻號
    [6] 同步追蹤的播放清單
    [7] 看下載過什麼
    [8] 追蹤一張新的播放清單
    [9] 檢查環境／連線（下載失敗時用）
    [L] 切換語言 / Language

    [0] 離開

  請選擇（直接按 Enter = 1）：
```

### 介面語言

選單支援**六種語言**：中文（繁體）· 日本語 · English · 한국어 · Español · Suomi。

在選單按 **`[L]`**：

```
   介面語言 / Interface language

    [1]*中文（繁體）
    [2] 日本語
    [3] English
    [4] 한국어
    [5] Español
    [6] Suomi

  請選擇（直接按 Enter = 不變）：
```

`*` 是目前的語言。選好**立刻存起來**，下次打開就是那個語言，不用再選。
`[L]` 這一列在每種語言下都帶著 "Language" 這個字 —— 就算現在的介面你完全看不懂，
也找得到出口。

第一次執行選單時會問一次，之後就不再問。也可以不透過選單直接設：

```powershell
python -m ytmusic config set ui_language ja     # zh-Hant, ja, en, ko, es, fi
```

**指令列也一樣**——`dl`、`doctor`、`wechat` 的輸出都跟著設定走：

```
$ python -m ytmusic dl "https://youtu.be/..." --dry-run     # ui_language = ko
URL 분석 중…
총 1개 중 1개 다운로드
출력: /Users/you/Music/ytmusic   형식: mp3 @ 192   동시: 3
```

失敗時的**解釋**也翻譯了，這其實才是重點：

```
$ python -m ytmusic dl "https://example.com/nope"           # ui_language = es
Analizando la URL…
✖ No se pudo leer https://example.com/nope: HTTP Error 404: Not Found
No se encontró nada que descargar.
```

> **沒翻的只有兩處，都是刻意的。** `--help` 的參數說明（打指令的人本來就在讀
> 英文旗標），以及 `下載.bat` 自己那三句訊息 —— `cmd.exe` 會在 Python 啟動前
> 就把非 ASCII 文字弄壞。
>
> 沒設定過語言時會**照系統語系自動選**（`LANG=ko_KR.UTF-8` → 韓文），
> 認不出來就用英文。設定檔裡選過的永遠優先。

### 選單怎麼決定平台

**貼網址的選項（[1] [4]）不會問你是哪個平台** —— YouTube、Bilibili、Vimeo、
Facebook… 工具看網址就認得出來。貼**微信視頻號**的網址也沒關係，會自動轉去走
微信那條路。

**只有搜尋（[2] [3]）會問**，因為關鍵字看不出你想搜哪裡：

```
  要找什麼歌？ 周杰倫

   在哪裡搜尋：[1] YouTube　[2] Bilibili
  請選擇（直接按 Enter = YouTube）：2
```

選單會一路問到底，**字幕和歌詞可以自己挑語言**：

```
  請選擇（直接按 Enter = 1）：4
  貼上網址後按 Enter：https://www.youtube.com/watch?v=...

   畫質：[1] 720p　[2] 1080p　[3] 最高
  請選擇（直接按 Enter = 720p）：2
  要一起嵌入字幕嗎？[y/Enter=不用] y

   [1] 繁中　[2] 簡中　[3] 英　[4] 日　[5] 韓　[6] 西班牙
   可複選，用逗號分隔（例如 1,3）
  字幕語言（直接按 Enter = 全部）：1,3
```

> 💡 **貼上沒反應？** Windows Terminal 按 `Ctrl+V`，舊版 PowerShell 按滑鼠**右鍵**。
> 貼上落空時選單會再問一次，不會把你踢回主選單。

**貼播放清單網址也可以**——選單會再問要不要整張下載、要不要收進獨立資料夾，
所以「整張清單下載影片 + 指定字幕語言」在選單裡就做得到。

各選項對應的詳細說明：
[① 下載一首歌](#下載一首歌)、
[② 用歌名搜尋](#用歌名搜尋)、
[③ 用歌手名稱找歌](#用歌手名稱找歌)、
[④ 下載影片](#下載影片)、
[⑤ 微信視頻號](#微信視頻號)、
[⑥⑧ 追蹤播放清單](#追蹤播放清單自動補新歌)、
[⑦ 下載歷史](#下載過的我還想再下載一次)

貼上網址、按 Enter，就開始下載。完全不用碰 PowerShell。

打指令的人也可以隨時叫出同一個選單：

```powershell
python -m ytmusic menu
```

---

## 目錄

**[🔍 快速查表](#-快速查表)** — 找指令、找錯誤，先看這個

- [雙擊啟動選單](#最簡單的用法雙擊啟動選單) — 不用打任何指令
- **[第一部分：安裝](#第一部分安裝只需做一次)** — 只需做一次
  - [Windows](#windows)　·　[macOS](#macos)
- **[第二部分：開始下載](#第二部分開始下載)**
  - [用歌名搜尋](#用歌名搜尋)
  - [Bilibili](#bilibili)　·　[Vimeo / Facebook / Instagram](#vimeofacebookinstagram-與其他站台)　·　[微信視頻號](#微信視頻號)
  - [用歌手名稱找歌](#用歌手名稱找歌)
  - [下載一首歌](#下載一首歌)
  - [下載整張播放清單](#下載整張播放清單)
  - [下載影片](#下載影片)
  - [追蹤播放清單，自動補新歌](#追蹤播放清單自動補新歌)
  - [歌詞與字幕](#歌詞與字幕)　·　[語言設定](#語言)
  - [檔案存到哪裡](#檔案存到哪裡)　·　[想要更好的音質](#想要更好的音質)
- **[第三部分：遇到問題怎麼辦](#第三部分遇到問題怎麼辦)**
  - [找不到 ytmusic 指令](#找不到-ytmusic-這個指令)
  - [雙擊 .bat 狂洗畫面](#雙擊-下載bat-一直跳錯或狂洗畫面)
  - [找不到 ffmpeg](#找不到-ffmpeg)
  - [Video unavailable](#video-unavailable影片無法使用)
  - [HTTP Error 403 / 需要登入](#http-error-403或需要登入)
  - **[先跑 doctor，讓它告訴你問題在哪](#先跑-doctor-讓它告訴你問題在哪)** — 不確定時先跑這個
  - [短網址被擋住](#短網址被擋住)　·　[SSL 連線被切斷](#ssl-連線被切斷)
  - [下載很慢或一直失敗](#下載很慢或一直失敗)
  - [想看詳細錯誤](#我想看到底出了什麼事)
  - [想重新下載已下載過的](#下載過的我還想再下載一次)
  - [私人清單下載不了](#我喜歡的音樂或私人清單下載不了)
  - [怎麼更新這個工具](#怎麼更新這個工具)
- **[第四部分：完整選項](#第四部分完整選項進階)**
  - [下載選項一覽](#下載選項)　·　[下載歷史](#下載歷史)　·　[預設設定](#預設設定)
  - [標籤怎麼判斷](#標籤是怎麼判斷的)　·　[離開狀態碼](#離開狀態碼)　·　[開發](#開發)

---

# 第一部分：安裝（只需做一次）

## Windows

### 步驟 1：打開 PowerShell

按鍵盤 `Win` 鍵，打 `powershell`，按 Enter。

會跳出一個黑色（或藍色）的視窗，這就是等一下要打字的地方。

### 步驟 2：檢查你有沒有需要的東西

**複製下面這行，貼到 PowerShell 裡，按 Enter：**

```powershell
python --version; git --version; ffmpeg -version
```

> 💡 貼上的方法：在 PowerShell 視窗裡按滑鼠**右鍵**就會自動貼上。

**看結果：**

- 如果出現三組版本號 → 太好了，跳到 **步驟 4**
- 如果有任何一個說「找不到」或跳出 Microsoft Store → 繼續步驟 3

### 步驟 3：安裝缺少的東西

**把下面三行一次全部複製貼上，按 Enter：**

```powershell
winget install Python.Python.3.12
winget install Git.Git
winget install Gyan.FFmpeg
```

安裝過程會跑一陣子，等它跑完。

> ### ⚠️ 這一步最多人卡住
>
> 裝完之後，**必須把 PowerShell 整個關掉，再重新打開一次**。
>
> 不重開的話，電腦不知道新程式裝在哪裡，下一步一定會失敗。

重開之後，**再跑一次步驟 2 的檢查指令**。三組版本號都出現才繼續。

### 步驟 4：下載這個工具

**複製貼上，按 Enter：**

```powershell
cd ~
git clone https://github.com/kunanli/YTDownload.git
cd YTDownload
pip install -e .
```

看到最後出現 `Successfully installed ytmusic` 就成功了。

### 步驟 5：測試

**複製貼上，按 Enter：**

```powershell
python -m ytmusic dl "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

看到 `✔ 完成 1 首` 就代表全部裝好了 🎉

檔案會在 `C:\Users\你的名字\Music\ytmusic`。

---

## macOS

打開「終端機」（Terminal），貼上這幾行：

```bash
# 1. 安裝 Homebrew（如果還沒有）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. 安裝需要的東西
brew install python git ffmpeg

# 3. 下載這個工具
cd ~
git clone https://github.com/kunanli/YTDownload.git
cd YTDownload
pip3 install -e .

# 4. 測試
python -m ytmusic dl "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

---

# 第二部分：開始下載

> ### 📌 每次要用之前，先切換到工具的資料夾
>
> ```powershell
> cd ~\YTDownload
> ```
>
> （Mac 是 `cd ~/YTDownload`）

> ### 📌 指令都是 `python -m ytmusic` 開頭
>
> 這個寫法在任何電腦上都能用。如果你看過 `ytmusic dl ...` 這種短寫法跑不動，
> 是 PATH 的問題，見[「找不到 ytmusic 這個指令」](#找不到-ytmusic-這個指令)。

> ### 📌 網址一定要用雙引號 `" "` 包起來
>
> ```powershell
> python -m ytmusic dl "https://..."     ✅ 對
> python -m ytmusic dl https://...       ❌ 錯，網址有 & 的話會壞掉
> ```

## 用歌名搜尋

**不知道網址也沒關係**，直接打歌名：

```powershell
python -m ytmusic search "告白氣球 周杰倫"
```

會列出結果讓你挑：

```
  1. ♪ 周杰倫 - 告白氣球                          03:35  周杰倫
  2.   周杰倫 Jay Chou《告白氣球》Official MV      03:36  周杰倫 Jay Chou
  3. ≡ 周杰倫最好聽的20首歌曲                    1:26:32  杰威爾歌詞MV頻道

  ♪ = 官方音源（音質通常最好）　≡ = 超過 15 分鐘，多半是合輯

要下載哪幾首？[1-8／逗號分隔／a 全部／Enter 第一首／q 取消]
```

輸入方式很彈性：

| 你打 | 意思 |
| --- | --- |
| 直接按 Enter | 下載第 1 首 |
| `3` | 下載第 3 首 |
| `1,3,5` | 下載第 1、3、5 首 |
| `2-4` | 下載第 2 到 4 首 |
| `a` | 全部下載 |
| `q` | 取消 |

其他選項：

```powershell
python -m ytmusic search "歌名" -n 20      # 顯示 20 筆（預設 8）
python -m ytmusic search "歌名" --first    # 不問，直接抓第一筆
python -m ytmusic search "歌名" --video    # 搜到的直接下載成影片
```

> 💡 有 ♪ 記號的是 YouTube Music 的官方音源，通常音質最好、也不會有片頭片尾。

## Bilibili

**網址直接貼就能用**，跟 YouTube 一樣：

```powershell
python -m ytmusic dl "https://www.bilibili.com/video/BV1xx411c7mD"
python -m ytmusic dl "https://www.bilibili.com/video/BVxxxxxxx" --video 1080
```

UP 主會被當成「演出者」寫進標籤，檔名一樣整理成 `UP主 - 標題.mp3`。
合集、收藏夾、UP 主的投稿列表也都支援，貼上網址就會整批展開。

搜尋要加 `--site bilibili`：

```powershell
python -m ytmusic search "周杰倫" --site bilibili
```

> ⚠️ Bilibili 有**地區限制**。部分影片在中國大陸以外會顯示
> `This video may be deleted or geo-restricted`，這是 Bilibili 擋的，不是工具的問題。
> 有代理伺服器的話可以加 `--proxy`：
>
> ```powershell
> python -m ytmusic dl "網址" --proxy socks5://127.0.0.1:1080
> ```
>
> 需要登入才能看的影片（大會員、付費內容）加 `--cookies-from-browser chrome`。

## Vimeo、Facebook、Instagram 與其他站台

**網址直接貼就好**，用法跟 YouTube 完全一樣：

```powershell
python -m ytmusic dl "https://vimeo.com/76979871" --video 1080
python -m ytmusic dl "https://www.facebook.com/watch/?v=..." --video 720
python -m ytmusic dl "https://www.instagram.com/reel/..." --cookies-from-browser chrome
```

底層的 yt-dlp 支援 **1700 多個網站**，多數貼上網址就能用。

### 各站台的注意事項

| 站台 | 狀況 |
| --- | --- |
| **Vimeo** | 直接可用。一般頁面要先換 OAuth token，某些網路環境會被回 `401 Unauthorized`，遇到時工具會**自動改用播放器網址重試**，你不用做任何事 |
| **Facebook** | **公開**影片與 Reels 直接可用；私人貼文、社團內容要加 `--cookies-from-browser` |
| **Instagram** | **幾乎都要登入**。沒帶 cookies 會看到「Instagram sent an empty media response」，加 `--cookies-from-browser chrome` 即可 |
| **LinkedIn** | 短網址 `lnkd.in/p/...` 與貼文網址都可以，**公開貼文不需登入**；登入才看得到的內容才要加 `--cookies-from-browser`。**要複製的是貼文網址，不是影片網址**，見下方 |

需要登入的站台，記得**先把該瀏覽器完全關掉**再執行，詳見
[「HTTP Error 403」或「需要登入」](#http-error-403或需要登入)。

### LinkedIn 的影片網址怎麼複製

**右鍵點影片沒有用** —— LinkedIn 把「Copy video address」鎖成灰色。
你要的是**貼文網址**，不是影片元素的網址。

兩個方法擇一：

| 方法 | 怎麼做 |
| --- | --- |
| **A** | 點貼文右上角的 `•••` → **Copy link to post** |
| **B** | 點作者名字下方的時間戳（例如 `1w`）→ 開啟該貼文專頁 → 複製網址列 |

拿到的網址長這樣：

```
https://www.linkedin.com/posts/某某帳號_關鍵字-activity-7xxxxxxxxxxxxxxxx-XXXX
```

然後：

```powershell
python -m ytmusic dl "貼文網址" --video 1080 --cookies-from-browser chrome
```

> 💡 同樣的道理也適用 Facebook 與 Instagram：**複製貼文／Reel 的網址**，
> 不要對影片本身按右鍵。

> ⚠️ 這些平台上多數是**別人的個人內容**。下載前想一下你有沒有權利保存與再利用，
> 詳見[使用須知](#使用須知)。

## 微信視頻號

**可以下載，而且是乾淨的 MP4** —— 不用裝憑證、不用代理整台電腦、也不用解密。

```powershell
python -m ytmusic wechat "https://weixin.qq.com/sph/XXXXXXXX"
```

```
正在向微信查這支影片…
  三次方AIRX｜虚幻引擎的Codex时刻，3D原生Agent来了 …
  拿到影片位址了，不用開瀏覽器。

找到影片，開始下載 → 三次方AIRX - 虚幻引擎的Codex时刻，3D原生Agent来了 一句话生成整个世界.mp4
完成　1.9 MiB
```

原理：微信視頻號的分享頁是一層 JS 外殼（整頁只有 2.5 KB），但頁面背後那支
`get_feed_info` API **不需要登入、不需要簽章**，直接問就會回影片位址。
拿到的檔案是標準 H.264／H.265 MP4，實測可以直接播放。

### 如果它說「微信沒有回傳影片位址」

同一支影片、同樣的請求，**換個網路環境問就拿得到** —— 微信會按來源決定要不要給
（實測：不同出口 IP 拿到的 `entryScene` 不一樣，有影片的是 51，沒影片的是 64）。

依序試：

| 做法 | 指令 |
| --- | --- |
| 換個網路（手機熱點、關掉 VPN／Proxy） | 原本那行再跑一次 |
| 用線上解析服務代查 | 加 `--resolver` |
| 讓瀏覽器實際載入頁面 | 加 `--browser` |

> ### ⚠️ `--resolver` 會把網址送給第三方
>
> 線上解析用的是 [ltaoo/wx_channels_download](https://github.com/ltaoo/wx_channels_download)
> 提供的公開服務 `sph.litao.workers.dev`。它**不屬於本工具**，也不受我們控制。
>
> 送出去的只有影片網址本身，**不會送出你的 cookies 或登入資訊**。工具一定會先問過
> 你才送；不想被問就加 `--no-resolver`（永遠不用），或自架一份用
> `--resolver-url` 指過去。

**不用先安裝任何東西** —— 第一次執行時如果缺 Playwright 或瀏覽器，
工具會問你要不要自動裝：

```
這個功能需要 Playwright（用來開瀏覽器），目前沒有安裝。
要現在自動安裝嗎？ [Y/n]

還缺瀏覽器本體（Chromium，約 150 MB）。
要現在下載嗎？ [Y/n]
```

直接按 Enter 就會裝好並繼續。不想被問就加 `-y`。

> 💡 想自己手動裝的話，**注意要用 `python -m`**：
>
> ```powershell
> python -m pip install playwright
> python -m playwright install chromium
> ```
>
> 直接打 `playwright install chromium` 在 Windows 上多半會說
> 「不是內部或外部命令」——pip 裝的執行檔跟 `ytmusic` 一樣不在 PATH。

### 第一次：先登入

```powershell
python -m ytmusic wechat --login
```

會開一個瀏覽器，**視窗不會自動關閉** —— 慢慢掃碼，登入好之後回到終端機按 Enter。
登入狀態會存起來，之後不用再掃。

### 之後：直接下載

```powershell
python -m ytmusic wechat "https://weixin.qq.com/sph/XXXXXXXX"
```

瀏覽器會開啟頁面、讓影片播放，抓到影片就自動下載並關閉。

登入過之後可以加 `--headless` 不顯示視窗：

```powershell
python -m ytmusic wechat "網址" --headless
```

其他選項：

| 選項 | 說明 |
| --- | --- |
| `-o DIR` | 輸出資料夾 |
| `--timeout 秒` | 最多等多久（預設 120） |
| `--headless` | 不顯示視窗（要先登入過） |
| `--keep-broken` | 即使抓到的檔案看起來不能播也保留 |
| `--login` | 只開瀏覽器掃碼登入，按 Enter 才關閉 |
| `--browser` | 微信不給影片位址時，開瀏覽器試一次 |
| `--resolver` | 微信不給時改用線上解析代查（會送網址給第三方） |
| `--no-resolver` | 永遠不用線上解析，也不要詢問 |
| `--resolver-url URL` | 自訂線上解析服務位址（可自架） |
| `-y, --yes` | 需要安裝 Playwright／瀏覽器時不詢問，直接裝 |

### 查證過程

| 查了什麼 | 結果 |
| --- | --- |
| 分享頁 `weixin.qq.com/sph/…` 的 HTML | 2,595 bytes 的 JS 外殼，沒有影片位址 |
| 頁面呼叫的 `get_feed_info` API | **不需登入、不需簽章**，直接 POST 就有回應 |
| 從這裡問（美國出口） | `entryScene 64`，只有標題／作者／封面 |
| 從線上解析服務問 | `entryScene 51`，**有 `h264VideoInfo.videoUrl`** |
| 下載那個位址 | 3.0 MB `ftypisom` MP4，44.5 秒，**沒有加密**，直接可播 |
| 頁面播放器程式碼 | `pageMode === "sph"` 時播放被關掉，所以純靠瀏覽器攔截**攔不到** |

所以「開瀏覽器等 120 秒」那條路本來就不會成功 —— 頁面自己不會去要影片。
**直接問 API 才是對的做法**，工具現在就是這樣做。

> ### 還有一條路：攔截微信客戶端流量
>
> [wx_channels_download](https://github.com/ltaoo/wx_channels_download)（本節做法的
> 來源）與 [wechatvideodownload](https://github.com/qiye45/wechatvideodownload) 都能
> 攔截**電腦版微信客戶端**的流量。前者會在視頻號頁面注入下載按鈕，一鍵下載。
>
> 代價是要**安裝根憑證**（等於讓一個程式看得到你所有的加密連線）、代理整台電腦的
> 流量，而且必須開著微信手動播放一次 —— 因此本工具不整合它，只在 API 這條路
> 完全失敗時建議你去用。
>
> **用完務必還原**：停掉代理程式 → `Win+R` 執行 `certmgr.msc`，在「受信任的根憑證
> 授權單位」裡刪掉它裝的憑證 → 刪掉程式資料夾。若關掉後瀏覽器連不上網，
> 到系統設定把「使用 Proxy 伺服器」關掉。

> ### 瀏覽器模式還留著嗎？
>
> 留著，但只在 API 查不到又加了 `--browser` 時才走。已驗過的部分：瀏覽器啟動、
> 頁面載入、請求攔截、來源挑選、下載、檔案格式檢查（用本機伺服器完整跑過，
> 正確攔到 6.4 MB 的 `video/mp4` 並下載成功）。

## 用歌手名稱找歌

只想聽某個歌手的話，加 `-a`（artist）：

```powershell
python -m ytmusic search "周杰倫" -a
```

差別很明顯 —— 一般搜尋會混進歌詞頻道、翻唱和好幾小時的合輯：

```
  1.   Jay Chou 周杰倫【Children of the Sun】Official MV    06:59  周杰倫 Jay Chou
  3. ≡ 周杰倫最好聽的20首歌曲 | 在雨天聽周杰倫…              1:26:32  杰威爾歌詞MV頻道
  4. ≡ 周杰倫歌曲🎧50首精選集【動態滾動歌詞】                3:37:37  大俠人生旅途
```

加了 `-a` 之後**只留下該歌手自己頻道上傳的單曲**：

```
  1.   Jay Chou 周杰倫【Children of the Sun】Official MV    06:59  周杰倫 Jay Chou
  2.   周杰倫 Jay Chou【擱淺 Step Aside】Official MV         04:29  周杰倫 Jay Chou
  3.   周杰倫 Jay Chou【夜曲 Nocturne】Official MV           03:54  周杰倫 Jay Chou
  4.   周杰倫 Jay Chou【青花瓷】Official MV                  04:04  周杰倫 Jay Chou
```

中英文名字都可以（`周杰倫`、`Jay Chou` 都找得到），大小寫和空格不影響。

> 💡 冷門歌手如果頻道名稱跟你打的字差太多，可能篩不到東西；這時工具會自動退回
> 一般搜尋結果，並在畫面上告訴你。

## 下載一首歌

在瀏覽器複製網址，然後：

```powershell
python -m ytmusic dl "貼上網址"
```

就這樣。歌名、歌手、專輯封面都會自動填好。

## 下載整張播放清單

```powershell
python -m ytmusic dl "播放清單網址" --playlist
```

想放進獨立資料夾、而且照順序編號的話：

```powershell
python -m ytmusic dl "播放清單網址" --playlist --playlist-folder
```

> ### 💡 為什麼有時候會問我要單曲還是整張？
>
> YouTube Music 的網址常常長這樣：
>
> ```
> watch?v=abc123&list=RDAMVMabc123
>        ↑ 這首歌      ↑ 一整串清單
> ```
>
> 一個網址裡**兩個都有**，工具不知道你要哪個，所以會問你：
>
> ```
> 要下載哪個？[1] 只要這一首（預設）　[2] 整張播放清單 >
> ```
>
> 直接按 Enter 就是只下載那一首。想要整張就打 `2` 再按 Enter。
>
> 不想每次都被問的話，直接加 `--single` 或 `--playlist`。
>
> ⚠️ 清單代號是 `RD` 開頭的是 YouTube **自動混音**，長度幾乎無限，不建議整張下載。

## 下載影片

加上 `--video` 就會下載影片而不是只抓聲音：

```powershell
python -m ytmusic dl "影片網址" --video
```

這樣會抓**最高畫質**，檔案可能很大。想省空間就指定畫質上限：

```powershell
python -m ytmusic dl "影片網址" --video 1080
```

可選畫質：

| 畫質 | 說明 |
| --- | --- |
| `360` / `480` | 很省空間，手機看夠用 |
| `720` | 一般推薦 |
| `1080` | 電腦螢幕看，畫質好 |
| `1440` / `2160` | 2K / 4K，檔案很大 |
| 不指定 | 有多好就抓多好 |

**關於檔案：**

- 存成 **MP4**，用 H.264 + AAC 編碼 —— Windows 內建播放器、iPhone、剪輯軟體都能直接開
- 檔名一樣會整理好，例如 `Rick Astley - Never Gonna Give You Up.mp4`
- 存放位置跟音樂一樣，見[檔案存到哪裡](#檔案存到哪裡)

> 💡 參考大小：一首 3 分半的歌，720p 約 29 MB、MP3 約 5 MB。

> ⚠️ 下載影片一定要有 ffmpeg（畫面和聲音是分開下載的，要合併）。
> 沒裝的話工具會提醒你，安裝方法見[安裝步驟 3](#步驟-3安裝缺少的東西)。

**播放清單也可以整批下載影片，字幕語言照樣能指定：**

```powershell
python -m ytmusic dl "播放清單網址" --playlist --video 720 --subs 繁中,英
```

不想打指令的話，[雙擊啟動選單](#最簡單的用法雙擊啟動選單)的 `[4] 下載影片`
貼上清單網址，也會一路問你畫質、字幕語言、要不要整張下載。

## 追蹤播放清單，自動補新歌

如果有一張清單你會一直往裡面加歌，可以把它「訂閱」起來：

```powershell
python -m ytmusic sync add "播放清單網址" --name 我的最愛
```

之後**每次只要跑這一行**，就會自動補上新加進去的歌（已經有的不會重下）：

```powershell
python -m ytmusic sync
```

```
=== [1/1] 我的最愛 ===
共 93 首；待下載 3 首，略過 90 首（已下載過）
✔ [1/3] YOASOBI - アイドル
✔ [2/3] Creepy Nuts - Bling-Bang-Bang-Born
✔ [3/3] 周杰倫 - 告白氣球
```

管理訂閱：

```powershell
python -m ytmusic sync list              # 看追蹤了哪些
python -m ytmusic sync remove 我的最愛   # 取消追蹤
python -m ytmusic sync rename 舊名 新名  # 改名
python -m ytmusic sync --dry-run         # 只看會下載什麼，不真的下載
```

每張清單可以有自己的資料夾和格式，加進去的時候設定就好：

```powershell
python -m ytmusic sync add "網址" --name 日文歌 -o "D:\音樂\日文"
python -m ytmusic sync add "網址" --name MV收藏 --video 1080
```

> 💡 訂閱資料存在 `subscriptions.json`，是純文字檔，你可以直接打開來看或改。

## 歌詞與字幕

**下載音樂時一併抓歌詞**，加 `--lyrics`：

```powershell
python -m ytmusic dl "網址" --lyrics
```

會多產生一個 `.lrc` 歌詞檔，內容是帶時間軸的同步歌詞：

```
[ti:Never Gonna Give You Up]
[ar:Rick Astley]

[00:18.64]We're no strangers to love
[00:22.64]You know the rules and so do I
```

同一份歌詞也會寫進 MP3 的標籤裡，所以：

- **支援 LRC 的播放器**（Poweramp、foobar2000、AIMP…）會**跟著音樂捲動**
- 只讀標籤的播放器也看得到歌詞，只是不會捲動

**下載影片時一併嵌入字幕**，加 `--subs`：

```powershell
python -m ytmusic dl "網址" --video 1080 --subs
```

字幕會直接**燒進 MP4 成為獨立字幕軌**，播放時可以自己開關、切換語言。

### 語言

預設會抓這六種（有哪個就抓哪個）：

| 打這個 | 也可以打 |
| --- | --- |
| `繁中` | `zh-TW` |
| `簡中` | `zh-Hans` |
| `英` | `en` |
| `日` | `ja` |
| `韓` | `ko` |
| `西班牙` | `es` |

只想要特定語言的話直接指定：

```powershell
python -m ytmusic dl "網址" --lyrics 繁中,英
python -m ytmusic dl "網址" --video 1080 --subs 日,英
```

想永久改預設：

```powershell
python -m ytmusic config set subtitle_langs "繁中,英"
```

> ⚠️ **不是每支影片都有歌詞。** YouTube Music 的官方音源常常沒有字幕，
> MV 則多半有。抓不到的時候會照常下載音樂，只是在最後提示你「沒有字幕可轉成歌詞」——
> **不會因為沒歌詞就讓整首歌下載失敗。**

> 💡 有人工上傳字幕的優先用人工的，沒有才退而用 YouTube 自動聽寫的
> （自動的準確度看發音，僅供參考）。

## 檔案存到哪裡？

預設在 `C:\Users\你的名字\Music\ytmusic`（Mac 是 `~/Music/ytmusic`）。

想換地方，設定一次就好，以後都會記住：

```powershell
python -m ytmusic config set output_dir "D:\我的音樂"
```

## 想要更好的音質

```powershell
python -m ytmusic config set quality 320
```

設一次就永久生效。（數字越大音質越好、檔案越大，320 是最高。）

---

# 第三部分：遇到問題怎麼辦

## 「找不到 ytmusic 這個指令」

如果你在別的地方看到 `ytmusic dl ...` 這種短寫法，跑出來是：

```
ytmusic : The term 'ytmusic' is not recognized as the name of a cmdlet...
```

那是因為 pip 安裝指令的資料夾沒有加進系統 PATH。**本說明書一律用
`python -m ytmusic`，這個寫法一定能用**，功能完全一樣，不用理會短寫法。

真的想用短寫法的話，跑這行把 pip 的資料夾加進 PATH（只需做一次）：

```powershell
$s = python -c "import sysconfig; print(sysconfig.get_path('scripts', 'nt_user'))"
[Environment]::SetEnvironmentVariable("Path", "$([Environment]::GetEnvironmentVariable('Path','User'));$s", "User")
```

跑完**關掉 PowerShell 再重開**，之後 `ytmusic dl "網址"` 就能用了。

## 雙擊 `下載.bat` 一直跳錯或狂洗畫面

請先更新到最新版：

```powershell
cd ~\YTDownload
git pull
```

舊版的啟動檔把選單文字寫在批次檔裡，cmd.exe 會把中文和換行切碎，變成一直重複的
`'xxx' is not recognized as an internal or external command`。新版的啟動檔只有幾行
純英文，選單改由 Python 顯示，不會再有這個問題。

更新後如果還是說找不到 Python，代表 Python 沒裝好或裝完沒重開視窗，見
[安裝步驟 3](#步驟-3安裝缺少的東西)。

## 「找不到 ffmpeg」

代表步驟 3 沒裝成功，或是**裝完沒有重開 PowerShell**。

```powershell
winget install Gyan.FFmpeg
```

裝完**關掉 PowerShell 再重開**。

## 「Video unavailable」（影片無法使用）

那支影片被刪除、設為私人，或你的地區看不到。換一支試試。

## 「HTTP Error 403」或「需要登入」

有些影片（會員限定、年齡限制）需要登入才能下載。

1. 用 Chrome 登入 YouTube
2. **把 Chrome 完全關掉**（很重要）
3. 加上 `--cookies-from-browser chrome`：

```powershell
python -m ytmusic dl "網址" --cookies-from-browser chrome
```

Chrome 讀不到的話改用 Firefox（Windows 上 Chrome 常常讀不到，這是 Google 的保護機制）。

## 先跑 doctor 讓它告訴你問題在哪

與其照著清單一項項猜，不如讓工具自己測：

```powershell
python -m ytmusic doctor "貼上連不上的那個網址"
```

（不想打指令：雙擊 `下載.bat`，選 `[9]`。）

它會先列出環境，再用**幾種連線方式各試一次同一個網址**，最後給一句結論：

```
環境檢查
  ✔ Python      3.12.1
  ✔ yt-dlp      2026.07.04
  ✔ ffmpeg      C:\ffmpeg\bin\ffmpeg.exe
  ✔ mutagen     1.48.1
  ! curl_cffi   沒有安裝　→　python -m pip install "curl_cffi>=0.10,<0.16"
  ! playwright  沒有安裝（只有微信瀏覽器模式需要）

連線測試：https://lnkd.in/p/XXXXXXXX
  ✖ 一般連線    [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation…
  ✖ 強制 IPv4   [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation…
  ✔ 完整網址    讀得到：Hello, digital twins + Blender lover! | Hans Yang

結論：只有完整網址通得了——被擋的是短網址那個網域本身，不是這個站台。
```

**`curl_cffi` 那行特別重要** —— 它會分清楚是「沒裝」還是「裝了但版本不對」，
這兩種情況 yt-dlp 都只會說「target 不可用」，看不出差別。

## 短網址被擋住

**如果失敗的都是 `lnkd.in`、`bit.ly` 這類短網址，先懷疑短網址本身。**

`lnkd.in` 是 LinkedIn 的轉址網域，因此出現在**大量追蹤器封鎖清單**裡 ——
廣告阻擋、DNS 過濾、防毒的網頁防護都會擋它。這種封鎖多半是看連線裡的網域名稱
直接把它切斷，症狀正是 `UNEXPECTED_EOF`；而同一台電腦連 `linkedin.com`
可能完全正常。

工具會自己處理。連線被切斷時你會看到：

```
  連線被中斷，改用 IPv4，再試一次…
  連線被中斷，把短網址換成完整網址，再試一次…

短網址展開會把這個網址送給第三方服務：
  https://unshorten.me/json/{url}

送出去的只有網址本身，不會送出你的 cookies 或登入資訊。
  要展開短網址再試一次嗎？ [Y/n] Y
    → https://www.linkedin.com/posts/…-ugcPost-7480643058343079937-CDDJ/
  以後遇到短網址都自動展開嗎？ [Y/n] Y
  好，記住了：C:\Users\你的名字\.config\ytmusic\config.json
```

**第二個問題答 `Y` 之後就不會再問了。** 等同於：

```powershell
python -m ytmusic config set expand_short_urls true    # 想取消就設成 false
```

想一開始就不問，或永遠不要用：

```powershell
python -m ytmusic dl "網址" --expand        # 直接展開，不詢問
python -m ytmusic dl "網址" --no-expand     # 永遠不展開，也不詢問
```

`--expander-url` 可以換成自架的展開服務。

自己動手也行：在瀏覽器開那個短網址，複製網址列那串長的 `linkedin.com/posts/...`
直接貼進去，完全不經過第三方。

> ### ⚠️ `curl: (35) TLS connect error … invalid library`
>
> 裝了 `curl_cffi` 之後看到這個錯，那是 **curl_cffi 在 Windows 上的已知問題**，
> 不是你設定錯：
> [yt-dlp#15385](https://github.com/yt-dlp/yt-dlp/issues/15385)、
> [curl_cffi#601](https://github.com/lexiforest/curl_cffi/issues/601) ——
> 兩個 issue 目前都還開著，沒有修法。
>
> 這種情況就別在假扮瀏覽器那條路上耗了，直接用上面的短網址展開。

## SSL 連線被切斷

畫面出現這種訊息：

```
✖ 無法讀取 https://lnkd.in/p/XXXXXXXX：Unable to download webpage:
  [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol
```

**這不是那支影片的問題，是連線在半路被切斷。** 工具會自動依序改用 IPv4、
假扮瀏覽器（若已安裝 curl_cffi）、以及展開短網址。全都不行時再依序試：

| 順序 | 做法 | 為什麼 |
| --- | --- | --- |
| 1 | **直接再跑一次** | 這種斷線常常是暫時的 |
| 2 | **短網址換成完整網址** | 見上一節，這是最常見的成因 |
| 3 | **暫時關掉防毒的「HTTPS／SSL 掃描」** | Avast、Kaspersky、ESET 會拆開 TLS 連線做檢查 |
| 4 | **關掉 VPN／Proxy**，或反過來 `--proxy` 指定一個 | 中間設備是常見兇手 |
| 5 | **換個網路**（手機熱點） | 用來確認是不是這條網路的問題 |

### 只有 LinkedIn 這樣？那多半是 TLS 指紋

如果 YouTube、Bilibili 都正常，只有某個站台連不上，那通常不是你的網路壞了 ——
是**對方在看 TLS 握手的特徵判斷你是不是瀏覽器**，不像就直接把連線切斷。

解法是讓 yt-dlp 假扮成瀏覽器的 TLS 指紋：

```powershell
python -m pip install "curl_cffi>=0.10,<0.16"
```

裝好之後**什麼都不用改** —— 下次遇到連線被切斷時會自動用上。也可以固定啟用：

```powershell
python -m ytmusic config set impersonate chrome
```

> ⚠️ **版本範圍不能省。** yt-dlp 只接受 `0.10 ≤ curl_cffi < 0.16`，
> 直接 `pip install curl_cffi` 會裝到 0.16，然後 yt-dlp 只會說
> 「Impersonate target "chrome" is not available」，完全不提是版本問題。

## 下載很慢或一直失敗

YouTube 常常改東西，工具要跟著更新：

```powershell
pip install -U yt-dlp
```

## 我想看到底出了什麼事

加上 `-v` 會印出完整的錯誤訊息：

```powershell
python -m ytmusic dl "網址" -v
```

## 下載過的我還想再下載一次

工具會記住下載過什麼，第二次跑同一張清單時會自動略過，像這樣：

```
共 90 首；待下載 81 首，略過 9 首（已下載過）
```

想連略過的那些一起重新下載，加 `--force`：

```powershell
python -m ytmusic dl "網址" --playlist --force
```

只想重下其中一首的話，也可以把那筆紀錄刪掉：

```powershell
python -m ytmusic history list          # 找到那首的影片 ID
python -m ytmusic history remove <ID>
```

## 「我喜歡的音樂」或私人清單下載不了

清單代號是 `LM`（我喜歡的音樂）或其他私人清單，是綁在你帳號底下的，
沒有登入就會出現 `HTTP Error 404`。要加上登入資訊：

```powershell
python -m ytmusic dl "https://music.youtube.com/playlist?list=LM" --playlist --cookies-from-browser chrome
```

記得**先把 Chrome 完全關掉**，詳見上面[「HTTP Error 403」或「需要登入」](#http-error-403或需要登入)。

## 怎麼更新這個工具

```powershell
cd ~\YTDownload
git pull
pip install -e .
```

---

# 第四部分：完整選項（進階）

## 下載選項

| 選項 | 說明 |
| --- | --- |
| `-o, --output DIR` | 這次的輸出資料夾 |
| `-f, --format` | `mp3`（預設）/ `m4a` / `opus` / `flac` / `wav` |
| `-q, --quality` | `96`–`320` kbps 或 `best`（預設 `192`） |
| `-j, --jobs N` | 同時下載幾首，預設 3，最多 16 |
| `--video [RES]` | 下載影片，可指定畫質上限 |
| `--lyrics [LANG]` | 下載歌詞，存成 .lrc 並寫進標籤 |
| `--subs [LANG]` | 下載影片時嵌入字幕軌 |
| `--single` | 網址同時含清單時，只要那一首 |
| `--playlist` | 網址同時含清單時，下載整張 |
| `--playlist-folder` | 用清單名稱建資料夾，檔名加上曲序 |
| `--force` | 忽略下載歷史，重新下載 |
| `--dry-run` | 只列出會下載什麼，不真的下載 |
| `--no-convert` | 不轉檔，保留原始音訊（不需要 ffmpeg） |
| `--no-tags` / `--no-cover` | 不寫標籤 / 不放封面 |
| `--no-rename` | 不依標籤改檔名 |
| `--no-history` | 這次不記錄也不讀取歷史 |
| `--cookies-from-browser` | 從瀏覽器讀登入資訊 |
| `--cookies FILE` | 指定 cookies.txt |
| `--proxy URL` | 代理伺服器 |
| `--impersonate [瀏覽器]` | 假扮成瀏覽器的 TLS 指紋（需 curl_cffi） |
| `--expand` | 短網址連不上時直接展開成完整網址，不再詢問 |
| `--no-expand` | 永遠不展開短網址，也不詢問 |
| `--expander-url URL` | 自訂短網址展開服務（可自架） |
| `--rate-limit RATE` | 限速，例如 `500K` |
| `--template TMPL` | 自訂 yt-dlp 檔名樣板（需含 `%(ext)s`） |
| `--no-progress` | 關掉進度列，只輸出純文字 |
| `-v, --verbose` | 顯示完整診斷訊息 |

這些選項 `download`、`search`、`sync` 三個指令都能用。

## 搜尋專屬選項

| 選項 | 說明 |
| --- | --- |
| `-n, --limit N` | 顯示幾筆結果（預設 8，上限 50） |
| `-a, --artist` | 把關鍵字當成歌手名，只留該歌手頻道的單曲 |
| `--site {youtube,bilibili}` | 要搜尋哪個站台（預設 youtube） |
| `--first` | 不詢問，直接抓第一筆（適合寫進腳本） |

## 訂閱同步選項

| 指令 | 說明 |
| --- | --- |
| `sync add URL [--name N] [-o DIR] [--video RES]` | 加入追蹤，可綁定專屬資料夾與畫質 |
| `sync list` | 列出追蹤中的清單 |
| `sync remove NAME` / `sync rename 舊 新` | 取消追蹤 / 改名 |
| `sync [NAME...]` | 同步全部或指定清單 |

## 下載歷史

```powershell
python -m ytmusic history list          # 看下載過什麼（-n 0 顯示全部）
python -m ytmusic history remove <ID>   # 移除某筆，之後可以重新下載
python -m ytmusic history prune         # 清掉檔案已被刪除的紀錄
python -m ytmusic history clear         # 全部清空
```

開頭有 `?` 表示紀錄還在、但檔案已經被移走或刪掉了。

## 預設設定

```powershell
python -m ytmusic config show                        # 看目前設定
python -m ytmusic config set output_dir "D:\Music"   # 改輸出位置
python -m ytmusic config set quality 320             # 改音質
python -m ytmusic config set playlist_folder true    # 清單一律建資料夾
python -m ytmusic config set expand_short_urls true  # 短網址一律自動展開
python -m ytmusic config set impersonate chrome      # 一律假扮瀏覽器連線
python -m ytmusic config reset                       # 還原預設
```

命令列打的選項永遠優先於這裡的設定。

設定檔放在 `~/.config/ytmusic/`。

## 標籤是怎麼判斷的

1. YouTube Music 的曲目自帶歌名／歌手／專輯資料，優先採用
2. 一般影片從標題解析：先拿掉 `(Official Music Video)`、`【官方MV】` 這類字樣，再依 `歌手 - 歌名` 拆開；拆不出來就用頻道名稱當歌手
3. 下載清單時，清單名稱當專輯、順序當曲序
4. 封面取解析度最高的 JPEG，有裝 Pillow 的話會裁成正方形

所以你會拿到 `Rick Astley - Never Gonna Give You Up.mp3`，而不是一長串亂七八糟的檔名。

## 離開狀態碼

| 碼 | 意義 |
| --- | --- |
| 0 | 全部成功 |
| 1 | 全部失敗 |
| 2 | 參數或設定有誤 |
| 3 | 前置條件不足（缺 ffmpeg、缺 yt-dlp、找不到曲目） |
| 4 | 部分成功、部分失敗 |
| 130 | 使用者中斷 |

## 開發

```bash
pip install -e ".[dev]"
python -m pytest
```

323 個測試，不需要網路。涵蓋標題解析、網址判斷、設定讀寫、歷史資料庫、
播放清單攤平、檔名重新命名、字幕轉歌詞、搜尋結果篩選、跨站台相容
（Bilibili 的 BV 號、Vimeo 網址轉換）與選單流程。

---

## ☕ 覺得好用的話

這個工具是免費的，以後也會一直免費。

會做它，是因為想聽的歌散在各個地方，一首一首存太麻煩。做著做著就變成現在這樣了——
能用歌名找、能認歌手、封面歌詞自動填好、清單加了新歌跑一行就補上。

如果它幫你省下了時間，或讓你的音樂資料夾終於整齊了，歡迎請我喝杯咖啡 ☕

<img src="docs/donate-wechat.png" alt="微信讚賞碼" width="240">

**不打賞也完全沒關係，真的。**

你願意用它、願意告訴我哪裡不好用，對我來說就已經很夠了。用得順手的話，
按個 ⭐ 也會讓我開心一整天。

謝謝你看到這裡 🙏

---

# 使用須知

本工具僅供下載你有權利取得的內容 —— 例如你自己的作品、公共領域素材，或授權允許
離線使用的音樂。下載受版權保護的內容可能違反 YouTube 服務條款與當地法律，請自行
確認你的使用方式合法。

用到 `--cookies` 相關功能時請注意：cookies 等同你的 YouTube 登入憑證，別把
`cookies.txt` 傳給任何人或上傳到任何地方。

## 授權

MIT
