import pytest

from ytmusic.utils import (
    classify_url, clean_title, display_width, human_size, human_time,
    is_radio_playlist, pad_display, parse_browser_spec, sanitize_filename,
    split_artist_title, strip_ansi, strip_topic, truncate, vimeo_player_url,
)


class TestCleanTitle:
    def test_removes_parenthesised_noise(self):
        assert clean_title("Song Name (Official Music Video)") == "Song Name"
        assert clean_title("Song Name (Official Video)") == "Song Name"
        assert clean_title("Song Name [Official Audio]") == "Song Name"
        assert clean_title("Song Name (Lyrics)") == "Song Name"

    def test_removes_cjk_bracket_noise(self):
        assert clean_title("周杰倫【告白氣球 官方MV】") == "周杰倫"
        assert clean_title("告白氣球【Official MV】") == "告白氣球"

    def test_keeps_meaningful_parentheses(self):
        assert clean_title("Song Name (feat. Someone)") == "Song Name (feat. Someone)"
        assert clean_title("Song Name (Acoustic)") == "Song Name (Acoustic)"

    def test_falls_back_to_original_when_everything_stripped(self):
        assert clean_title("(Official Video)") == "(Official Video)"

    def test_handles_empty(self):
        assert clean_title("") == ""


class TestSplitArtistTitle:
    def test_splits_on_hyphen(self):
        assert split_artist_title("Artist - Song") == ("Artist", "Song")

    def test_splits_on_en_dash(self):
        assert split_artist_title("Artist – Song") == ("Artist", "Song")

    def test_strips_noise_before_splitting(self):
        assert split_artist_title("Artist - Song (Official Video)") == ("Artist", "Song")

    def test_keeps_trailing_hyphens_in_title(self):
        assert split_artist_title("A - B - C") == ("A", "B - C")

    def test_cjk_quotes(self):
        assert split_artist_title("周杰倫「告白氣球」") == ("周杰倫", "告白氣球")

    def test_returns_none_artist_when_unsplittable(self):
        artist, title = split_artist_title("JustOneTitle")
        assert artist is None
        assert title == "JustOneTitle"

    def test_pipe_separator(self):
        assert split_artist_title("Artist | Song") == ("Artist", "Song")


class TestStripTopic:
    def test_removes_topic_suffix(self):
        assert strip_topic("Some Artist - Topic") == "Some Artist"

    def test_leaves_other_names_alone(self):
        assert strip_topic("Some Artist") == "Some Artist"


class TestSanitizeFilename:
    def test_replaces_illegal_characters(self):
        assert sanitize_filename('a/b:c*d?e"f<g>h|i') == "a_b_c_d_e_f_g_h_i"

    def test_strips_trailing_dots_and_spaces(self):
        assert sanitize_filename("name. ") == "name"

    def test_escapes_windows_reserved_names(self):
        assert sanitize_filename("CON") == "_CON"
        assert sanitize_filename("com1.mp3").startswith("_")

    def test_truncates(self):
        assert len(sanitize_filename("x" * 500, max_length=20)) == 20

    def test_empty_becomes_placeholder(self):
        assert sanitize_filename("") == "untitled"
        assert sanitize_filename("   ") == "untitled"

    def test_keeps_cjk(self):
        assert sanitize_filename("告白氣球") == "告白氣球"


class TestParseBrowserSpec:
    def test_plain_browser_name(self):
        assert parse_browser_spec("chrome") == ("chrome", None, None, None)

    def test_normalises_case_and_spacing(self):
        assert parse_browser_spec("  Firefox  ") == ("firefox", None, None, None)

    def test_profile(self):
        assert parse_browser_spec("chrome:Profile 1") == ("chrome", "Profile 1", None, None)

    def test_profile_path(self):
        name, profile, _, _ = parse_browser_spec("firefox:~/.mozilla/firefox/abc.default")
        assert (name, profile) == ("firefox", "~/.mozilla/firefox/abc.default")

    def test_keyring(self):
        assert parse_browser_spec("chromium+gnomekeyring") == (
            "chromium", None, "GNOMEKEYRING", None
        )

    def test_container(self):
        assert parse_browser_spec("firefox::Personal") == (
            "firefox", None, None, "Personal"
        )

    def test_profile_and_container(self):
        assert parse_browser_spec("firefox:dev-edition::Work") == (
            "firefox", "dev-edition", None, "Work"
        )

    def test_rejects_empty(self):
        with pytest.raises(ValueError):
            parse_browser_spec("")
        with pytest.raises(ValueError):
            parse_browser_spec("  ")


