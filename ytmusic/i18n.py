"""介面語言。

涵蓋使用者實際看得到的文字：選單、提示、下載流程、doctor、微信、短網址展開，
以及失敗時那幾行「解釋」——切了語言卻只有選單變，等於沒切。

不翻的只有兩處，都是刻意的：`--help` 的參數說明（打指令的人本來就在讀英文旗標），
以及 `下載.bat` 自己那三句（cmd.exe 會在 Python 啟動前把非 ASCII 弄壞）。

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


# --------------------------------------------------------------------------
# 第二批：下載流程、doctor、微信、短網址——也就是「解釋」。
# 切了語言卻只有選單變，等於沒切；真正需要看懂的是失敗時的那幾行。
# --------------------------------------------------------------------------

MESSAGES.update({
    "noun.url": {
        "zh-Hant": "網址", "ja": "URL", "en": "the URL",
        "ko": "URL", "es": "la URL", "fi": "URL:ää",
    },
    "dl.resolving": {
        "zh-Hant": "正在解析{what}…",
        "ja": "{what} を解析しています…",
        "en": "Resolving {what}…",
        "ko": "{what} 분석 중…",
        "es": "Analizando {what}…",
        "fi": "Selvitetään {what}…",
    },
    "dl.nothing": {
        "zh-Hant": "沒有找到可下載的曲目。",
        "ja": "ダウンロードできるものが見つかりませんでした。",
        "en": "Nothing found to download.",
        "ko": "다운로드할 수 있는 항목을 찾지 못했습니다.",
        "es": "No se encontró nada que descargar.",
        "fi": "Ladattavaa ei löytynyt.",
    },
    "dl.plan": {
        "zh-Hant": "共 {total} 首；待下載 {pending} 首",
        "ja": "全 {total} 件、うち {pending} 件をダウンロード",
        "en": "{total} found, {pending} to download",
        "ko": "총 {total}개 중 {pending}개 다운로드",
        "es": "{total} en total, {pending} por descargar",
        "fi": "{total} löytyi, {pending} ladataan",
    },
    "dl.plan_skipped": {
        "zh-Hant": "，略過 {n} 首（已下載過）",
        "ja": "、{n} 件はスキップ（ダウンロード済み）",
        "en": ", skipping {n} (already downloaded)",
        "ko": ", {n}개 건너뜀 (이미 받음)",
        "es": ", omitiendo {n} (ya descargados)",
        "fi": ", ohitetaan {n} (jo ladattu)",
    },
    "dl.output": {
        "zh-Hant": "輸出：{dir}　格式：{fmt}　並行：{jobs}",
        "ja": "出力：{dir}　形式：{fmt}　並列：{jobs}",
        "en": "Output: {dir}   Format: {fmt}   Parallel: {jobs}",
        "ko": "출력: {dir}   형식: {fmt}   동시: {jobs}",
        "es": "Salida: {dir}   Formato: {fmt}   En paralelo: {jobs}",
        "fi": "Kohde: {dir}   Muoto: {fmt}   Rinnakkain: {jobs}",
    },
    "fmt.video": {
        "zh-Hant": "mp4 影片", "ja": "mp4 動画", "en": "mp4 video",
        "ko": "mp4 영상", "es": "vídeo mp4", "fi": "mp4-video",
    },
    "fmt.raw": {
        "zh-Hant": "原始音訊", "ja": "元の音声", "en": "original audio",
        "ko": "원본 오디오", "es": "audio original", "fi": "alkuperäinen ääni",
    },
    "fmt.best_video": {
        "zh-Hant": " @ 最佳畫質", "ja": " @ 最高画質", "en": " @ best quality",
        "ko": " @ 최고 화질", "es": " @ máxima calidad", "fi": " @ paras laatu",
    },
    "fmt.max_res": {
        "zh-Hant": " @ 最高 {res}p", "ja": " @ 最大 {res}p", "en": " @ up to {res}p",
        "ko": " @ 최대 {res}p", "es": " @ hasta {res}p", "fi": " @ enintään {res}p",
    },
    "dl.done": {
        "zh-Hant": "完成 {n} 首",
        "ja": "{n} 件 完了",
        "en": "Done: {n}",
        "ko": "{n}개 완료",
        "es": "Listo: {n}",
        "fi": "Valmis: {n}",
    },
    "dl.failed_count": {
        "zh-Hant": "，失敗 {n} 首",
        "ja": "、{n} 件 失敗",
        "en": ", {n} failed",
        "ko": ", {n}개 실패",
        "es": ", {n} con error",
        "fi": ", {n} epäonnistui",
    },
    "dl.total_size": {
        "zh-Hant": "　共 {size}　→ {dir}",
        "ja": "　合計 {size}　→ {dir}",
        "en": "   {size} total   → {dir}",
        "ko": "   총 {size}   → {dir}",
        "es": "   {size} en total   → {dir}",
        "fi": "   yhteensä {size}   → {dir}",
    },
    "dl.cancelled": {
        "zh-Hant": "已取消。", "ja": "キャンセルしました。", "en": "Cancelled.",
        "ko": "취소했습니다.", "es": "Cancelado.", "fi": "Peruttu.",
    },
    "err.unreadable": {
        "zh-Hant": "✖ 無法讀取 {url}：{error}",
        "ja": "✖ {url} を読み取れません：{error}",
        "en": "✖ Couldn't read {url}: {error}",
        "ko": "✖ {url}을(를) 읽을 수 없습니다: {error}",
        "es": "✖ No se pudo leer {url}: {error}",
        "fi": "✖ Ei voitu lukea {url}: {error}",
    },
    "err.unreadable_bare": {
        "zh-Hant": "✖ 無法讀取 {url}",
        "ja": "✖ {url} を読み取れません",
        "en": "✖ Couldn't read {url}",
        "ko": "✖ {url}을(를) 읽을 수 없습니다",
        "es": "✖ No se pudo leer {url}",
        "fi": "✖ Ei voitu lukea {url}",
    },
    "retry.cut": {
        "zh-Hant": "  連線被中斷，{how}，再試一次…",
        "ja": "  接続が切られました。{how}して再試行します…",
        "en": "  Connection cut — retrying: {how}…",
        "ko": "  연결이 끊겼습니다. {how}(으)로 다시 시도합니다…",
        "es": "  Conexión cortada; reintentando: {how}…",
        "fi": "  Yhteys katkaistiin – yritetään uudelleen: {how}…",
    },
    "retry.ipv4": {
        "zh-Hant": "改用 IPv4", "ja": "IPv4 に切り替え", "en": "force IPv4",
        "ko": "IPv4 강제", "es": "forzar IPv4", "fi": "pakota IPv4",
    },
    "retry.impersonate": {
        "zh-Hant": "假扮成瀏覽器的 TLS 指紋",
        "ja": "ブラウザの TLS 指紋を偽装",
        "en": "mimic a browser's TLS fingerprint",
        "ko": "브라우저 TLS 지문 위장",
        "es": "imitar la huella TLS de un navegador",
        "fi": "matki selaimen TLS-sormenjälkeä",
    },
    "retry.expand": {
        "zh-Hant": "把短網址換成完整網址",
        "ja": "短縮 URL を完全な URL に置き換え",
        "en": "swap the short URL for the full one",
        "ko": "단축 URL을 전체 URL로 교체",
        "es": "cambiar la URL corta por la completa",
        "fi": "vaihda lyhyt URL täydelliseen",
    },
    "net.hint": {
        "zh-Hant": """  這是連線的問題，不是那支影片的問題——連到一半被切斷了。依序試：
    1. 直接再跑一次（這種斷線常常是暫時的）
    2. 短網址（lnkd.in、bit.ly…）換成完整網址：在瀏覽器開啟後複製網址列
    3. 暫時關掉防毒軟體的「HTTPS／SSL 掃描」——它會拆開 TLS，常造成這個錯誤
    4. 關掉 VPN／Proxy，或反過來用 --proxy 指定一個
    5. 換個網路（手機熱點）""",
        "ja": """  これは接続の問題で、動画の問題ではありません——途中で切断されました。順に試してください：
    1. もう一度実行する（この種の切断は一時的なことが多い）
    2. 短縮 URL（lnkd.in、bit.ly…）を完全な URL に：ブラウザで開いてアドレスバーをコピー
    3. ウイルス対策の「HTTPS／SSL スキャン」を一時的に切る——TLS を開くのでこの原因になりやすい
    4. VPN／プロキシを切る、または逆に --proxy で指定する
    5. 別のネットワーク（スマホのテザリング）を試す""",
        "en": """  This is a connection problem, not a problem with the video — it was cut mid-way. Try in order:
    1. Just run it again (these cuts are often temporary)
    2. Replace the short URL (lnkd.in, bit.ly…) with the full one: open it in a browser and copy the address bar
    3. Temporarily turn off your antivirus's "HTTPS/SSL scanning" — it breaks TLS open and often causes this
    4. Turn off VPN/proxy, or conversely set one with --proxy
    5. Try a different network (phone hotspot)""",
        "ko": """  이것은 연결 문제이며 영상의 문제가 아닙니다 — 도중에 끊겼습니다. 순서대로 시도하세요:
    1. 그냥 다시 실행 (이런 끊김은 대개 일시적입니다)
    2. 단축 URL(lnkd.in, bit.ly…)을 전체 URL로: 브라우저에서 열고 주소창을 복사
    3. 백신의 "HTTPS/SSL 검사"를 잠시 끄기 — TLS를 열어보므로 이 오류의 흔한 원인입니다
    4. VPN/프록시 끄기, 또는 반대로 --proxy로 지정하기
    5. 다른 네트워크(휴대폰 핫스팟) 사용""",
        "es": """  Es un problema de conexión, no del vídeo: se cortó a mitad. Prueba en este orden:
    1. Vuelve a ejecutarlo (estos cortes suelen ser temporales)
    2. Cambia la URL corta (lnkd.in, bit.ly…) por la completa: ábrela en el navegador y copia la barra de direcciones
    3. Desactiva temporalmente el "análisis HTTPS/SSL" de tu antivirus: abre el TLS y suele causar esto
    4. Desactiva la VPN/proxy, o al revés, indica uno con --proxy
    5. Prueba otra red (datos del móvil)""",
        "fi": """  Tämä on yhteysongelma, ei videon ongelma – yhteys katkesi kesken. Kokeile järjestyksessä:
    1. Aja uudelleen (nämä katkokset ovat usein tilapäisiä)
    2. Vaihda lyhyt URL (lnkd.in, bit.ly…) täydelliseen: avaa selaimessa ja kopioi osoiterivi
    3. Kytke virustorjunnan "HTTPS/SSL-tarkistus" hetkeksi pois – se avaa TLS:n ja aiheuttaa tätä usein
    4. Kytke VPN/välityspalvelin pois – tai päinvastoin, määritä se --proxy-valitsimella
    5. Kokeile toista verkkoa (puhelimen jaettu yhteys)""",
    },
    "doctor.env": {
        "zh-Hant": "環境檢查", "ja": "環境チェック", "en": "Environment check",
        "ko": "환경 점검", "es": "Comprobación del entorno", "fi": "Ympäristön tarkistus",
    },
    "doctor.todo": {
        "zh-Hant": "要處理的：", "ja": "対応が必要：", "en": "Needs attention:",
        "ko": "처리해야 할 것:", "es": "Requiere atención:", "fi": "Vaatii huomiota:",
    },
    "doctor.url_hint": {
        "zh-Hant": "想知道某個網址為什麼連不上，把網址接在後面：",
        "ja": "特定の URL がつながらない理由を調べるには、URL を後ろに付けてください：",
        "en": "To find out why a particular URL won't connect, put it after the command:",
        "ko": "특정 URL이 왜 연결되지 않는지 알아보려면 URL을 뒤에 붙이세요:",
        "es": "Para saber por qué una URL no conecta, ponla después del comando:",
        "fi": "Selvittääksesi miksi tietty URL ei yhdisty, lisää se komennon perään:",
    },
    "doctor.testing": {
        "zh-Hant": "連線測試：{url}", "ja": "接続テスト：{url}", "en": "Connection test: {url}",
        "ko": "연결 테스트: {url}", "es": "Prueba de conexión: {url}",
        "fi": "Yhteystesti: {url}",
    },
    "doctor.trying": {
        "zh-Hant": "  測試 {name}…", "ja": "  {name} をテスト中…", "en": "  Testing {name}…",
        "ko": "  {name} 테스트 중…", "es": "  Probando {name}…", "fi": "  Testataan: {name}…",
    },
    "doctor.readable": {
        "zh-Hant": "讀得到：{title}", "ja": "読み取れました：{title}", "en": "Readable: {title}",
        "ko": "읽었습니다: {title}", "es": "Se pudo leer: {title}", "fi": "Luettavissa: {title}",
    },
    "doctor.conclusion": {
        "zh-Hant": "結論：{text}", "ja": "結論：{text}", "en": "Conclusion: {text}",
        "ko": "결론: {text}", "es": "Conclusión: {text}", "fi": "Johtopäätös: {text}",
    },
    "probe.plain": {
        "zh-Hant": "一般連線", "ja": "通常の接続", "en": "Plain connection",
        "ko": "일반 연결", "es": "Conexión normal", "fi": "Tavallinen yhteys",
    },
    "probe.ipv4": {
        "zh-Hant": "強制 IPv4", "ja": "IPv4 強制", "en": "Forced IPv4",
        "ko": "IPv4 강제", "es": "IPv4 forzado", "fi": "Pakotettu IPv4",
    },
    "probe.impersonate": {
        "zh-Hant": "假扮瀏覽器", "ja": "ブラウザ偽装", "en": "Browser impersonation",
        "ko": "브라우저 위장", "es": "Imitar navegador", "fi": "Selaimen matkinta",
    },
    "probe.full_url": {
        "zh-Hant": "完整網址", "ja": "完全な URL", "en": "Full URL",
        "ko": "전체 URL", "es": "URL completa", "fi": "Täysi URL",
    },
    "conclusion.plain": {
        "zh-Hant": "一般連線就通了。剛才的失敗多半是暫時的，直接重跑下載即可。",
        "ja": "通常の接続で通りました。先ほどの失敗は一時的なものでしょう。もう一度実行してください。",
        "en": "The plain connection worked. The earlier failure was probably temporary — just run the download again.",
        "ko": "일반 연결로 성공했습니다. 앞선 실패는 일시적인 것으로 보입니다. 다시 실행하세요.",
        "es": "La conexión normal funcionó. El fallo anterior fue probablemente temporal: vuelve a ejecutar la descarga.",
        "fi": "Tavallinen yhteys toimi. Aiempi virhe oli luultavasti tilapäinen – aja lataus uudelleen.",
    },
    "conclusion.ipv4": {
        "zh-Hant": "強制 IPv4 才通，代表 IPv6 那條路有問題——下載時會自動改走，不用特別設定。",
        "ja": "IPv4 強制でのみ通りました。IPv6 経路に問題があります——ダウンロード時は自動で切り替わるので設定は不要です。",
        "en": "Only forced IPv4 worked, so your IPv6 route is broken — downloads switch to it automatically, nothing to configure.",
        "ko": "IPv4 강제에서만 성공했습니다. IPv6 경로에 문제가 있습니다 — 다운로드 시 자동으로 전환되므로 설정할 것은 없습니다.",
        "es": "Solo funcionó forzando IPv4: tu ruta IPv6 está rota. Las descargas cambian solas, no hay que configurar nada.",
        "fi": "Vain pakotettu IPv4 toimi, eli IPv6-reittisi on rikki – lataukset vaihtavat siihen automaattisesti, mitään ei tarvitse asettaa.",
    },
    "conclusion.impersonate": {
        "zh-Hant": "只有假扮瀏覽器才通，代表對方在看 TLS 指紋擋非瀏覽器。\n"
                   "  固定用這招：python -m ytmusic config set impersonate chrome",
        "ja": "ブラウザ偽装でのみ通りました。相手が TLS 指紋でブラウザ以外を弾いています。\n"
              "  常に使うには：python -m ytmusic config set impersonate chrome",
        "en": "Only browser impersonation worked — the site judges TLS fingerprints and blocks non-browsers.\n"
              "  Make it permanent: python -m ytmusic config set impersonate chrome",
        "ko": "브라우저 위장에서만 성공했습니다. 상대가 TLS 지문으로 브라우저가 아닌 연결을 막고 있습니다.\n"
              "  계속 사용하려면: python -m ytmusic config set impersonate chrome",
        "es": "Solo funcionó imitando un navegador: el sitio juzga la huella TLS y bloquea lo que no lo sea.\n"
              "  Hazlo permanente: python -m ytmusic config set impersonate chrome",
        "fi": "Vain selaimen matkinta toimi – sivusto arvioi TLS-sormenjäljen ja estää muut kuin selaimet.\n"
              "  Ota pysyvästi käyttöön: python -m ytmusic config set impersonate chrome",
    },
    "conclusion.short_blocked": {
        "zh-Hant": "只有完整網址通得了——被擋的是短網址那個網域本身，不是這個站台。\n"
                   "  下載時加 --expand 會自動換成完整網址。",
        "ja": "完全な URL でのみ通りました——ブロックされているのは短縮 URL のドメイン自体で、サイトではありません。\n"
              "  ダウンロード時に --expand を付ければ自動で置き換わります。",
        "en": "Only the full URL worked — what's blocked is the short-link domain itself, not the site.\n"
              "  Add --expand when downloading and it swaps automatically.",
        "ko": "전체 URL에서만 성공했습니다 — 차단된 것은 단축 URL 도메인 자체이지 사이트가 아닙니다.\n"
              "  다운로드할 때 --expand를 붙이면 자동으로 교체됩니다.",
        "es": "Solo funcionó la URL completa: lo bloqueado es el dominio del acortador, no el sitio.\n"
              "  Añade --expand al descargar y lo cambia solo.",
        "fi": "Vain täysi URL toimi – estetty on lyhytosoitteen verkkotunnus itse, ei sivusto.\n"
              "  Lisää --expand lataukseen, niin vaihto tapahtuu automaattisesti.",
    },
    "conclusion.none": {
        "zh-Hant": "三種方式都連不上。這條網路到這個站台是不通的——"
                   "換個網路（手機熱點）再跑一次 doctor，就能確定是網路還是站台的問題。",
        "ja": "どの方法でも接続できませんでした。このネットワークからこのサイトへは通りません——"
              "別のネットワーク（スマホのテザリング）で doctor をもう一度実行すれば、ネットワークとサイトのどちらの問題か分かります。",
        "en": "Nothing got through. This network can't reach this site — "
              "run doctor again on a different network (phone hotspot) to tell whether it's the network or the site.",
        "ko": "어떤 방법으로도 연결되지 않았습니다. 이 네트워크에서 이 사이트로는 통하지 않습니다 — "
              "다른 네트워크(휴대폰 핫스팟)에서 doctor를 다시 실행하면 네트워크 문제인지 사이트 문제인지 알 수 있습니다.",
        "es": "Nada pasó. Esta red no llega a este sitio: "
              "ejecuta doctor en otra red (datos del móvil) para saber si es la red o el sitio.",
        "fi": "Mikään ei mennyt läpi. Tästä verkosta ei pääse tälle sivustolle – "
              "aja doctor toisessa verkossa (puhelimen jaettu yhteys), niin tiedät onko vika verkossa vai sivustossa.",
    },
    "dep.not_installed": {
        "zh-Hant": "沒有安裝　→　{command}",
        "ja": "未インストール　→　{command}",
        "en": "not installed  →  {command}",
        "ko": "설치되지 않음  →  {command}",
        "es": "no instalado  →  {command}",
        "fi": "ei asennettu  →  {command}",
    },
    "dep.unsupported": {
        "zh-Hant": "{version} 不在 yt-dlp 支援範圍　→　{command}",
        "ja": "{version} は yt-dlp の対応範囲外　→　{command}",
        "en": "{version} is outside yt-dlp's supported range  →  {command}",
        "ko": "{version}은(는) yt-dlp 지원 범위 밖  →  {command}",
        "es": "{version} está fuera del rango admitido por yt-dlp  →  {command}",
        "fi": "{version} ei ole yt-dlp:n tukemalla välillä  →  {command}",
    },
    "dep.usable": {
        "zh-Hant": "{version}　可用（{targets}）",
        "ja": "{version}　利用可能（{targets}）",
        "en": "{version}  available ({targets})",
        "ko": "{version}  사용 가능 ({targets})",
        "es": "{version}  disponible ({targets})",
        "fi": "{version}  käytettävissä ({targets})",
    },
    "dep.load_failed": {
        "zh-Hant": "{version}　但 yt-dlp 載入失敗：{error}",
        "ja": "{version}　しかし yt-dlp が読み込めません：{error}",
        "en": "{version}  but yt-dlp can't load it: {error}",
        "ko": "{version}  하지만 yt-dlp가 불러오지 못함: {error}",
        "es": "{version}  pero yt-dlp no puede cargarlo: {error}",
        "fi": "{version}  mutta yt-dlp ei saa sitä ladattua: {error}",
    },
    "dep.no_targets": {
        "zh-Hant": "沒有可用目標", "ja": "利用可能なターゲットなし", "en": "no targets available",
        "ko": "사용 가능한 대상 없음", "es": "sin objetivos disponibles", "fi": "ei kohteita",
    },
    "dep.ffmpeg_missing": {
        "zh-Hant": "找不到　→　轉檔與影片合併會失敗",
        "ja": "見つかりません　→　変換と動画の結合が失敗します",
        "en": "not found  →  conversion and video merging will fail",
        "ko": "찾을 수 없음  →  변환과 영상 병합이 실패합니다",
        "es": "no encontrado  →  la conversión y la unión de vídeo fallarán",
        "fi": "ei löydy  →  muunnos ja videon yhdistäminen epäonnistuvat",
    },
    "dep.mutagen_missing": {
        "zh-Hant": "沒有安裝　→　寫不了標籤與封面",
        "ja": "未インストール　→　タグとカバーアートを書き込めません",
        "en": "not installed  →  tags and cover art can't be written",
        "ko": "설치되지 않음  →  태그와 앨범 아트를 쓸 수 없습니다",
        "es": "no instalado  →  no se podrán escribir etiquetas ni carátula",
        "fi": "ei asennettu  →  tunnisteita ja kansikuvaa ei voi kirjoittaa",
    },
    "dep.playwright_yes": {
        "zh-Hant": "已安裝（微信瀏覽器模式可用）",
        "ja": "インストール済み（WeChat のブラウザモードが使えます）",
        "en": "installed (WeChat browser mode available)",
        "ko": "설치됨 (위챗 브라우저 모드 사용 가능)",
        "es": "instalado (modo navegador de WeChat disponible)",
        "fi": "asennettu (WeChatin selaintila käytettävissä)",
    },
    "dep.playwright_no": {
        "zh-Hant": "沒有安裝（只有微信瀏覽器模式需要）",
        "ja": "未インストール（WeChat のブラウザモードでのみ必要）",
        "en": "not installed (only needed for WeChat browser mode)",
        "ko": "설치되지 않음 (위챗 브라우저 모드에만 필요)",
        "es": "no instalado (solo hace falta para el modo navegador de WeChat)",
        "fi": "ei asennettu (tarvitaan vain WeChatin selaintilassa)",
    },
    "wx.asking": {
        "zh-Hant": "正在向微信查這支影片…",
        "ja": "WeChat にこの動画を問い合わせています…",
        "en": "Asking WeChat about this video…",
        "ko": "위챗에 이 영상을 조회하는 중…",
        "es": "Consultando este vídeo a WeChat…",
        "fi": "Kysytään WeChatilta tästä videosta…",
    },
    "wx.unknown_author": {
        "zh-Hant": "（未知作者）", "ja": "（作者不明）", "en": "(unknown author)",
        "ko": "(작성자 미상)", "es": "(autor desconocido)", "fi": "(tekijä tuntematon)",
    },
    "wx.untitled": {
        "zh-Hant": "（無標題）", "ja": "（タイトルなし）", "en": "(no title)",
        "ko": "(제목 없음)", "es": "(sin título)", "fi": "(ei otsikkoa)",
    },
    "wx.resolver_asking": {
        "zh-Hant": "正在請線上服務代查…",
        "ja": "オンラインサービスに照会しています…",
        "en": "Asking the online resolver…",
        "ko": "온라인 서비스에 조회하는 중…",
        "es": "Consultando al servicio en línea…",
        "fi": "Kysytään verkkopalvelulta…",
    },
    "wx.resolver_none": {
        "zh-Hant": "  線上服務也沒查到。",
        "ja": "  オンラインサービスでも見つかりませんでした。",
        "en": "  The online resolver didn't find it either.",
        "ko": "  온라인 서비스에서도 찾지 못했습니다.",
        "es": "  El servicio en línea tampoco lo encontró.",
        "fi": "  Verkkopalvelukaan ei löytänyt sitä.",
    },
    "wx.got_url": {
        "zh-Hant": "  拿到影片位址了，不用開瀏覽器。",
        "ja": "  動画の URL を取得しました。ブラウザは不要です。",
        "en": "  Got the video URL — no browser needed.",
        "ko": "  영상 URL을 얻었습니다 — 브라우저가 필요 없습니다.",
        "es": "  Tengo la URL del vídeo: no hace falta navegador.",
        "fi": "  Videon URL saatiin – selainta ei tarvita.",
    },
    "wx.cant": {
        "zh-Hant": "✖ 拿不到：{reason}", "ja": "✖ 取得できません：{reason}",
        "en": "✖ Can't get it: {reason}", "ko": "✖ 가져올 수 없습니다: {reason}",
        "es": "✖ No se puede obtener: {reason}", "fi": "✖ Ei saatu: {reason}",
    },
    "wx.no_url_reason": {
        "zh-Hant": "微信沒有回傳影片位址",
        "ja": "WeChat が動画の URL を返しませんでした",
        "en": "WeChat returned no video URL",
        "ko": "위챗이 영상 URL을 주지 않았습니다",
        "es": "WeChat no devolvió ninguna URL de vídeo",
        "fi": "WeChat ei palauttanut videon URL:ää",
    },
    "wx.found": {
        "zh-Hant": "找到影片，開始下載 → {name}",
        "ja": "動画が見つかりました。ダウンロードを開始 → {name}",
        "en": "Found the video, downloading → {name}",
        "ko": "영상을 찾았습니다. 다운로드 시작 → {name}",
        "es": "Vídeo encontrado, descargando → {name}",
        "fi": "Video löytyi, ladataan → {name}",
    },
    "wx.done": {
        "zh-Hant": "完成　{size}　→ {path}", "ja": "完了　{size}　→ {path}",
        "en": "Done   {size}   → {path}", "ko": "완료   {size}   → {path}",
        "es": "Listo   {size}   → {path}", "fi": "Valmis   {size}   → {path}",
    },
    "wx.dl_failed": {
        "zh-Hant": "下載失敗：{error}", "ja": "ダウンロード失敗：{error}",
        "en": "Download failed: {error}", "ko": "다운로드 실패: {error}",
        "es": "Fallo la descarga: {error}", "fi": "Lataus epäonnistui: {error}",
    },
    "wx.blocked_hint": {
        "zh-Hant": """微信這次沒有把影片位址送回來——只給了標題、作者與封面。

