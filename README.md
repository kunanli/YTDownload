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
ytmusic dl "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
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
ytmusic dl "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
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

> ### 📌 網址一定要用雙引號 `" "` 包起來
>
> ```powershell
> ytmusic dl "https://..."     ✅ 對
> ytmusic dl https://...       ❌ 錯，網址有 & 的話會壞掉
> ```

## 下載一首歌

在瀏覽器複製網址，然後：

```powershell
ytmusic dl "貼上網址"
```

就這樣。歌名、歌手、專輯封面都會自動填好。

## 下載整張播放清單

```powershell
ytmusic dl "播放清單網址" --playlist
```

想放進獨立資料夾、而且照順序編號的話：

```powershell
ytmusic dl "播放清單網址" --playlist --playlist-folder
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

```powershell
ytmusic dl "影片網址" --video
```

想省空間就限制畫質：

```powershell
ytmusic dl "影片網址" --video 720
```

可選畫質：`360`、`480`、`720`、`1080`、`1440`、`2160`

影片存成 MP4，用的是相容性最好的編碼，Windows 內建播放器就能直接開。

## 檔案存到哪裡？

預設在 `C:\Users\你的名字\Music\ytmusic`（Mac 是 `~/Music/ytmusic`）。

想換地方，設定一次就好，以後都會記住：

```powershell
ytmusic config set output_dir "D:\我的音樂"
```

## 想要更好的音質

```powershell
ytmusic config set quality 320
```

設一次就永久生效。（數字越大音質越好、檔案越大，320 是最高。）

---

# 第三部分：遇到問題怎麼辦

## 「找不到 ytmusic 這個指令」

改用這個寫法，功能完全一樣：

```powershell
python -m ytmusic dl "網址"
```

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
ytmusic dl "網址" --cookies-from-browser chrome
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
ytmusic dl "網址" -v
```

## 同一首歌想重新下載

工具會記住下載過什麼，預設不會重複下載。想強制重下：

```powershell
ytmusic dl "網址" --force
```

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
ytmusic history list          # 看下載過什麼（-n 0 顯示全部）
ytmusic history remove <ID>   # 移除某筆，之後可以重新下載
ytmusic history prune         # 清掉檔案已被刪除的紀錄
ytmusic history clear         # 全部清空
```

開頭有 `?` 表示紀錄還在、但檔案已經被移走或刪掉了。

## 預設設定

```powershell
ytmusic config show                        # 看目前設定
ytmusic config set output_dir "D:\Music"   # 改輸出位置
ytmusic config set quality 320             # 改音質
ytmusic config set playlist_folder true    # 清單一律建資料夾
ytmusic config reset                       # 還原預設
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
