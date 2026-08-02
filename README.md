# YTDownload

把 YouTube 和 YouTube Music 的東西下載到電腦裡。歌曲會自動整理好歌名、歌手和專輯封面。

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
| YouTube Music 的網址 | ✅ |

---

## 最簡單的用法：雙擊啟動選單

裝好之後，**不想打指令的話，直接在資料夾裡雙擊
[`下載.bat`](%E4%B8%8B%E8%BC%89.bat)**（Mac 是
[`下載.command`](%E4%B8%8B%E8%BC%89.command)），會跳出選單：

```
  ============================================
     YouTube 音樂下載器
  ============================================

    [1] 下載音樂（貼網址）
    [2] 用歌名搜尋
    [3] 下載影片（貼網址）
    [4] 同步追蹤的播放清單
    [5] 看下載過什麼
    [6] 追蹤一張新的播放清單

    [0] 離開

  請選擇（直接按 Enter = 1）：
```

各選項對應的詳細說明：
[① 下載一首歌](#下載一首歌)、
[② 用歌名搜尋](#用歌名搜尋)、
[③ 下載影片](#下載影片)、
[④⑥ 追蹤播放清單](#追蹤播放清單自動補新歌)、
[⑤ 下載歷史](#下載過的我還想再下載一次)

貼上網址、按 Enter，就開始下載。完全不用碰 PowerShell。

打指令的人也可以隨時叫出同一個選單：

```powershell
python -m ytmusic menu
```

## 懶人包：四個最常用的指令

想打指令的話，你要的大概就是這幾行其中一行：

```powershell
# 不知道網址？直接用歌名搜尋
python -m ytmusic search "告白氣球"

# 下載一首歌（MP3）
python -m ytmusic dl "網址"

# 下載整張播放清單
python -m ytmusic dl "網址" --playlist --playlist-folder

# 下載影片（MP4，可指定畫質）
python -m ytmusic dl "網址" --video 1080
```

還沒安裝 → 往下看 [第一部分：安裝](#第一部分安裝只需做一次)

---

## 目錄

- [**雙擊啟動選單**](#最簡單的用法雙擊啟動選單) — 不用打任何指令
- [第一部分：安裝](#第一部分安裝只需做一次) — Windows / macOS，只需做一次
- [第二部分：開始下載](#第二部分開始下載)
  - [**用歌名搜尋**](#用歌名搜尋)
  - [下載一首歌](#下載一首歌)
  - [下載整張播放清單](#下載整張播放清單)
  - [**下載影片**](#下載影片)
  - [**追蹤播放清單，自動補新歌**](#追蹤播放清單自動補新歌)
  - [檔案存到哪裡](#檔案存到哪裡)
- [第三部分：遇到問題怎麼辦](#第三部分遇到問題怎麼辦)
- [第四部分：完整選項](#第四部分完整選項進階)

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
  3.   告白氣球-周杰倫（周二珂 cover）             03:33  老司機

  ♪ = 官方音源（音質通常最好）

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

**播放清單也可以整批下載影片：**

```powershell
python -m ytmusic dl "播放清單網址" --playlist --video 720
```

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
| `--rate-limit RATE` | 限速，例如 `500K` |
| `-v, --verbose` | 顯示完整診斷訊息 |

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

156 個測試，不需要網路。涵蓋標題解析、網址判斷、設定讀寫、歷史資料庫、
播放清單攤平、檔名重新命名與影片格式選擇。

---

# 使用須知

本工具僅供下載你有權利取得的內容 —— 例如你自己的作品、公共領域素材，或授權允許
離線使用的音樂。下載受版權保護的內容可能違反 YouTube 服務條款與當地法律，請自行
確認你的使用方式合法。

用到 `--cookies` 相關功能時請注意：cookies 等同你的 YouTube 登入憑證，別把
`cookies.txt` 傳給任何人或上傳到任何地方。

## 授權

MIT
