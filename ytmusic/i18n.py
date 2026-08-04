"""介面語言。

只翻譯「啟動選單」這一層——也就是雙擊 `下載.bat` 之後看到的所有文字。
下載過程的進度與錯誤訊息還是中文，那是另一批字串，用同一套機制補上即可。

翻譯表刻意攤平成 `{訊息代號: {語言: 文字}}`：一眼就看得出哪個語言少了哪一句，
測試也直接驗得出來（少一句就紅）。繁體中文是原文，缺譯時退回它。
"""

from __future__ import annotations

DEFAULT = "zh-Hant"

# 顯示順序＝選單裡的編號順序。名稱一律用該語言自己的寫法，
# 因為看不懂目前介面語言的人，只認得出自己母語長什麼樣子。
LANGUAGES: tuple[tuple[str, str], ...] = (
    ("zh-Hant", "中文（繁體）"),
    ("ja", "日本語"),
    ("en", "English"),
    ("ko", "한국어"),
    ("es", "Español"),
    ("fi", "Suomi"),
)

LANGUAGE_CODES = tuple(code for code, _ in LANGUAGES)


MESSAGES: dict[str, dict[str, str]] = {
    "app.title": {
        "zh-Hant": "影音下載器",
        "ja": "動画・音楽ダウンローダー",
        "en": "Video & Music Downloader",
        "ko": "영상·음악 다운로더",
        "es": "Descargador de vídeo y música",
        "fi": "Video- ja musiikkilataaja",
    },
    "app.subtitle": {
        "zh-Hant": "YouTube · Bilibili · Vimeo · 微信視頻號 …",
        "ja": "YouTube · Bilibili · Vimeo · WeChat チャンネル …",
        "en": "YouTube · Bilibili · Vimeo · WeChat Channels …",
        "ko": "YouTube · Bilibili · Vimeo · 위챗 채널 …",
        "es": "YouTube · Bilibili · Vimeo · Canales de WeChat …",
        "fi": "YouTube · Bilibili · Vimeo · WeChat-kanavat …",
    },
    "menu.music": {
        "zh-Hant": "下載音樂（任何網站，貼網址）",
        "ja": "音楽をダウンロード（どのサイトでも、URL を貼り付け）",
        "en": "Download music (any site — paste a URL)",
        "ko": "음악 다운로드 (아무 사이트나, URL 붙여넣기)",
        "es": "Descargar música (cualquier sitio: pega una URL)",
        "fi": "Lataa musiikkia (mikä tahansa sivusto – liitä URL)",
    },
    "menu.search_song": {
        "zh-Hant": "用歌名搜尋",
        "ja": "曲名で検索",
        "en": "Search by song title",
        "ko": "곡 제목으로 검색",
        "es": "Buscar por título",
        "fi": "Hae kappaleen nimellä",
    },
    "menu.search_artist": {
        "zh-Hant": "用歌手名稱找歌",
        "ja": "アーティスト名で探す",
        "en": "Find songs by artist",
        "ko": "아티스트 이름으로 찾기",
        "es": "Buscar por artista",
        "fi": "Etsi artistin nimellä",
    },
    "menu.video": {
        "zh-Hant": "下載影片（任何網站，貼網址）",
        "ja": "動画をダウンロード（どのサイトでも、URL を貼り付け）",
        "en": "Download video (any site — paste a URL)",
        "ko": "영상 다운로드 (아무 사이트나, URL 붙여넣기)",
        "es": "Descargar vídeo (cualquier sitio: pega una URL)",
        "fi": "Lataa video (mikä tahansa sivusto – liitä URL)",
    },
    "menu.wechat": {
        "zh-Hant": "下載微信視頻號",
        "ja": "WeChat チャンネルをダウンロード",
        "en": "Download a WeChat Channels video",
        "ko": "위챗 채널 영상 다운로드",
        "es": "Descargar vídeo de Canales de WeChat",
        "fi": "Lataa WeChat-kanavan video",
    },
    "menu.sync": {
        "zh-Hant": "同步追蹤的播放清單",
        "ja": "登録したプレイリストを同期",
        "en": "Sync followed playlists",
        "ko": "구독한 재생목록 동기화",
        "es": "Sincronizar listas seguidas",
        "fi": "Synkronoi seuratut soittolistat",
    },
    "menu.history": {
        "zh-Hant": "看下載過什麼",
        "ja": "ダウンロード履歴を見る",
        "en": "See what you have downloaded",
        "ko": "다운로드 기록 보기",
        "es": "Ver lo que has descargado",
        "fi": "Katso mitä on ladattu",
    },
    "menu.subscribe": {
        "zh-Hant": "追蹤一張新的播放清單",
        "ja": "新しいプレイリストを登録",
        "en": "Follow a new playlist",
        "ko": "새 재생목록 구독",
        "es": "Seguir una lista nueva",
        "fi": "Seuraa uutta soittolistaa",
    },
    "menu.doctor": {
        "zh-Hant": "檢查環境／連線（下載失敗時用）",
        "ja": "環境・接続をチェック（失敗したとき）",
        "en": "Check environment / connection (when downloads fail)",
        "ko": "환경·연결 점검 (다운로드가 실패할 때)",
        "es": "Comprobar entorno / conexión (si falla la descarga)",
        "fi": "Tarkista ympäristö ja yhteys (kun lataus epäonnistuu)",
    },
    "menu.language": {
        "zh-Hant": "切換語言 / Language",
        "ja": "表示言語を変更 / Language",
        "en": "Change language",
        "ko": "언어 변경 / Language",
        "es": "Cambiar idioma / Language",
        "fi": "Vaihda kieli / Language",
    },
    "menu.quit": {
        "zh-Hant": "離開",
        "ja": "終了",
        "en": "Quit",
        "ko": "종료",
        "es": "Salir",
        "fi": "Poistu",
    },
    "prompt.choice": {
        "zh-Hant": "請選擇（直接按 Enter = 1）：",
        "ja": "選んでください（Enter だけで 1）：",
        "en": "Choose (press Enter for 1): ",
        "ko": "선택하세요 (그냥 Enter = 1): ",
        "es": "Elige (Enter = 1): ",
        "fi": "Valitse (Enter = 1): ",
    },
    "prompt.url": {
        "zh-Hant": "貼上網址後按 Enter：",
        "ja": "URL を貼り付けて Enter：",
        "en": "Paste a URL and press Enter: ",
        "ko": "URL을 붙여넣고 Enter: ",
        "es": "Pega una URL y pulsa Enter: ",
        "fi": "Liitä URL ja paina Enter: ",
    },
    "prompt.keyword": {
        "zh-Hant": "要找什麼歌？ ",
        "ja": "どの曲を探しますか？ ",
        "en": "What song are you looking for? ",
        "ko": "어떤 곡을 찾나요? ",
        "es": "¿Qué canción buscas? ",
        "fi": "Mitä kappaletta etsit? ",
    },
    "prompt.artist": {
        "zh-Hant": "歌手名稱？ ",
        "ja": "アーティスト名は？ ",
        "en": "Artist name? ",
        "ko": "아티스트 이름? ",
        "es": "¿Nombre del artista? ",
        "fi": "Artistin nimi? ",
    },
    "prompt.wechat_url": {
        "zh-Hant": "貼上視頻號網址（第一次使用請直接按 Enter 先登入）：",
        "ja": "チャンネルの URL を貼り付け（初回は Enter だけでログイン）：",
        "en": "Paste the Channels URL (first time: press Enter to log in): ",
        "ko": "채널 URL을 붙여넣으세요 (처음이면 Enter로 로그인): ",
        "es": "Pega la URL del canal (la primera vez, Enter para iniciar sesión): ",
        "fi": "Liitä kanavan URL (ensimmäisellä kerralla Enter kirjautumiseen): ",
    },
    "prompt.playlist_url": {
        "zh-Hant": "貼上播放清單網址：",
        "ja": "プレイリストの URL を貼り付け：",
        "en": "Paste the playlist URL: ",
        "ko": "재생목록 URL을 붙여넣으세요: ",
        "es": "Pega la URL de la lista: ",
        "fi": "Liitä soittolistan URL: ",
    },
    "prompt.playlist_name": {
        "zh-Hant": "取個名字（可直接按 Enter 跳過）：",
        "ja": "名前をつける（Enter で省略）：",
        "en": "Give it a name (Enter to skip): ",
        "ko": "이름을 지정하세요 (Enter로 건너뛰기): ",
        "es": "Ponle un nombre (Enter para omitir): ",
        "fi": "Anna sille nimi (Enter ohittaa): ",
    },
    "prompt.doctor_url": {
        "zh-Hant": "要測哪個網址？（可直接按 Enter 只檢查環境）：",
        "ja": "どの URL を試しますか？（Enter で環境チェックのみ）：",
        "en": "Which URL should I test? (Enter = check the environment only): ",
        "ko": "어떤 URL을 테스트할까요? (Enter = 환경만 점검): ",
        "es": "¿Qué URL pruebo? (Enter = solo el entorno): ",
        "fi": "Minkä URL:n testaan? (Enter = vain ympäristö): ",
    },
    "prompt.back": {
        "zh-Hant": "按 Enter 回到選單…",
        "ja": "Enter でメニューに戻ります…",
        "en": "Press Enter to return to the menu… ",
        "ko": "Enter를 누르면 메뉴로 돌아갑니다… ",
        "es": "Pulsa Enter para volver al menú… ",
        "fi": "Paina Enter palataksesi valikkoon… ",
    },
    "paste.hint": {
        "zh-Hant": "（貼上：Windows Terminal 按 Ctrl+V，舊版 PowerShell 按滑鼠右鍵；"
                   "不想繼續請輸入 q）",
        "ja": "（貼り付け：Windows Terminal は Ctrl+V、旧 PowerShell は右クリック。"
              "やめるときは q）",
        "en": "(Paste: Ctrl+V in Windows Terminal, right-click in older PowerShell. "
              "Type q to cancel.)",
        "ko": "(붙여넣기: Windows Terminal은 Ctrl+V, 구버전 PowerShell은 마우스 오른쪽 버튼. "
              "취소하려면 q)",
        "es": "(Pegar: Ctrl+V en Windows Terminal, clic derecho en PowerShell antiguo. "
              "Escribe q para cancelar.)",
        "fi": "(Liittäminen: Windows Terminalissa Ctrl+V, vanhassa PowerShellissä hiiren "
              "oikea painike. Peruuta kirjoittamalla q.)",
    },
    "retry.blank": {
        "zh-Hant": "沒有讀到任何內容，再試一次。",
        "ja": "何も入力されませんでした。もう一度どうぞ。",
        "en": "Nothing came through. Try again.",
        "ko": "아무것도 입력되지 않았습니다. 다시 시도하세요.",
        "es": "No llegó nada. Inténtalo de nuevo.",
        "fi": "Mitään ei tullut. Yritä uudelleen.",
    },
    "ask.lyrics": {
        "zh-Hant": "要一起抓歌詞嗎？",
        "ja": "歌詞も一緒に取得しますか？",
        "en": "Fetch lyrics as well?",
        "ko": "가사도 함께 받을까요?",
        "es": "¿Descargar también la letra?",
        "fi": "Haetaanko myös sanoitukset?",
    },
    "ask.subs": {
        "zh-Hant": "要一起嵌入字幕嗎？",
        "ja": "字幕も埋め込みますか？",
        "en": "Embed subtitles as well?",
        "ko": "자막도 넣을까요?",
        "es": "¿Incrustar también los subtítulos?",
        "fi": "Upotetaanko myös tekstitykset?",
    },
    "ask.folder_each": {
        "zh-Hant": "每張清單收進獨立資料夾嗎？",
        "ja": "プレイリストごとにフォルダを分けますか？",
        "en": "Put each playlist in its own folder?",
        "ko": "재생목록마다 폴더를 나눌까요?",
        "es": "¿Una carpeta separada por lista?",
        "fi": "Oma kansio jokaiselle soittolistalle?",
    },
    "ask.playlist_all": {
        "zh-Hant": "這個網址含整張播放清單，要全部下載嗎？",
        "ja": "この URL にはプレイリスト全体が含まれます。すべてダウンロードしますか？",
        "en": "This URL contains a whole playlist. Download all of it?",
        "ko": "이 URL에는 재생목록 전체가 있습니다. 전부 받을까요?",
        "es": "Esta URL contiene una lista completa. ¿Descargarla entera?",
        "fi": "Tämä URL sisältää koko soittolistan. Ladataanko kaikki?",
    },
    "ask.folder_named": {
        "zh-Hant": "收進以清單命名的資料夾嗎？",
        "ja": "プレイリスト名のフォルダにまとめますか？",
        "en": "Put them in a folder named after the playlist?",
        "ko": "재생목록 이름의 폴더에 넣을까요?",
        "es": "¿Guardarlas en una carpeta con el nombre de la lista?",
        "fi": "Tallennetaanko soittolistan nimiseen kansioon?",
    },
    "yesno.suffix": {
        "zh-Hant": "[y/Enter=不用]",
        "ja": "[y / Enter=いいえ]",
        "en": "[y / Enter = no]",
        "ko": "[y / Enter = 아니요]",
        "es": "[y / Enter = no]",
        "fi": "[y / Enter = ei]",
    },
    "site.where": {
        "zh-Hant": "在哪裡搜尋：",
        "ja": "どこで検索：",
        "en": "Search where:",
        "ko": "어디에서 검색:",
        "es": "Dónde buscar:",
        "fi": "Mistä haetaan:",
    },
    "site.choose": {
        "zh-Hant": "請選擇（直接按 Enter = YouTube）：",
        "ja": "選んでください（Enter だけで YouTube）：",
        "en": "Choose (Enter = YouTube): ",
        "ko": "선택하세요 (Enter = YouTube): ",
        "es": "Elige (Enter = YouTube): ",
        "fi": "Valitse (Enter = YouTube): ",
    },
    "quality.label": {
        "zh-Hant": "畫質：",
        "ja": "画質：",
        "en": "Quality:",
        "ko": "화질:",
        "es": "Calidad:",
        "fi": "Laatu:",
    },
    "quality.best": {
        "zh-Hant": "最高",
        "ja": "最高",
        "en": "Best",
        "ko": "최고",
        "es": "Máxima",
        "fi": "Paras",
    },
    "quality.choose": {
        "zh-Hant": "請選擇（直接按 Enter = 720p）：",
        "ja": "選んでください（Enter だけで 720p）：",
        "en": "Choose (Enter = 720p): ",
        "ko": "선택하세요 (Enter = 720p): ",
        "es": "Elige (Enter = 720p): ",
        "fi": "Valitse (Enter = 720p): ",
    },
    "lang.multi": {
        "zh-Hant": "可複選，用逗號分隔（例如 1,3）",
        "ja": "複数選択可、カンマ区切り（例：1,3）",
        "en": "Multiple allowed, comma-separated (e.g. 1,3)",
        "ko": "여러 개 선택 가능, 쉼표로 구분 (예: 1,3)",
        "es": "Puedes elegir varios, separados por comas (p. ej. 1,3)",
        "fi": "Voit valita useita, erota pilkulla (esim. 1,3)",
    },
    "lang.subs": {
        "zh-Hant": "字幕語言（直接按 Enter = 全部）：",
        "ja": "字幕の言語（Enter だけで全部）：",
        "en": "Subtitle language (Enter = all): ",
        "ko": "자막 언어 (Enter = 전부): ",
        "es": "Idioma de los subtítulos (Enter = todos): ",
        "fi": "Tekstityksen kieli (Enter = kaikki): ",
    },
    "lang.lyrics": {
        "zh-Hant": "歌詞語言（直接按 Enter = 全部）：",
        "ja": "歌詞の言語（Enter だけで全部）：",
        "en": "Lyrics language (Enter = all): ",
        "ko": "가사 언어 (Enter = 전부): ",
        "es": "Idioma de la letra (Enter = todos): ",
        "fi": "Sanoitusten kieli (Enter = kaikki): ",
    },
    # 字幕語言的顯示名稱。送給 --subs 的值仍是中文別名，只有畫面上的字會變。
    "sublang.zh-Hant": {
        "zh-Hant": "繁中", "ja": "繁体字中国語", "en": "Trad. Chinese",
        "ko": "번체 중국어", "es": "Chino trad.", "fi": "Kiina (perint.)",
    },
    "sublang.zh-Hans": {
        "zh-Hant": "簡中", "ja": "簡体字中国語", "en": "Simp. Chinese",
        "ko": "간체 중국어", "es": "Chino simp.", "fi": "Kiina (yksink.)",
    },
    "sublang.en": {
        "zh-Hant": "英", "ja": "英語", "en": "English",
        "ko": "영어", "es": "Inglés", "fi": "Englanti",
    },
    "sublang.ja": {
        "zh-Hant": "日", "ja": "日本語", "en": "Japanese",
        "ko": "일본어", "es": "Japonés", "fi": "Japani",
    },
    "sublang.ko": {
        "zh-Hant": "韓", "ja": "韓国語", "en": "Korean",
        "ko": "한국어", "es": "Coreano", "fi": "Korea",
    },
    "sublang.es": {
        "zh-Hant": "西班牙", "ja": "スペイン語", "en": "Spanish",
        "ko": "스페인어", "es": "Español", "fi": "Espanja",
    },
    "bye": {
        "zh-Hant": "再見。",
        "ja": "さようなら。",
        "en": "Bye.",
        "ko": "안녕히 가세요.",
        "es": "Hasta luego.",
        "fi": "Näkemiin.",
    },
    "interrupted": {
        "zh-Hant": "已中斷。",
        "ja": "中断しました。",
        "en": "Interrupted.",
        "ko": "중단되었습니다.",
        "es": "Interrumpido.",
        "fi": "Keskeytetty.",
    },
    "ui.title": {
        "zh-Hant": "介面語言 / Interface language",
        "ja": "表示言語 / Interface language",
        "en": "Interface language",
        "ko": "인터페이스 언어 / Interface language",
        "es": "Idioma de la interfaz / Interface language",
        "fi": "Käyttöliittymän kieli / Interface language",
    },
    "ui.choose": {
        "zh-Hant": "請選擇（直接按 Enter = 不變）：",
        "ja": "選んでください（Enter で変更なし）：",
        "en": "Choose (Enter = keep current): ",
        "ko": "선택하세요 (Enter = 그대로): ",
        "es": "Elige (Enter = sin cambios): ",
        "fi": "Valitse (Enter = ei muutosta): ",
    },
    "ui.saved": {
        "zh-Hant": "已切換成 {name}。",
        "ja": "{name} に切り替えました。",
        "en": "Switched to {name}.",
        "ko": "{name}(으)로 변경했습니다.",
        "es": "Cambiado a {name}.",
        "fi": "Vaihdettu: {name}.",
    },
    "ui.save_failed": {
        "zh-Hant": "存不起來（{error}）——這次先用著，下次會回到原本的語言。",
        "ja": "保存できませんでした（{error}）——今回のみ有効です。",
        "en": "Couldn't save it ({error}) — using it for this session only.",
        "ko": "저장하지 못했습니다 ({error}) — 이번 실행에만 적용됩니다.",
        "es": "No se pudo guardar ({error}): solo para esta sesión.",
        "fi": "Tallennus epäonnistui ({error}) – käytössä vain tämän kerran.",
    },
    "deps.header": {
        "zh-Hant": "── 缺少一些東西 ──",
        "ja": "── 足りないものがあります ──",
        "en": "── Some things are missing ──",
        "ko": "── 빠진 것이 있습니다 ──",
        "es": "── Faltan algunas cosas ──",
        "fi": "── Jotain puuttuu ──",
    },
    "deps.required": {
        "zh-Hant": "必要", "ja": "必須", "en": "Required",
        "ko": "필수", "es": "Necesario", "fi": "Pakollinen",
    },
    "deps.optional": {
        "zh-Hant": "選用", "ja": "任意", "en": "Optional",
        "ko": "선택", "es": "Opcional", "fi": "Valinnainen",
    },
    "deps.ask": {
        "zh-Hant": "要現在幫你裝嗎？ ",
        "ja": "今インストールしますか？ ",
        "en": "Install them now? ",
        "ko": "지금 설치할까요? ",
        "es": "¿Los instalo ahora? ",
        "fi": "Asennetaanko nyt? ",
    },
    "deps.installing": {
        "zh-Hant": "安裝 {name}…",
        "ja": "{name} をインストールしています…",
        "en": "Installing {name}…",
        "ko": "{name} 설치 중…",
        "es": "Instalando {name}…",
        "fi": "Asennetaan {name}…",
    },
    "deps.running": {
        "zh-Hant": "執行：{command}",
        "ja": "実行：{command}",
        "en": "Running: {command}",
        "ko": "실행: {command}",
        "es": "Ejecutando: {command}",
        "fi": "Suoritetaan: {command}",
    },
    "deps.failed": {
        "zh-Hant": "失敗：{error}",
        "ja": "失敗：{error}",
        "en": "Failed: {error}",
        "ko": "실패: {error}",
        "es": "Error: {error}",
        "fi": "Epäonnistui: {error}",
    },
    "deps.still_missing": {
        "zh-Hant": "這些還是沒裝起來：",
        "ja": "次のものはインストールできませんでした：",
        "en": "These are still missing:",
        "ko": "다음 항목은 여전히 없습니다:",
        "es": "Estos siguen faltando:",
        "fi": "Nämä puuttuvat yhä:",
    },
    "deps.done": {
        "zh-Hant": "裝好了。如果還是說找不到，把視窗關掉重開一次。",
        "ja": "完了しました。まだ見つからないと言われる場合は、ウィンドウを閉じて開き直してください。",
        "en": "Done. If it still says not found, close this window and open it again.",
        "ko": "완료했습니다. 그래도 찾을 수 없다고 하면 창을 닫고 다시 여세요.",
        "es": "Listo. Si aún dice que no lo encuentra, cierra esta ventana y ábrela otra vez.",
        "fi": "Valmis. Jos se yhä sanoo ettei löydy, sulje ikkuna ja avaa se uudelleen.",
    },
    "deps.optional_only": {
        "zh-Hant": "以上都是選用的，不裝也能正常下載。",
        "ja": "上記はすべて任意です。入れなくてもダウンロードはできます。",
        "en": "All of the above are optional — downloading works without them.",
        "ko": "위 항목은 모두 선택 사항이며, 없어도 다운로드는 됩니다.",
        "es": "Todo lo anterior es opcional: la descarga funciona sin ello.",
        "fi": "Kaikki yllä oleva on valinnaista – lataus toimii ilmankin.",
    },
    "dep.why.yt-dlp": {
        "zh-Hant": "沒有它就完全不能下載",
        "ja": "これがないと一切ダウンロードできません",
        "en": "Without it nothing can be downloaded",
        "ko": "이것이 없으면 아무것도 받을 수 없습니다",
        "es": "Sin esto no se puede descargar nada",
        "fi": "Ilman tätä mitään ei voi ladata",
    },
    "dep.why.mutagen": {
        "zh-Hant": "寫不了歌名、歌手與專輯封面",
        "ja": "曲名・アーティスト・アルバムアートを書き込めません",
        "en": "Song title, artist and cover art can't be written",
        "ko": "곡 제목·아티스트·앨범 아트를 쓸 수 없습니다",
        "es": "No se pueden escribir título, artista ni carátula",
        "fi": "Kappaleen nimeä, artistia tai kansikuvaa ei voi kirjoittaa",
    },
    "dep.why.ffmpeg": {
        "zh-Hant": "轉不了 MP3，也合併不了影片的畫面與聲音",
        "ja": "MP3 に変換できず、映像と音声も結合できません",
        "en": "Can't convert to MP3, or merge video picture with sound",
        "ko": "MP3로 변환할 수 없고 영상과 소리를 합칠 수 없습니다",
        "es": "No se puede convertir a MP3 ni unir vídeo y audio",
        "fi": "Ei voi muuntaa MP3:ksi eikä yhdistää kuvaa ja ääntä",
    },
    "dep.why.curl_cffi": {
        "zh-Hant": "部分站台（如 LinkedIn）會擋非瀏覽器的連線，裝了才連得上",
        "ja": "一部のサイト（LinkedIn など）はブラウザ以外の接続を遮断します",
        "en": "Some sites (LinkedIn, for one) block non-browser connections",
        "ko": "일부 사이트(예: LinkedIn)는 브라우저가 아닌 연결을 차단합니다",
        "es": "Algunos sitios (LinkedIn, por ejemplo) bloquean conexiones que no son de navegador",
        "fi": "Jotkin sivustot (esim. LinkedIn) estävät muut kuin selainyhteydet",
    },
}