class TestClassifyUrl:
    def test_plain_video(self):
        assert classify_url("https://www.youtube.com/watch?v=abc") == "video"

    def test_short_link(self):
        assert classify_url("https://youtu.be/abc") == "video"

    def test_music_youtube_video(self):
        assert classify_url("https://music.youtube.com/watch?v=abc") == "video"

    def test_plain_playlist(self):
        assert classify_url("https://www.youtube.com/playlist?list=PL123") == "playlist"

    def test_ambiguous_watch_with_list(self):
        assert classify_url("https://www.youtube.com/watch?v=abc&list=PL123") == "both"

    def test_ambiguous_music_radio(self):
        url = "https://music.youtube.com/watch?v=abc&list=RDAMVMabc"
        assert classify_url(url) == "both"

    def test_ambiguous_short_link(self):
        assert classify_url("https://youtu.be/abc?list=PL123") == "both"

    def test_share_parameter_is_not_a_playlist(self):
        assert classify_url("https://music.youtube.com/watch?v=abc&si=XYZ") == "video"

    def test_non_youtube_is_unknown(self):
        assert classify_url("https://example.com/watch?v=abc&list=PL1") == "unknown"

    def test_channel_url_is_unknown(self):
        assert classify_url("https://www.youtube.com/@someone") == "unknown"


class TestIsRadioPlaylist:
    def test_detects_radio_mix(self):
        assert is_radio_playlist("https://music.youtube.com/watch?v=a&list=RDAMVMa")
        assert is_radio_playlist("https://www.youtube.com/watch?v=a&list=RD123")

    def test_normal_playlist_is_not_radio(self):
        assert not is_radio_playlist("https://www.youtube.com/watch?v=a&list=PL123")

    def test_no_list_is_not_radio(self):
        assert not is_radio_playlist("https://youtu.be/abc")


class TestFormatting:
    def test_human_size(self):
        assert human_size(0) == "--"
        assert human_size(None) == "--"
        assert human_size(512) == "512 B"
        assert human_size(1024) == "1.0 KiB"
        assert human_size(5 * 1024 * 1024) == "5.0 MiB"

    def test_human_time(self):
        assert human_time(None) == "--:--"
        assert human_time(65) == "01:05"
        assert human_time(3725) == "1:02:05"

    def test_truncate(self):
        assert truncate("abcdef", 10) == "abcdef"
        # 省略號本身在中日韓字型下佔 2 欄，所以 4 欄只放得下 2 個字母
        assert truncate("abcdef", 4) == "ab…"


class TestDisplayWidth:
    def test_ascii_is_one_column_each(self):
        assert display_width("abc") == 3

    def test_cjk_is_two_columns_each(self):
        assert display_width("告白氣球") == 8
        assert display_width("マッシュル") == 10

    def test_mixed(self):
        assert display_width("YOASOBI「アイドル」") == 7 + 2 * 6

    def test_block_characters_have_inconsistent_widths(self):
        # 原本的進度列用 █ 當已完成、░ 當未完成，但兩者寬度不同：
        # █ 是 Ambiguous（中日韓下算 2 欄），░ 是 Neutral（1 欄）。
        # 於是同一條 18 格的列會隨著進度從 18 欄長到 36 欄——這就是破版主因，
        # 也是進度列改用純 ASCII 的原因。
        assert display_width("█") == 2
        assert display_width("░") == 1
        assert display_width("#" * 18) == display_width("-" * 18) == 18

    def test_check_marks_are_neutral_width(self):
        # ✔✖ 的 East Asian Width 是 N（單寬）。它們只出現在會自然捲動的
        # 訊息列，不在需要精準對齊的進度區塊裡。
        assert display_width("✔") == 1
        assert display_width("✖") == 1

    def test_combining_marks_take_no_space(self):
        assert display_width("é") == 1

    def test_empty(self):
        assert display_width("") == 0


