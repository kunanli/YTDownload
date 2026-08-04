# YTDownload

**v1.18.0** ｜ [Changelog](CHANGELOG.md) ｜ [繁體中文](README.md)

Download video and music from YouTube, YouTube Music, Bilibili, Vimeo, Facebook and
1700+ other sites. Songs come out with the title, artist and cover art already filled in.

**You don't need to know anything about computers.** Follow the steps below.
Setup is a one-time job, about 10 minutes.

---

## What it can do

| You want | Can it? |
| --- | --- |
| Download a song as MP3 | ✅ |
| Download a whole playlist | ✅ |
| Download video (MP4) | ✅ |
| Fill in title, artist and cover art automatically | ✅ |
| Remember what you downloaded, skip duplicates | ✅ |
| Download lyrics (synced `.lrc`) | ✅ |
| Download subtitles (embedded track) | ✅ |
| Find songs by artist name | ✅ |
| YouTube Music links | ✅ |
| Bilibili (search, collections, favourites) | ✅ |
| Vimeo | ✅ |
| Facebook (videos, Reels) | ✅ public content |
| Instagram (posts, Reels, Stories) | ✅ needs login |
| LinkedIn (post videos, Learning) | ✅ needs login |
| WeChat Channels | ✅ [no certificates, no decryption](#wechat-channels) |
| Interface in 6 languages | ✅ [中文 · 日本語 · English · 한국어 · Español · Suomi](#interface-language) |

---

## 🔍 Quick reference

### I want to…

| I want to | Type this | More |
| --- | --- | --- |
| **Not type commands at all** | double-click `下載.bat` | [here](#the-easy-way-double-click-the-launcher) |
| Download one song | `python -m ytmusic dl "URL"` | [here](#download-one-song) |
| Find a song by name | `python -m ytmusic search "title"` | [here](#search-by-song-title) |
| Find songs by an artist | `python -m ytmusic search "artist" -a` | [here](#find-songs-by-artist) |
| Download from Bilibili | `python -m ytmusic dl "B站 URL"` | [here](#sites) |
| Search Bilibili | `python -m ytmusic search "keyword" --site bilibili` | [here](#sites) |
| Download Vimeo / Facebook | `python -m ytmusic dl "URL"` | [here](#sites) |
| Download Instagram / LinkedIn | `… --cookies-from-browser chrome` | [here](#sites) |
| Download WeChat Channels | `python -m ytmusic wechat "URL"` | [here](#wechat-channels) |
| Download a whole playlist | `python -m ytmusic dl "URL" --playlist` | [here](#download-a-whole-playlist) |
| One folder per playlist | add `--playlist-folder` | [here](#download-a-whole-playlist) |
| Download video | `python -m ytmusic dl "URL" --video 1080` | [here](#download-video) |
| Get lyrics too | add `--lyrics` | [here](#lyrics-and-subtitles) |
| Embed subtitles | add `--subs` | [here](#lyrics-and-subtitles) |
| Pick subtitle/lyrics language | `--subs 繁中,英`, `--lyrics 日` | [here](#languages) |
| Auto-add new playlist items | `python -m ytmusic sync` | [here](#follow-a-playlist) |
| Re-download something | add `--force` | [here](#i-want-to-download-something-again) |
| See download history | `python -m ytmusic history list` | [here](#other-commands) |
| Download something that needs login | add `--cookies-from-browser chrome` | [here](#http-error-403-or-login-required) |
| Preview without downloading | add `--dry-run` | [here](#download-options) |
| Change the interface language | menu option `[L]` | [here](#interface-language) |

### Change a default (set once, applies forever)

| Setting | Command |
| --- | --- |
| Where files go | `python -m ytmusic config set output_dir "D:\Music"` |
| Audio quality | `python -m ytmusic config set quality 320` |
| Lyrics language | `python -m ytmusic config set subtitle_langs "繁中,英"` |
| Parallel downloads | `python -m ytmusic config set concurrency 5` |
| Auto-expand short URLs | `python -m ytmusic config set expand_short_urls true` |
| Interface language | `python -m ytmusic config set ui_language en` |
| Show current settings | `python -m ytmusic config show` |

### Something went wrong — find it by what's on screen

| On screen | What to do |
| --- | --- |
| `'ytmusic' is not recognized` | [Commands start with `python -m`](#ytmusic-is-not-recognized) |
| `找不到 ffmpeg` / ffmpeg not found | [Install ffmpeg, then reopen the window](#ffmpeg-not-found) |
| `Video unavailable` | [Something is wrong with that video](#video-unavailable) |
| `Instagram sent an empty media response` | [Instagram needs login](#sites) |
| `HTTP Error 403`, login required | [Pass your browser login](#http-error-403-or-login-required) |
| `HTTP Error 404` on `list=LM` | [Private playlists always need login](#private-playlists-wont-download) |
| **No idea what's wrong** | [`python -m ytmusic doctor "URL"`](#run-doctor-first) |
| Only `lnkd.in` / `bit.ly` links fail | [The short domain is blocked — use `--expand`](#short-urls-are-blocked) |
| `[SSL: UNEXPECTED_EOF_WHILE_READING]` | [The connection is cut, not the video](#ssl-connection-cut) |
| Only LinkedIn fails, other sites are fine | [Install curl_cffi to mimic a browser](#only-linkedin-fails-thats-probably-tls-fingerprinting) |
| `curl: (35) TLS connect error … invalid library` | [Known curl_cffi bug on Windows](#short-urls-are-blocked) |
| Pasting in the menu does nothing | [Ctrl+V in Windows Terminal, right-click in old PowerShell](#the-easy-way-double-click-the-launcher) |

---

## The easy way: double-click the launcher

### The first double-click sets everything up

`下載.bat` doesn't just open the menu — it makes sure you have a working setup first:

| Step | What it does | If it's missing |
| --- | --- | --- |
| 1 | Look for Python | Tells you to run `winget install Python.Python.3.12`; it won't just close |
| 2 | Check the `ytmusic` package | Runs `pip install -e .` **automatically** (you'll see this on the first run) |
| 3 | Open the menu, which checks yt-dlp / mutagen / ffmpeg / curl_cffi | Lists what's missing and offers to install it |

Step 3 looks like this — **it only appears when something is actually missing**:

```
  ── Some things are missing ──

  [Required] ffmpeg: Can't convert to MP3, or merge video picture with sound
  [Optional] curl_cffi: Some sites (LinkedIn, for one) block non-browser connections

  Install them now? [Y/n]
```

- Only **[Required]** items prompt you; **[Optional]** ones are just listed
- ffmpeg is installed via `winget` (Windows) or `brew` (macOS); on Linux you get the
  command to run yourself (it needs sudo, and this tool won't escalate for you)
- Answer `n` and you get manual steps instead — nothing is forced
- If it still says "not found" afterwards, **close the window and open it again**

macOS users: `下載.command` behaves identically.

### The menu

```
  ================================================
     Video & Music Downloader
     YouTube · Bilibili · Vimeo · WeChat Channels …
  ================================================

    [1] Download music (any site — paste a URL)
    [2] Search by song title
    [3] Find songs by artist
    [4] Download video (any site — paste a URL)
    [5] Download a WeChat Channels video
    [6] Sync followed playlists
    [7] See what you have downloaded
    [8] Follow a new playlist
    [9] Check environment / connection (when downloads fail)
    [L] Change language

    [0] Quit

  Choose (press Enter for 1):
```

Command-line users can open the same menu any time:

```powershell
python -m ytmusic menu
```

### Interface language

The menu speaks **six languages**: 中文（繁體）· 日本語 · English · 한국어 · Español · Suomi.

Press **`[L]`** in the menu:

```
   Interface language

    [1] 中文（繁體）
    [2] 日本語
    [3]*English
    [4] 한국어
    [5] Español
    [6] Suomi

  Choose (Enter = keep current):
```

`*` marks the current one. Your choice is **saved immediately** — no need to pick it again.
The `[L]` entry always contains the word "Language" in every language, so you can find
your way out even if the current interface is unreadable to you.

The very first time you run the menu it asks once, then never again. You can also set it
without the menu:

```powershell
python -m ytmusic config set ui_language en     # zh-Hant, ja, en, ko, es, fi
```

**The command line follows it too** — `dl`, `doctor` and `wechat` all print in your
chosen language:

```
$ python -m ytmusic dl "https://youtu.be/..." --dry-run     # ui_language = ko
URL 분석 중…
총 1개 중 1개 다운로드
출력: /Users/you/Music/ytmusic   형식: mp3 @ 192   동시: 3
```

The **explanations you get when something fails** are translated as well, which is really
the point:

```
$ python -m ytmusic dl "https://example.com/nope"           # ui_language = es
Analizando la URL…
✖ No se pudo leer https://example.com/nope: HTTP Error 404: Not Found
No se encontró nada que descargar.
```

> **Only two things stay untranslated, both on purpose.** The `--help` text for command
> flags (if you're typing commands you're already reading English flag names), and the
> three messages inside `下載.bat` itself — `cmd.exe` mangles non-ASCII before Python
> ever starts.
>
> If you've never picked a language, it **follows your system locale**
> (`LANG=ko_KR.UTF-8` → Korean), falling back to English. An explicit setting always wins.

### How the menu picks a platform

**The paste-a-URL options ([1] and [4]) never ask which site you're on** — YouTube,
Bilibili, Vimeo, Facebook: the tool works it out from the URL. Pasting a WeChat Channels
link is fine too; it's routed automatically.

**Only search ([2] and [3]) asks**, because a keyword doesn't tell you where to search.

> 💡 **Paste not working?** `Ctrl+V` in Windows Terminal, **right-click** in older
> PowerShell. If a paste comes through empty the menu asks again instead of dumping you
> back at the main menu.

---

## Part 1: Install (one time only)

### Windows

**1. Open PowerShell** — press `Win`, type `powershell`, press Enter.

**2. Check what you already have.** Paste this and press Enter:

```powershell
python --version; git --version; ffmpeg -version
```

Three version numbers → skip to step 4. Anything says "not found" → step 3.

**3. Install what's missing:**

```powershell
winget install Python.Python.3.12
winget install Git.Git
winget install Gyan.FFmpeg
```

> ### ⚠️ This is where most people get stuck
>
> When it finishes, **close PowerShell completely and open a new window.**
> Without that, your computer doesn't know where the new programs are and the next
> step will fail.

Then run the step-2 check again. Continue only when all three version numbers appear.

**4. Get the tool:**

```powershell
cd ~
git clone https://github.com/kunanli/YTDownload.git
cd YTDownload
pip install -e .
```

`Successfully installed ytmusic` means it worked.

**5. Test it:**

```powershell
python -m ytmusic dl "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

Files land in `C:\Users\<you>\Music\ytmusic`.

### macOS

```bash
# 1. Homebrew, if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Dependencies
brew install python git ffmpeg

# 3. The tool
cd ~
git clone https://github.com/kunanli/YTDownload.git
cd YTDownload
pip3 install -e .
```

---

## Part 2: Downloading

### Download one song

```powershell
python -m ytmusic dl "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

You get `Rick Astley - Never Gonna Give You Up.mp3`, tagged, with cover art.

### Search by song title

Don't have a URL? Search:

```powershell
python -m ytmusic search "never gonna give you up"
```

Pick with `3`, `1,3,5`, `2-4`, `a` for all, or `q` to quit. `♪` marks official audio,
`≡` marks compilations over 15 minutes.

### Find songs by artist

```powershell
python -m ytmusic search "Rick Astley" -a
```

`-a` keeps only tracks from that artist's own channel — no covers, no 3-hour mixes.

### Download a whole playlist

```powershell
python -m ytmusic dl "PLAYLIST_URL" --playlist
python -m ytmusic dl "PLAYLIST_URL" --playlist --playlist-folder   # one folder per list
```

Already-downloaded tracks are skipped automatically.

### Download video

```powershell
python -m ytmusic dl "URL" --video 1080
```

Quality: `360`, `480`, `720`, `1080`, `1440`, `2160`, or `best`. Output is H.264 + AAC MP4
for maximum compatibility.

### Lyrics and subtitles

```powershell
python -m ytmusic dl "URL" --lyrics              # music + synced .lrc, written into the tags
python -m ytmusic dl "URL" --video 1080 --subs   # video with an embedded subtitle track
```

#### Languages

Six are supported. The values are Chinese aliases because that's what the tool matches on —
they work regardless of your interface language:

| Type this | Language |
| --- | --- |
| `繁中` | Traditional Chinese |
| `簡中` | Simplified Chinese |
| `英` | English |
| `日` | Japanese |
| `韓` | Korean |
| `西班牙` | Spanish |

```powershell
python -m ytmusic dl "URL" --lyrics 繁中,英
python -m ytmusic dl "URL" --video 1080 --subs 日,英
python -m ytmusic config set subtitle_langs "繁中,英"    # make it the default
```

> ⚠️ **Not every video has lyrics.** Official YouTube Music audio often has no subtitles;
> music videos usually do. When there's nothing to fetch you still get the song — the tool
> just says so at the end. **A missing subtitle never fails the download.**

### Follow a playlist

```powershell
python -m ytmusic sync add "PLAYLIST_URL" --name "workout"
python -m ytmusic sync                  # fetch whatever is new
python -m ytmusic sync list
python -m ytmusic sync remove workout
```

### Where files go

`C:\Users\<you>\Music\ytmusic` on Windows, `~/Music/ytmusic` on macOS.

```powershell
python -m ytmusic config set output_dir "D:\My Music"
python -m ytmusic config set quality 320
```

---

## Sites

| Site | Notes |
| --- | --- |
| **YouTube / YouTube Music** | Works out of the box, including playlists and channels |
| **Bilibili** | Video URLs, collections, favourites and uploader lists all expand. Search with `--site bilibili`. Some content is region-locked |
| **Vimeo** | Paste the URL. Some networks get a 401 from Vimeo's token endpoint; the tool retries via `player.vimeo.com` automatically and keeps the private hash |
| **Facebook** | Public videos and Reels work directly |
| **Instagram** | Posts, Reels and Stories work, but almost everything needs `--cookies-from-browser` |
| **LinkedIn** | Both `lnkd.in/p/...` short links and post URLs work, and **public posts need no login**. Copy the **post** URL, not the video URL — see below |
| **WeChat Channels** | See [its own section](#wechat-channels) |

### How to copy a LinkedIn video URL

**Right-clicking the video doesn't help** — LinkedIn greys out "Copy video address".

Use the `•••` menu at the top right of the post → **Copy link to post**. Or click the
timestamp to open the post on its own page and copy the address bar. Facebook and
Instagram work the same way.

### WeChat Channels

**It works, and you get a clean MP4** — no certificates, no system-wide proxy, no decryption.

```powershell
python -m ytmusic wechat "https://weixin.qq.com/sph/XXXXXXXX"
```

```
Asking WeChat about this video…
  三次方AIRX｜虚幻引擎的Codex时刻 …
  Got the video URL — no browser needed.

完成　1.9 MiB
```

How: the share page is a 2,595-byte JavaScript shell, but the `get_feed_info` API behind it
**needs no login and no signature** — just ask it. What comes back is a standard H.264/H.265
MP4 that plays as-is.

#### If it says WeChat returned no video URL

The same request from a different network gets a different answer — WeChat decides per
source (measured: the `entryScene` field comes back `51` with a video URL, `64` without).

| Try | Command |
| --- | --- |
| A different network (phone hotspot, VPN off) | run it again |
| An online resolver | add `--resolver` |
| Actually load the page in a browser | add `--browser` |

> ### ⚠️ `--resolver` sends the URL to a third party
>
> It uses the public service from
> [ltaoo/wx_channels_download](https://github.com/ltaoo/wx_channels_download).
> That service **is not part of this tool** and is outside our control. Only the URL is
> sent — never your cookies or login. You are always asked first; `--no-resolver` disables
> it permanently and `--resolver-url` points at your own deployment.

---

## Part 3: When something goes wrong

### Run doctor first

Instead of guessing your way down a checklist, let the tool measure it:

```powershell
python -m ytmusic doctor "the URL that won't work"
```

(Menu users: double-click `下載.bat`, choose `[9]`.)

It lists your environment, then tries the **same URL several different ways** and tells you
what it concludes:

```
環境檢查
  ✔ Python      3.12.1
  ✔ yt-dlp      2026.07.04
  ✔ ffmpeg      C:\ffmpeg\bin\ffmpeg.exe
  ✔ mutagen     1.48.1
  ! curl_cffi   沒有安裝　→　python -m pip install "curl_cffi>=0.10,<0.16"
  ! playwright  沒有安裝

連線測試：https://lnkd.in/p/XXXXXXXX
  ✖ 一般連線    [SSL: UNEXPECTED_EOF_WHILE_READING] …
  ✖ 強制 IPv4   [SSL: UNEXPECTED_EOF_WHILE_READING] …
  ✔ 完整網址    讀得到：Hello, digital twins + Blender lover! | Hans Yang
```

**The `curl_cffi` line matters most** — it distinguishes "not installed" from "installed but
the wrong version", which yt-dlp reports identically as "target not available".

### Short URLs are blocked

**If everything that fails is an `lnkd.in` or `bit.ly` link, suspect the short domain itself.**

`lnkd.in` is LinkedIn's redirect domain, which puts it on **a lot of tracker blocklists** —
ad blockers, DNS filters and antivirus web shields all block it. That kind of block usually
matches the domain name in the connection and cuts it dead, which looks exactly like
`UNEXPECTED_EOF` — while `linkedin.com` on the very same machine is fine.

The tool handles it. When a connection is cut you'll see:

```
  連線被中斷，改用 IPv4，再試一次…
  連線被中斷，把短網址換成完整網址，再試一次…

  Expand the short URL and retry? [Y/n] Y
    → https://www.linkedin.com/posts/…-ugcPost-7480643058343079937-CDDJ/
  Always expand short URLs from now on? [Y/n] Y
```

**Answer `Y` to the second question and you're never asked again.** Equivalent to:

```powershell
python -m ytmusic config set expand_short_urls true    # false to undo
python -m ytmusic dl "URL" --expand                    # expand, don't ask
python -m ytmusic dl "URL" --no-expand                 # never expand, never ask
```

You can also do it by hand with no third party involved: open the short URL in your browser
and copy the long `linkedin.com/posts/...` address.

> ### ⚠️ `curl: (35) TLS connect error … invalid library`
>
> If you see this after installing `curl_cffi`, it's a **known curl_cffi bug on Windows**,
> not a mistake on your side:
> [yt-dlp#15385](https://github.com/yt-dlp/yt-dlp/issues/15385),
> [curl_cffi#601](https://github.com/lexiforest/curl_cffi/issues/601) — both still open,
> no fix. Don't spend time on the browser-impersonation route; use short-URL expansion above.

### SSL connection cut

```
✖ 無法讀取 https://lnkd.in/p/XXXXXXXX：Unable to download webpage:
  [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol
```

**This isn't the video's fault — the connection was cut mid-handshake.** The tool
automatically retries over IPv4, then with browser impersonation (if `curl_cffi` is
installed), then by expanding the short URL. If all of that fails:

| Order | Do this | Why |
| --- | --- | --- |
| 1 | **Just run it again** | These cuts are often temporary |
| 2 | **Use the full URL instead of the short one** | See the section above — the most common cause |
| 3 | **Turn off your antivirus's HTTPS/SSL scanning** | Avast, Kaspersky and ESET all break TLS open to inspect it |
| 4 | **Turn off VPN/proxy** — or use `--proxy` to set one | Middleboxes are the usual suspect |
| 5 | **Try a different network** (phone hotspot) | Confirms whether it's this network |

#### Only LinkedIn fails? That's probably TLS fingerprinting

If YouTube and Bilibili are fine and only one site fails, your network probably isn't broken —
**the site is judging your TLS handshake** and cutting off anything that doesn't look like a
browser.

```powershell
python -m pip install "curl_cffi>=0.10,<0.16"
```

Nothing else to change: the next cut connection retries with it automatically. To always use it:

```powershell
python -m ytmusic config set impersonate chrome
```

> ⚠️ **Don't drop the version range.** yt-dlp only accepts `0.10 ≤ curl_cffi < 0.16`.
> A plain `pip install curl_cffi` gets you 0.16, and yt-dlp then says
> `Impersonate target "chrome" is not available` without ever mentioning versions.

### `'ytmusic' is not recognized`

Use `python -m ytmusic` instead of bare `ytmusic`. pip's script folder often isn't on
Windows' PATH.

### ffmpeg not found

```powershell
winget install Gyan.FFmpeg      # Windows
brew install ffmpeg             # macOS
```

**Close the window and open a new one afterwards.**

### `Video unavailable`

The video itself is private, deleted or region-locked. Try it in a browser to confirm.

### HTTP Error 403 or login required

```powershell
python -m ytmusic dl "URL" --cookies-from-browser chrome
```

Works with `chrome`, `firefox`, `edge`, `brave`, `safari`. Add a profile if you need one:
`chrome:Profile 2`.

### Private playlists won't download

`list=LM` ("Liked music") and other private playlists always need
`--cookies-from-browser`.

### I want to download something again

```powershell
python -m ytmusic dl "URL" --force
python -m ytmusic history clear      # or wipe the whole history
```

### I want to see what actually happened

```powershell
python -m ytmusic dl "URL" -v
```

### Updating

```powershell
cd ~/YTDownload
git pull
pip install -e .
python -m pip install -U yt-dlp     # sites change; this is the usual fix
```

---

## Part 4: Full options

### Download options

| Option | Meaning |
| --- | --- |
| `-o, --output DIR` | Output folder for this run |
| `-f, --format` | `mp3` (default) / `m4a` / `opus` / `flac` / `wav` |
| `-q, --quality` | `96`–`320` kbps or `best` (default `192`) |
| `-j, --jobs N` | Parallel downloads, default 3, max 16 |
| `--video [RES]` | Download video, optional quality cap |
| `--lyrics [LANG]` | Lyrics as `.lrc`, also written into the tags |
| `--subs [LANG]` | Embed a subtitle track |
| `--single` / `--playlist` | For URLs that are both a video and a playlist |
| `--playlist-folder` | Folder per playlist, track numbers in filenames |
| `--force` | Ignore history, download anyway |
| `--dry-run` | List what would be downloaded, download nothing |
| `--no-convert` | Keep the original audio (no ffmpeg needed) |
| `--no-tags` / `--no-cover` | Skip tags / skip cover art |
| `--no-rename` | Keep yt-dlp's filename template output |
| `--no-history` | Don't read or write history this run |
| `--cookies-from-browser` | Read login from a browser |
| `--cookies FILE` | Use a cookies.txt |
| `--proxy URL` | Proxy server |
| `--impersonate [BROWSER]` | Mimic a browser's TLS fingerprint (needs curl_cffi) |
| `--expand` | Expand short URLs when blocked, without asking |
| `--no-expand` | Never expand short URLs, never ask |
| `--expander-url URL` | Your own short-URL expander |
| `--rate-limit RATE` | Speed cap, e.g. `500K` |
| `--template TMPL` | yt-dlp filename template (must contain `%(ext)s`) |
| `--no-progress` | Plain text output, no progress bar |
| `-v, --verbose` | Full diagnostics |

Available on `download`, `search` and `sync`.

### Other commands

```powershell
python -m ytmusic menu                  # interactive menu
python -m ytmusic doctor "URL"          # diagnose a failure
python -m ytmusic wechat "URL"          # WeChat Channels
python -m ytmusic history list          # what you've downloaded (-n 0 for all)
python -m ytmusic config show
python -m ytmusic config set output_dir "D:\Music"
python -m ytmusic config reset
```

Command-line options always beat config file values. Config lives in `~/.config/ytmusic/`.

### Exit codes

| Code | Meaning |
| --- | --- |
| 0 | Everything succeeded |
| 1 | Everything failed |
| 2 | Bad arguments or settings |
| 3 | Missing prerequisite (no ffmpeg, no yt-dlp, nothing found) |
| 4 | Partial success |
| 130 | Interrupted |

### Development

```bash
pip install -e ".[dev]"
python -m pytest -q
```

---

## ☕ If you find this useful

This tool is free and always will be. If it saved you some time, a coffee is very welcome.

<img src="docs/donate-wechat.png" alt="WeChat tip code" width="240">

---

## Terms of use

Download only what you have the right to download. Respect each site's terms of service and
the copyright of the people who made the content. This tool is for personal, offline use —
what you do with it is your responsibility.

## Licence

MIT