_current = DEFAULT


def available() -> tuple[tuple[str, str], ...]:
    return LANGUAGES


def language() -> str:
    return _current


def set_language(code: str | None) -> str:
    """切換介面語言。認不得的代號一律忽略，回傳實際生效的語言。"""
    global _current
    if code and code in LANGUAGE_CODES:
        _current = code
    return _current


def language_name(code: str) -> str:
    return dict(LANGUAGES).get(code, code)


def t(key: str, **kwargs) -> str:
    """取一句翻譯。

    缺譯時退回繁體中文，再不行就回代號本身——畫面上出現代號很醜，但比整個
    崩掉好，而且一眼就看得出漏了哪一句。
    """
    entry = MESSAGES.get(key)
    if entry is None:
        return key
    text = entry.get(_current) or entry.get(DEFAULT) or key
    return text.format(**kwargs) if kwargs else text


def detect(env: dict | None = None) -> str:
    """從系統設定猜一個介面語言，猜不到就用英文。

    使用者沒選過語言時才會用到。刻意不猜成中文——看不懂的人比較可能懂英文。
    """
    import os

    env = os.environ if env is None else env
    raw = ""
    for name in ("LC_ALL", "LC_MESSAGES", "LANG", "LANGUAGE"):
        if env.get(name):
            raw = env[name]
            break
    if not raw:
        try:
            import locale

            raw = locale.getdefaultlocale()[0] or ""
        except Exception:
            raw = ""
    return match(raw)


def match(raw: str) -> str:
    """把 `zh_TW.UTF-8`、`ja-JP` 這種字串對到我們支援的語言。"""
    tag = (raw or "").replace("_", "-").split(".")[0].split(":")[0].strip().lower()
    if not tag:
        return "en"
    if tag.startswith("zh"):
        # 簡體圈的使用者看繁體仍然讀得懂，比丟英文給他們好。
        return "zh-Hant"
    for code in LANGUAGE_CODES:
        if tag == code.lower() or tag.split("-")[0] == code.split("-")[0].lower():
            return code
    return "en"