同一支影片換個網路環境問就拿得到，所以這不是「這支影片不能下載」，
比較像是微信按來源決定要不要給。可以試試：

  1. 換個網路（手機熱點、關掉 VPN／Proxy）再跑一次
  2. 加 --resolver 用線上解析服務代查（會把網址送給第三方）
  3. 加 --browser 讓瀏覽器實際載入頁面試一次""",
        "ja": """今回 WeChat は動画の URL を返しませんでした——タイトル・作者・カバーのみです。

同じ動画でもネットワークを変えれば取得できることがあります。つまり
「この動画がダウンロードできない」のではなく、WeChat が接続元によって
出し分けているようです。試せること：

  1. 別のネットワーク（テザリング、VPN／プロキシを切る）でもう一度
  2. --resolver でオンライン解析サービスに照会（URL が第三者に送られます）
  3. --browser で実際にブラウザにページを読み込ませる""",
        "en": """WeChat didn't return a video URL this time — only the title, author and cover.

The same video often works from a different network, so this isn't "this video can't be
downloaded"; WeChat appears to decide based on where the request comes from. Try:

  1. A different network (phone hotspot, VPN/proxy off), then run it again
  2. --resolver to ask an online resolver (this sends the URL to a third party)
  3. --browser to actually load the page in a browser""",
        "ko": """이번에 위챗은 영상 URL을 주지 않았습니다 — 제목·작성자·표지만 왔습니다.

