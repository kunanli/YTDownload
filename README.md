# YTDownload

**v1.2.0** ｜ [更新紀錄](CHANGELOG.md)

把 YouTube、YouTube Music、Bilibili、Vimeo 等 1700 多個網站的影片和音樂下載到電腦裡。歌曲會自動整理好歌名、歌手和專輯封面。

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
| LinkedIn（貼文影片、Learning） | ✅ 需登入 |
| 微信視頻號 | ❌ [有替代工具](#微信視頻號) |

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
| 下載 Vimeo / LinkedIn | `python -m ytmusic dl "網址"` | [看這裡](#vimeolinkedin-與其他站台) |
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
| 看目前設定 | `python -m ytmusic config show` |

### 出問題了？照畫面上的字找

| 畫面上寫 | 怎麼辦 |
| --- | --- |
| `'ytmusic' is not recognized` | [指令要用 `python -m` 開頭](#找不到-ytmusic-這個指令) |
| `找不到 ffmpeg` | [裝 ffmpeg，裝完重開視窗](#找不到-ffmpeg) |
| `Video unavailable` | [那支影片本身有問題](#video-unavailable影片無法使用) |
| `HTTP Error 403`、需要登入 | [要帶瀏覽器登入資訊](#http-error-403或需要登入) |
| `HTTP Error 404`（`list=LM`） | [私人清單一定要登入](#我喜歡的音樂或私人清單下載不了) |
| 雙擊 `.bat` 狂洗畫面 | [舊版問題，更新就好](#雙擊-下載bat-一直跳錯或狂洗畫面) |
| 下載很慢、一直失敗 | [更新 yt-dlp](#下載很慢或一直失敗) |
| 「沒有字幕可轉成歌詞」 | [那支影片沒字幕，正常現象](#歌詞與字幕) |
| 想看完整錯誤訊息 | [指令後面加 `-v`](#我想看到底出了什麼事) |

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
    [3] 用歌手名稱找歌
    [4] 下載影片（貼網址）
    [5] 同步追蹤的播放清單
    [6] 看下載過什麼
    [7] 追蹤一張新的播放清單

    [0] 離開

  請選擇（直接按 Enter = 1）：
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

**貼播放清單網址也可以**——選單會再問要不要整張下載、要不要收進獨立資料夾，
所以「整張清單下載影片 + 指定字幕語言」在選單裡就做得到。

各選項對應的詳細說明：
[① 下載一首歌](#下載一首歌)、
[② 用歌名搜尋](#用歌名搜尋)、
[③ 用歌手名稱找歌](#用歌手名稱找歌)、
[④ 下載影片](#下載影片)、
[⑤⑦ 追蹤播放清單](#追蹤播放清單自動補新歌)、
[⑥ 下載歷史](#下載過的我還想再下載一次)

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
  - [Bilibili](#bilibili)　·　[Vimeo / LinkedIn](#vimeolinkedin-與其他站台)　·　[微信視頻號](#微信視頻號)
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

## Vimeo、LinkedIn 與其他站台

**網址直接貼就好**，用法跟 YouTube 完全一樣：

```powershell
python -m ytmusic dl "https://vimeo.com/76979871" --video 1080
python -m ytmusic dl "https://www.linkedin.com/posts/..." --video 720
```

底層的 yt-dlp 支援 **1700 多個網站**，多數貼上網址就能用。上面列出的是實際驗過的。

> 💡 **Vimeo**：一般頁面要先換 OAuth token，某些網路環境會被回
> `401 Unauthorized`。遇到時工具會**自動改用播放器網址重試**，你不用做任何事。
>
> 💡 **LinkedIn**：多數貼文和 Learning 課程要登入才看得到，記得加
> `--cookies-from-browser chrome`。

## 微信視頻號

**這個工具不支援，但有別的工具做得到** —— 原因值得說清楚。

微信視頻號（`channels.weixin.qq.com`）的影片網址**沒辦法從分享連結推導出來**：

- 分享頁只是一層 JS 外殼（實測整頁只有 2.5 KB），裡面沒有任何影片位址
- 真正的影片位址要靠微信客戶端帶著簽章與 session token 去換，而且串流是加密的
- yt-dlp 支援 1752 個網站，**沒有任何一個對應微信視頻號**

所以「貼上網址就下載」這條路走不通，而本工具整個設計就是建立在這條路上。

### 那要用什麼

有兩款工具做得到，做法都是**攔截流量**而不是解析網址：

| 工具 | 特點 |
| --- | --- |
| [wx_video_download](https://github.com/qiye45/wx_video_download) | 把「下載」按鈕直接注入微信的播放頁面，正常瀏覽時點一下就存檔；支援 Windows / macOS / Linux |
| [wechatvideodownload](https://github.com/qiye45/wechatvideodownload) | 獨立視窗操作，需自行按「開始監聽」與「解密」 |

兩者的共同步驟都是：

1. 以系統管理員身分執行，安裝它的根憑證
2. 啟動本機代理（攔截流量）
3. **開著微信、手動播放那支影片**
4. 工具從流量裡截下影片

卡在**第 3 步**：必須有人真的去播放，這件事無法自動化，也沒辦法塞進
`python -m ytmusic dl <網址>` 這種用法裡。硬要整合，等於在音樂下載器裡塞進
一整套代理與憑證安裝流程，最後還是得你手動操作。

> ⚠️ 這兩款都需要在電腦上**安裝根憑證並代理自己的網路流量**。這是它們能運作的
> 前提，但也代表安裝期間所有 HTTPS 流量都會經過它。要不要接受這個代價由你評估。
>
> **用完務必還原**：停掉代理程式 → `Win+R` 執行 `certmgr.msc`，在「受信任的
> 根憑證授權單位」裡刪掉它裝的憑證（例如 SunnyNet）→ 刪掉程式資料夾。
> 若關掉後瀏覽器連不上網，到系統設定把「使用 Proxy 伺服器」關掉。

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

301 個測試，不需要網路。涵蓋標題解析、網址判斷、設定讀寫、歷史資料庫、
播放清單攤平、檔名重新命名、字幕轉歌詞、搜尋結果篩選與選單流程。

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