class TestTruncateDisplayWidth:
    def test_cjk_truncated_by_columns_not_characters(self):
        # 6 欄 = 省略號 2 欄 + 2 個日文字 4 欄
        assert truncate("マッシュル -MASHLE-", 6) == "マッ…"

    def test_result_never_exceeds_requested_width(self):
        title = "Creepy Nuts「Bling-Bang-Bang-Born」×TV Anime「マッシュル -MASHLE-」"
        for width in range(1, 60):
            assert display_width(truncate(title, width)) <= width

    def test_exact_fit_is_untouched(self):
        assert truncate("告白氣球", 8) == "告白氣球"

    def test_too_narrow_for_ellipsis_returns_blanks(self):
        assert truncate("告白氣球", 1) == " "

    def test_zero_width(self):
        assert truncate("abc", 0) == ""


class TestPadDisplay:
    def test_pads_cjk_by_columns(self):
        assert pad_display("告白", 8) == "告白    "  # 4 欄 + 4 空白

    def test_no_padding_when_already_wide_enough(self):
        assert pad_display("abcdef", 3) == "abcdef"


class TestVimeoPlayerUrl:
    def test_plain_video_url(self):
        assert vimeo_player_url("https://vimeo.com/76979871") == (
            "https://player.vimeo.com/video/76979871"
        )

    def test_www_prefix(self):
        assert vimeo_player_url("https://www.vimeo.com/123").endswith("/video/123")

    def test_trailing_slash_and_query(self):
        assert vimeo_player_url("https://vimeo.com/123/?foo=bar") == (
            "https://player.vimeo.com/video/123"
        )

    def test_unlisted_hash_is_preserved(self):
        # 未公開影片少了雜湊就會變成無權觀看
        assert vimeo_player_url("https://vimeo.com/123/abc123def") == (
            "https://player.vimeo.com/video/123?h=abc123def"
        )

    def test_already_a_player_url_returns_none(self):
        assert vimeo_player_url("https://player.vimeo.com/video/123") is None

    def test_non_vimeo_returns_none(self):
        assert vimeo_player_url("https://youtu.be/abc") is None

    def test_channel_url_returns_none(self):
        assert vimeo_player_url("https://vimeo.com/channels/staffpicks") is None

    def test_empty(self):
        assert vimeo_player_url("") is None


class TestStripAnsi:
    """顏色碼跟著訊息一起印出去，會把畫面吃掉一整段。"""

    def test_removes_colour_codes(self):
        assert strip_ansi("\x1b[0;31mERROR:\x1b[0m boom") == "ERROR: boom"

    def test_removes_bare_control_characters(self):
        assert strip_ansi("a\rb\x00c") == "abc"

    def test_keeps_newlines_and_tabs(self):
        assert strip_ansi("a\nb\tc") == "a\nb\tc"

    def test_keeps_plain_text_untouched(self):
        assert strip_ansi("Unsupported URL: https://x/y") == "Unsupported URL: https://x/y"

    def test_handles_empty(self):
        assert strip_ansi("") == "" and strip_ansi(None) == ""


class TestFindJsRuntimes:
    def test_prefers_deno_because_yt_dlp_enables_only_that_by_default(self, monkeypatch):
        from ytmusic.utils import find_js_runtimes

        monkeypatch.setattr("shutil.which",
                            lambda name: f"/bin/{name}" if name in {"deno", "node"} else None)
        assert list(find_js_runtimes()) == ["deno", "node"]

    def test_nothing_installed(self, monkeypatch):
        from ytmusic.utils import find_js_runtimes

        monkeypatch.setattr("shutil.which", lambda name: None)
        assert find_js_runtimes() == {}