같은 영상도 네트워크를 바꾸면 받아지는 경우가 있습니다. 즉 "이 영상은 받을 수 없다"가
아니라, 위챗이 요청 출처에 따라 다르게 주는 것으로 보입니다. 시도해 보세요:

  1. 다른 네트워크(휴대폰 핫스팟, VPN/프록시 끄기)에서 다시 실행
  2. --resolver 로 온라인 서비스에 조회 (URL이 제3자에게 전송됩니다)
  3. --browser 로 실제 브라우저에서 페이지를 열어보기""",
        "es": """Esta vez WeChat no devolvió una URL de vídeo: solo el título, el autor y la carátula.

El mismo vídeo suele funcionar desde otra red, así que no es que "este vídeo no se pueda
descargar": WeChat parece decidir según de dónde venga la petición. Prueba:

  1. Otra red (datos del móvil, VPN/proxy apagados) y vuelve a ejecutarlo
  2. --resolver para consultar a un servicio en línea (envía la URL a un tercero)
  3. --browser para cargar la página de verdad en un navegador""",
        "fi": """WeChat ei palauttanut videon URL:ää tällä kertaa – vain otsikon, tekijän ja kansikuvan.

Sama video toimii usein toisesta verkosta, joten kyse ei ole siitä ettei videota voi ladata;
WeChat näyttää päättävän sen mukaan mistä pyyntö tulee. Kokeile:

  1. Toinen verkko (puhelimen jaettu yhteys, VPN/välityspalvelin pois) ja aja uudelleen
  2. --resolver kysyäksesi verkkopalvelulta (lähettää URL:n kolmannelle osapuolelle)
  3. --browser ladataksesi sivun oikeasti selaimeen""",
    },
    "wx.resolver_ask": {
        "zh-Hant": "要用線上解析代查嗎？ ", "ja": "オンライン解析に照会しますか？ ",
        "en": "Ask the online resolver? ", "ko": "온라인 서비스에 조회할까요? ",
        "es": "¿Consultar al servicio en línea? ", "fi": "Kysytäänkö verkkopalvelulta? ",
    },
    "short.ask": {
        "zh-Hant": "要展開短網址再試一次嗎？ ",
        "ja": "短縮 URL を展開して再試行しますか？ ",
        "en": "Expand the short URL and retry? ",
        "ko": "단축 URL을 펼쳐서 다시 시도할까요? ",
        "es": "¿Expandir la URL corta y reintentar? ",
        "fi": "Puretaanko lyhyt URL ja yritetään uudelleen? ",
    },
    "short.remember": {
        "zh-Hant": "以後遇到短網址都自動展開嗎？ ",
        "ja": "今後は短縮 URL を自動で展開しますか？ ",
        "en": "Always expand short URLs from now on? ",
        "ko": "앞으로 단축 URL을 항상 자동으로 펼칠까요? ",
        "es": "¿Expandir siempre las URLs cortas a partir de ahora? ",
        "fi": "Puretaanko lyhyet URL:t jatkossa aina? ",
    },
    "short.saved": {
        "zh-Hant": "好，記住了：{path}\n  想取消：python -m ytmusic config set expand_short_urls false",
        "ja": "了解しました。保存先：{path}\n  取り消すには：python -m ytmusic config set expand_short_urls false",
        "en": "Saved: {path}\n  To undo: python -m ytmusic config set expand_short_urls false",
        "ko": "저장했습니다: {path}\n  취소하려면: python -m ytmusic config set expand_short_urls false",
        "es": "Guardado: {path}\n  Para deshacer: python -m ytmusic config set expand_short_urls false",
        "fi": "Tallennettu: {path}\n  Peruaksesi: python -m ytmusic config set expand_short_urls false",
    },
    "short.save_failed": {
        "zh-Hant": "記不起來（{error}）——下次還是會問。",
        "ja": "保存できませんでした（{error}）——次回もお尋ねします。",
        "en": "Couldn't remember it ({error}) — you'll be asked again next time.",
        "ko": "저장하지 못했습니다 ({error}) — 다음에 다시 물어봅니다.",
        "es": "No se pudo recordar ({error}): se te preguntará de nuevo.",
        "fi": "Ei voitu muistaa ({error}) – kysytään ensi kerralla uudelleen.",
    },
})