class TestYoutubeLoginCookies:
    """YouTube 對「cookies 沒登入」回的訊息跟「你是機器人」一模一樣，所以要自己驗。"""

    def _write(self, tmp_path, *names):
        path = tmp_path / "cookies.txt"
        lines = ["# Netscape HTTP Cookie File"]
        for name in names:
            lines.append(f".youtube.com\tTRUE\t/\tTRUE\t9999999999\t{name}\tvalue")
        path.write_text("\n".join(lines) + "\n")
        return path

    def test_a_real_login_export(self, tmp_path):
        from ytmusic.utils import youtube_login_cookies

        path = self._write(tmp_path, "LOGIN_INFO", "SAPISID", "PREF", "VISITOR_INFO1_LIVE")
        assert youtube_login_cookies(path) == (True, [])

    def test_secure_3papisid_counts_instead_of_sapisid(self, tmp_path):
        from ytmusic.utils import youtube_login_cookies

        path = self._write(tmp_path, "LOGIN_INFO", "__Secure-3PAPISID")
        assert youtube_login_cookies(path)[0]

    def test_not_logged_in_export(self, tmp_path):
        # 沒登入的無痕視窗匯出來的，長這樣：有 cookies，但沒有登入憑證
        from ytmusic.utils import youtube_login_cookies

        path = self._write(tmp_path, "PREF", "VISITOR_INFO1_LIVE", "YSC")
        logged_in, missing = youtube_login_cookies(path)
        assert not logged_in
        assert "LOGIN_INFO" in missing

    def test_login_info_alone_is_not_enough(self, tmp_path):
        from ytmusic.utils import youtube_login_cookies

        assert not youtube_login_cookies(self._write(tmp_path, "LOGIN_INFO"))[0]

    def test_cookies_for_another_site_do_not_count(self, tmp_path):
        # 匯出時分頁不在 youtube.com——最常見的匯錯方式
        from ytmusic.utils import youtube_login_cookies

        path = tmp_path / "cookies.txt"
        path.write_text(".google.com\tTRUE\t/\tTRUE\t9999999999\tLOGIN_INFO\tv\n"
                        ".google.com\tTRUE\t/\tTRUE\t9999999999\tSAPISID\tv\n")
        assert not youtube_login_cookies(path)[0]

    def test_an_unreadable_file_is_not_reported_as_a_problem(self, tmp_path):
        # 這只是輔助檢查，不該擋下本來可能成功的下載
        from ytmusic.utils import youtube_login_cookies

        assert youtube_login_cookies(tmp_path / "nope.txt") == (True, [])


class TestSameSong:
    """全部取自實際跑出來的標題：混音清單裡同一首歌的不同上傳版本。"""

    def _yes(self, wanted, candidate):
        from ytmusic.utils import same_song

        assert same_song(wanted, candidate), f"{wanted!r} 應該對上 {candidate!r}"

    def _no(self, wanted, candidate):
        from ytmusic.utils import same_song

        assert not same_song(wanted, candidate), f"{wanted!r} 不該對上 {candidate!r}"

    def test_uploader_prefixed(self):
        self._yes("ヒカルの碁 OP2　I'll Be The One　Full",
                  "TAKAPON921 - ヒカルの碁 OP2 I'll Be The One Full")

    def test_artist_prefixed(self):
        self._yes("JUST COMMUNICATION", "TWO-MIX - JUST COMMUNICATION")

    def test_suffix_in_the_other_direction(self):
        self._yes("馬渡松子 - 微笑みの爆弾", "微笑みの爆弾 (幽☆遊☆白書の主題歌)")

    def test_official_video_noise_is_ignored(self):
        self._yes("Every Little Thing - Dear My Friend",
                  "「Dear My Friend 」MUSIC VIDEO / Every Little Thing")

    def test_a_different_song_is_rejected(self):
        self._no("My will", "Do As Infinity / Fukai Mori（Deep into the Forest）")

    def test_a_three_hour_medley_is_rejected(self):
        # 抓錯的代價比漏抓高：使用者不會發現，直到播放清單裡冒出四十分鐘的東西
        self._no("Every Heart-ミンナノキモチ-", "90年代アニソンメドレー 3時間耐久 作業用BGM")

    def test_empty_title_never_matches(self):
        self._no("", "隨便什麼")
