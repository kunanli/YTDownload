import pytest
from pathlib import Path

from ytmusic.config import Config
from ytmusic.downloader import (
    Downloader, Track, _CollectingLogger, _clean_error_text, _fallback_url,
    _final_path, _parse_rate, _rename_from_meta, _short_error, _unique_path,
    Result, _walk, _is_network_error, _extract_over_ipv4, NETWORK_HINT,
    CURL_CFFI_SPEC, IMPERSONATE_HINT, RADIO_DEFAULT_MAX, BLOCKED_ABORT_AFTER,
    is_blocked_error, is_cookie_error,
)
from ytmusic.history import History
from ytmusic.tagger import TrackMeta


class TestWalk:
    def test_single_video(self):
        tracks = _walk({"id": "abc", "title": "Song", "webpage_url": "https://youtu.be/abc"})
        assert len(tracks) == 1
        assert tracks[0].video_id == "abc"
        assert tracks[0].url == "https://youtu.be/abc"

    def test_constructs_url_when_missing(self):
        assert _walk({"id": "abc", "title": "S"})[0].url.endswith("watch?v=abc")

    def test_playlist_flattens_and_numbers_entries(self):
        info = {
            "_type": "playlist",
            "title": "My Mix",
            "playlist_count": 2,
            "entries": [
                {"id": "a", "title": "One", "url": "https://youtu.be/a"},
                {"id": "b", "title": "Two", "url": "https://youtu.be/b"},
            ],
        }
        tracks = _walk(info)
        assert [t.video_id for t in tracks] == ["a", "b"]
        assert [t.playlist_index for t in tracks] == [1, 2]
        assert all(t.playlist_title == "My Mix" for t in tracks)
        assert all(t.playlist_count == 2 for t in tracks)

    def test_nested_playlists(self):
        info = {
            "_type": "playlist", "title": "Channel",
            "entries": [
                {"_type": "playlist", "title": "Inner",
                 "entries": [{"id": "a", "title": "One"}]},
                {"id": "b", "title": "Two"},
            ],
        }
        tracks = _walk(info)
        assert [t.video_id for t in tracks] == ["a", "b"]
        assert tracks[0].playlist_title == "Inner"

    def test_skips_empty_entries(self):
        info = {"_type": "playlist", "entries": [None, {"id": "a", "title": "One"}]}
        assert [t.video_id for t in _walk(info)] == ["a"]

    def test_skips_unexpanded_playlist_references(self):
        info = {"_type": "url", "ie_key": "YoutubeTab", "id": "UC123"}
        assert _walk({"_type": "playlist", "entries": [info]}) == []

    def test_entry_without_id_is_dropped(self):
        assert _walk({"title": "no id"}) == []


class TestFinalPath:
    def test_reads_requested_downloads(self):
        info = {"requested_downloads": [{"filepath": "/music/song.mp3"}]}
        assert _final_path(info) == Path("/music/song.mp3")

    def test_falls_back_to_filename(self):
        assert _final_path({"_filename": "/music/song.webm"}) == Path("/music/song.webm")

    def test_returns_none_when_unknown(self):
        assert _final_path({}) is None


class TestParseRate:
    def test_suffixes(self):
        assert _parse_rate("500K") == 500 * 1024
        assert _parse_rate("1.5M") == int(1.5 * 1024 ** 2)
        assert _parse_rate("2G") == 2 * 1024 ** 3
        assert _parse_rate("1000") == 1000
        assert _parse_rate("500KB") == 500 * 1024

    def test_invalid(self):
        assert _parse_rate("fast") is None
        assert _parse_rate("") is None


class TestFilterNew:
    def _downloader(self, tmp_path, history, **overrides):
        config = Config(output_dir=tmp_path, **overrides)
        return Downloader(config, history=history)

    def test_splits_by_history(self, tmp_path):
        with History(tmp_path / "h.db") as history:
            history.add("seen")
            downloader = self._downloader(tmp_path, history)
            tracks = [Track("seen", "u", "A"), Track("fresh", "u", "B")]
            pending, skipped = downloader.filter_new(tracks)
            assert [t.video_id for t in pending] == ["fresh"]
            assert [t.video_id for t in skipped] == ["seen"]

    def test_force_ignores_history(self, tmp_path):
        with History(tmp_path / "h.db") as history:
            history.add("seen")
            downloader = self._downloader(tmp_path, history)
            pending, skipped = downloader.filter_new([Track("seen", "u", "A")], force=True)
            assert len(pending) == 1
            assert skipped == []

    def test_history_disabled(self, tmp_path):
        downloader = self._downloader(tmp_path, None, use_history=False)
        pending, skipped = downloader.filter_new([Track("seen", "u", "A")])
        assert len(pending) == 1
        assert skipped == []


class TestOptions:
    def test_postprocessor_uses_configured_codec(self, tmp_path):
        config = Config(output_dir=tmp_path, audio_format="flac", quality="320")
        pps = Downloader(config)._postprocessors()
        assert pps[0]["preferredcodec"] == "flac"
        assert pps[0]["preferredquality"] == "320"

    def test_best_quality_maps_to_vbr_zero(self, tmp_path):
        config = Config(output_dir=tmp_path, quality="best")
        assert Downloader(config)._postprocessors()[0]["preferredquality"] == "0"

    def test_no_convert_means_no_postprocessors(self, tmp_path):
        config = Config(output_dir=tmp_path, convert=False)
        assert Downloader(config)._postprocessors() == []

    def test_outtmpl_uses_playlist_subfolder(self, tmp_path):
        config = Config(output_dir=tmp_path, playlist_folder=True)
        track = Track("a", "u", "t", playlist_title="My: Mix")
        tmpl = Downloader(config)._outtmpl(track)
        assert "My_ Mix" in tmpl
        assert (tmp_path / "My_ Mix").is_dir()

    def test_outtmpl_without_playlist(self, tmp_path):
        config = Config(output_dir=tmp_path, playlist_folder=True)
        tmpl = Downloader(config)._outtmpl(Track("a", "u", "t"))
        assert tmpl == str(tmp_path / config.filename_template)

    def test_base_opts_carry_network_settings(self, tmp_path):
        config = Config(output_dir=tmp_path, proxy="socks5://127.0.0.1:1080",
                        rate_limit="500K", cookies_from_browser="firefox")
        opts = Downloader(config)._base_opts()
        assert opts["proxy"] == "socks5://127.0.0.1:1080"
        assert opts["ratelimit"] == 500 * 1024
        assert opts["cookiesfrombrowser"] == ("firefox", None, None, None)

    def test_base_opts_parse_browser_profile(self, tmp_path):
        config = Config(output_dir=tmp_path, cookies_from_browser="chrome:Profile 1")
        opts = Downloader(config)._base_opts()
        assert opts["cookiesfrombrowser"] == ("chrome", "Profile 1", None, None)


class TestRenameFromMeta:
    def _file(self, tmp_path, name="raw.mp3"):
        path = tmp_path / name
        path.write_bytes(b"audio")
        return path

    def test_renames_to_artist_and_title(self, tmp_path):
        path = self._file(tmp_path)
        result = _rename_from_meta(path, TrackMeta(title="Song", artist="Artist"))
        assert result.name == "Artist - Song.mp3"
        assert result.is_file()
        assert not path.exists()

    def test_title_only_when_artist_unknown(self, tmp_path):
        result = _rename_from_meta(self._file(tmp_path), TrackMeta(title="Song"))
        assert result.name == "Song.mp3"

    def test_adds_track_number_when_requested(self, tmp_path):
        meta = TrackMeta(title="Song", artist="Artist", track_number=3)
        result = _rename_from_meta(self._file(tmp_path), meta, number=True)
        assert result.name == "03 - Artist - Song.mp3"

    def test_track_number_omitted_by_default(self, tmp_path):
        meta = TrackMeta(title="Song", artist="Artist", track_number=3)
        assert _rename_from_meta(self._file(tmp_path), meta).name == "Artist - Song.mp3"

    def test_sanitizes_illegal_characters(self, tmp_path):
        meta = TrackMeta(title="A/B: C", artist="D?E")
        assert _rename_from_meta(self._file(tmp_path), meta).name == "D_E - A_B_ C.mp3"

    def test_no_title_leaves_file_alone(self, tmp_path):
        path = self._file(tmp_path)
        assert _rename_from_meta(path, TrackMeta()) is None
        assert path.is_file()

    def test_avoids_clobbering_a_different_file(self, tmp_path):
        (tmp_path / "Artist - Song.mp3").write_bytes(b"existing")
        path = self._file(tmp_path)
        result = _rename_from_meta(path, TrackMeta(title="Song", artist="Artist"))
        assert result.name == "Artist - Song (2).mp3"
        assert (tmp_path / "Artist - Song.mp3").read_bytes() == b"existing"

    def test_replaces_its_own_previous_download(self, tmp_path):
        previous = tmp_path / "Artist - Song.mp3"
        previous.write_bytes(b"old")
        path = self._file(tmp_path)
        result = _rename_from_meta(
            path, TrackMeta(title="Song", artist="Artist"), replaceable=previous
        )
        assert result == previous
        assert previous.read_bytes() == b"audio"
        assert not list(tmp_path.glob("* (2).mp3"))

    def test_already_correct_name_is_a_no_op(self, tmp_path):
        path = self._file(tmp_path, "Artist - Song.mp3")
        result = _rename_from_meta(path, TrackMeta(title="Song", artist="Artist"))
        assert result == path
        assert path.read_bytes() == b"audio"


class TestUniquePath:
    def test_free_name_is_returned_as_is(self, tmp_path):
        assert _unique_path(tmp_path / "a.mp3") == tmp_path / "a.mp3"

    def test_increments_until_free(self, tmp_path):
        (tmp_path / "a.mp3").touch()
        (tmp_path / "a (2).mp3").touch()
        assert _unique_path(tmp_path / "a.mp3").name == "a (3).mp3"


class TestShortError:
    def test_strips_prefix_and_trailing_noise(self):
        exc = Exception("ERROR: [youtube] abc: Video unavailable; some detail")
        assert _short_error(exc) == "[youtube] abc: Video unavailable"

    def test_keeps_message_when_split_would_empty_it(self):
        # 開頭就是分隔符時，切完會變空字串——必須保留原文而不是留下空白
        assert _short_error(Exception("; unexpected")) == "; unexpected"

    def test_falls_back_to_logger_when_exception_has_no_message(self):
        logger = _CollectingLogger()
        logger.error("ERROR: [youtube] abc: Sign in to confirm you're not a bot")
        message = _short_error(Exception(""), logger)
        assert "Sign in to confirm" in message

    def test_never_returns_empty(self):
        message = _short_error(ValueError(""))
        assert message
        assert "ValueError" in message

    def test_uninformative_message_gains_the_exception_type(self):
        # 使用者曾看到「無法讀取 <網址>：」後面一片空白，完全無從查起
        message = _short_error(OSError("403"))
        assert "403" in message and "OSError" in message

    def test_informative_message_is_left_alone(self):
        message = _short_error(Exception("[LinkedIn] abc: Unsupported URL"))
        assert message == "[LinkedIn] abc: Unsupported URL"

    def test_truncates_very_long_messages(self):
        assert len(_short_error(Exception("x" * 500))) == 200


class TestVerbose:
    def test_quiet_by_default(self, tmp_path):
        opts = Downloader(Config(output_dir=tmp_path))._base_opts()
        assert opts["quiet"] is True
        assert opts["verbose"] is False

    def test_verbose_unmutes_yt_dlp(self, tmp_path):
        opts = Downloader(Config(output_dir=tmp_path), verbose=True)._base_opts()
        assert opts["quiet"] is False
        assert opts["no_warnings"] is False
        assert opts["verbose"] is True

    def test_verbose_leaves_logger_unattached(self, tmp_path):
        downloader = Downloader(Config(output_dir=tmp_path), verbose=True)
        opts = downloader._download_opts(Track("a", "u", "t"), _CollectingLogger())
        assert "logger" not in opts

    def test_logger_attached_when_quiet(self, tmp_path):
        downloader = Downloader(Config(output_dir=tmp_path))
        opts = downloader._download_opts(Track("a", "u", "t"), _CollectingLogger())
        assert "logger" in opts


class TestVideoMode:
    def test_audio_selector_by_default(self, tmp_path):
        assert Downloader(Config(output_dir=tmp_path))._format_selector() == "bestaudio/best"

    def test_best_video_prefers_compatible_codecs(self, tmp_path):
        selector = Downloader(Config(output_dir=tmp_path), video="best")._format_selector()
        # H.264 + AAC 必須排在最前面，否則會拿到 Windows 放不動的 AV1／Opus
        assert selector.startswith("bestvideo[vcodec^=avc1]+bestaudio[acodec^=mp4a]")
        assert selector.endswith("/best")

    def test_capped_video_selector_applies_height_to_every_branch(self, tmp_path):
        selector = Downloader(Config(output_dir=tmp_path), video="1080")._format_selector()
        assert "bestvideo[vcodec^=avc1][height<=?1080]+bestaudio[acodec^=mp4a]" in selector
        assert "/bestvideo[height<=?1080]+bestaudio" in selector
        assert "/best[height<=?1080]" in selector
        assert selector.endswith("/best")

    def test_video_mode_skips_audio_extraction(self, tmp_path):
        downloader = Downloader(Config(output_dir=tmp_path), video="720")
        assert downloader._postprocessors() == []

    def test_video_mode_merges_to_mp4(self, tmp_path):
        downloader = Downloader(Config(output_dir=tmp_path), video="720")
        opts = downloader._download_opts(Track("a", "u", "t"), _CollectingLogger())
        assert opts["merge_output_format"] == "mp4"

    def test_audio_mode_does_not_set_merge_format(self, tmp_path):
        downloader = Downloader(Config(output_dir=tmp_path))
        opts = downloader._download_opts(Track("a", "u", "t"), _CollectingLogger())
        assert "merge_output_format" not in opts


class TestPreflight:
    def test_rejects_invalid_config(self, tmp_path):
        from ytmusic.downloader import DownloadAborted

        downloader = Downloader(Config(output_dir=tmp_path, audio_format="aiff"))
        try:
            downloader.preflight()
        except DownloadAborted as exc:
            assert "aiff" in str(exc)
        else:
            raise AssertionError("預期會因為格式不合法而中止")

    def test_creates_output_dir_when_not_converting(self, tmp_path):
        target = tmp_path / "nested" / "out"
        Downloader(Config(output_dir=target, convert=False)).preflight()
        assert target.is_dir()


class TestFallbackUrl:
    def test_vimeo_oauth_failure_falls_back_to_player(self):
        exc = Exception("[vimeo] 76979871: Failed to fetch macos OAuth token: "
                        "HTTP Error 401: Unauthorized")
        assert _fallback_url("https://vimeo.com/76979871", exc) == (
            "https://player.vimeo.com/video/76979871"
        )

    def test_other_vimeo_errors_are_not_retried(self):
        exc = Exception("[vimeo] 123: Video unavailable")
        assert _fallback_url("https://vimeo.com/123", exc) is None

    def test_non_vimeo_errors_are_not_retried(self):
        exc = Exception("[youtube] abc: Sign in to confirm you're not a bot")
        assert _fallback_url("https://youtu.be/abc", exc) is None

    def test_player_url_has_no_further_fallback(self):
        exc = Exception("[vimeo] 123: OAuth 401")
        assert _fallback_url("https://player.vimeo.com/video/123", exc) is None


class TestColouredErrorMessages:
    """yt-dlp 在支援顏色的終端機上會把錯誤上色，訊息不能因此消失。

    實際災情：使用者只看到「無法讀取 <網址>：」後面一片空白，之後變成
    「…：DownloadError]」——因為 `\x1b[0;31m` 裡的 `;` 被當成句子分隔符切開，
    留下半截控制序列把後面的字吃掉。
    """

    RAW = "\x1b[0;31mERROR:\x1b[0m Unsupported URL: https://lnkd.in/p/gsKEgKZu"

    def test_clean_keeps_the_real_message(self):
        assert _clean_error_text(self.RAW) == "Unsupported URL: https://lnkd.in/p/gsKEgKZu"

    def test_short_error_has_no_escape_left(self):
        message = _short_error(Exception(self.RAW))
        assert "\x1b" not in message
        assert "lnkd.in" in message

    def test_short_coloured_message_still_readable(self):
        message = _short_error(Exception("\x1b[0;31mERROR:\x1b[0m HTTP Error 403"))
        assert message == "HTTP Error 403"

    def test_semicolon_still_trims_verbose_tails(self):
        text = "Unsupported URL; please report this issue"
        assert _clean_error_text(text) == "Unsupported URL"

    def test_empty_exception_still_says_something(self):
        assert "沒有訊息" in _short_error(Exception(""))


class TestNetworkErrorDetection:
    """連線被切斷跟「這支影片不能下載」是兩回事，建議也完全不同。"""

    def test_detects_ssl_eof(self):
        # 使用者實際遇到的：LinkedIn 短網址在他的網路上 TLS 被切斷
        assert _is_network_error(Exception(
            "Unable to download webpage: [SSL: UNEXPECTED_EOF_WHILE_READING] "
            "EOF occurred in violation of protocol (_ssl.c:1081)"))

    def test_detects_connection_reset(self):
        assert _is_network_error(Exception("<urlopen error [Errno 104] Connection reset by peer>"))

    def test_detects_timeout(self):
        assert _is_network_error(Exception("The read operation timed out"))

    def test_detects_dns_failure(self):
        assert _is_network_error(Exception("getaddrinfo failed"))

    def test_ignores_content_errors(self):
        assert not _is_network_error(Exception("Video unavailable"))
        assert not _is_network_error(Exception("Unsupported URL: https://example.com/x"))

    def test_sees_through_colour_codes(self):
        assert _is_network_error(Exception("\x1b[0;31mERROR:\x1b[0m connection reset"))


class TestNetworkHint:
    def test_says_it_is_not_the_video(self):
        assert "不是那支影片的問題" in NETWORK_HINT

    def test_mentions_antivirus_tls_scanning(self):
        # 防毒拆 TLS 是這個錯誤最常見的成因，卻最少人想到
        assert "掃描" in NETWORK_HINT

    def test_mentions_short_url_workaround(self):
        assert "lnkd.in" in NETWORK_HINT


class TestIpv4Retry:
    def test_forces_ipv4_and_keeps_other_options(self, monkeypatch):
        captured = {}

        class FakeYDL:
            def __init__(self, opts):
                captured.update(opts)

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def extract_info(self, url, download=False):
                captured["url"] = url
                return {"id": "x"}

        import yt_dlp
        monkeypatch.setattr(yt_dlp, "YoutubeDL", FakeYDL)
        info = _extract_over_ipv4({"proxy": "http://p", "quiet": True}, "https://x/y")

        assert info == {"id": "x"}
        assert captured["source_address"] == "0.0.0.0"  # 等同 yt-dlp 的 -4
        assert captured["proxy"] == "http://p"          # 其他設定不能被弄丟

    def test_does_not_mutate_the_caller_options(self, monkeypatch):
        class FakeYDL:
            def __init__(self, opts):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def extract_info(self, url, download=False):
                return None

        import yt_dlp
        monkeypatch.setattr(yt_dlp, "YoutubeDL", FakeYDL)
        opts = {"quiet": True}
        _extract_over_ipv4(opts, "https://x/y")
        assert "source_address" not in opts


class TestImpersonateHint:
    """curl_cffi 的版本區間是 yt-dlp 寫死的，提示裡不能漏掉。"""

    def test_pins_the_version_range(self):
        # 實際踩過：裝了 0.16 之後 yt-dlp 只說「target 不可用」，完全不提版本
        assert CURL_CFFI_SPEC == "curl_cffi>=0.10,<0.16"
        assert CURL_CFFI_SPEC in IMPERSONATE_HINT

    def test_uses_python_m_pip(self):
        # 跟 playwright 同一個坑：Windows 上 pip 裝的執行檔不在 PATH
        assert "python -m pip install" in IMPERSONATE_HINT

    def test_explains_why_it_helps(self):
        assert "TLS" in IMPERSONATE_HINT


class TestNetworkRetryOrder:
    """兩招治的是不同病因，順序有意義：先免安裝的，再要裝東西的。"""

    def _downloader(self, monkeypatch, *, available, ipv4, impersonating):
        import ytmusic.downloader as mod
        from ytmusic.config import Config

        monkeypatch.setattr(mod, "impersonation_available", lambda: available)
        monkeypatch.setattr(mod, "_extract_over_ipv4", ipv4)
        monkeypatch.setattr(mod, "_extract_impersonating", impersonating)
        downloader = mod.Downloader(Config())
        downloader._log = lambda message: None
        return downloader

    @staticmethod
    def _ssl_error(*args, **kwargs):
        raise Exception("[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred")

    def test_tries_ipv4_first_then_impersonation(self, monkeypatch):
        order = []
        downloader = self._downloader(
            monkeypatch, available=True,
            ipv4=lambda o, u: (order.append("ipv4"), self._ssl_error())[0],
            impersonating=lambda o, u, t="chrome": (order.append("impersonate"),
                                                    {"id": "ok"})[1],
        )
        info, _ = downloader._retry_network({}, "https://x/y", Exception("[SSL: x]"))
        assert order == ["ipv4", "impersonate"]
        assert info == {"id": "ok"}

    def test_skips_impersonation_when_unavailable(self, monkeypatch):
        order = []
        downloader = self._downloader(
            monkeypatch, available=False,
            ipv4=lambda o, u: (order.append("ipv4"), self._ssl_error())[0],
            impersonating=lambda o, u, t="chrome": order.append("impersonate"),
        )
        info, _ = downloader._retry_network({}, "https://x/y", Exception("[SSL: x]"))
        assert order == ["ipv4"]
        assert info is None

    def test_stops_when_the_error_stops_being_a_network_one(self, monkeypatch):
        # 換了條件之後變成「影片不存在」，再重試沒有意義
        order = []

        def ipv4(opts, url):
            order.append("ipv4")
            raise Exception("Video unavailable")

        downloader = self._downloader(
            monkeypatch, available=True, ipv4=ipv4,
            impersonating=lambda o, u, t="chrome": order.append("impersonate"),
        )
        info, failure = downloader._retry_network({}, "https://x/y", Exception("[SSL: x]"))
        assert order == ["ipv4"]
        assert info is None
        assert "Video unavailable" in str(failure)

    def test_does_not_re_impersonate_when_user_already_asked_for_it(self, monkeypatch):
        order = []
        downloader = self._downloader(
            monkeypatch, available=True,
            ipv4=lambda o, u: (order.append("ipv4"), self._ssl_error())[0],
            impersonating=lambda o, u, t="chrome": order.append("impersonate"),
        )
        downloader.impersonate = "chrome"
        downloader._retry_network({}, "https://x/y", Exception("[SSL: x]"))
        assert order == ["ipv4"]


class TestImpersonateOption:
    def test_config_value_reaches_ytdlp_options(self, monkeypatch):
        import ytmusic.downloader as mod
        from ytmusic.config import Config

        monkeypatch.setattr(mod, "impersonate_target", lambda name: f"<{name}>")
        assert mod.Downloader(Config(impersonate="firefox"))._base_opts()["impersonate"] == "<firefox>"

    def test_absent_by_default(self):
        from ytmusic.config import Config

        assert "impersonate" not in Downloader(Config())._base_opts()


class TestTrackCap:
    """自動混音清單沒有盡頭，所以「整張下載」一定要有個停得下來的數字。"""

    def _downloader(self, tmp_path, **kwargs):
        return Downloader(Config(output_dir=tmp_path), **kwargs)

    def test_radio_playlist_is_capped_by_default(self, tmp_path):
        url = "https://www.youtube.com/watch?v=abc&list=RDabc"
        assert self._downloader(tmp_path).track_cap(url) == RADIO_DEFAULT_MAX

    def test_ordinary_playlist_is_not_capped(self, tmp_path):
        url = "https://www.youtube.com/playlist?list=PL123"
        assert self._downloader(tmp_path).track_cap(url) is None

    def test_single_mode_needs_no_cap(self, tmp_path):
        # 只要那一首的時候，清單多長都無所謂
        url = "https://www.youtube.com/watch?v=abc&list=RDabc"
        assert self._downloader(tmp_path).track_cap(url, single=True) is None

    def test_explicit_max_wins_over_the_radio_default(self, tmp_path):
        url = "https://www.youtube.com/watch?v=abc&list=RDabc"
        assert self._downloader(tmp_path, max_tracks=5).track_cap(url) == 5

    def test_max_zero_means_no_limit_even_for_a_mix(self, tmp_path):
        url = "https://www.youtube.com/watch?v=abc&list=RDabc"
        assert self._downloader(tmp_path, max_tracks=0).track_cap(url) is None

    def test_max_applies_to_ordinary_playlists_too(self, tmp_path):
        url = "https://www.youtube.com/playlist?list=PL123"
        assert self._downloader(tmp_path, max_tracks=3).track_cap(url) == 3


class TestExpandHonoursTheCap:
    def _fake_ydl(self, monkeypatch, entries, captured):
        class FakeYDL:
            def __init__(self, opts):
                captured.append(opts)

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def extract_info(self, url, download=False):
                return {"_type": "playlist", "title": "Mix", "entries": entries}

        import yt_dlp
        monkeypatch.setattr(yt_dlp, "YoutubeDL", FakeYDL)

    def test_cap_is_passed_to_ytdlp_not_just_applied_afterwards(self, tmp_path, monkeypatch):
        # 事後才截斷等於白問了幾十頁——混音清單是一頁一頁問出來的。
        captured: list[dict] = []
        entries = [{"id": f"v{i}", "title": str(i)} for i in range(10)]
        self._fake_ydl(monkeypatch, entries, captured)

        downloader = Downloader(Config(output_dir=tmp_path), max_tracks=3)
        tracks = downloader.expand(["https://www.youtube.com/playlist?list=PL1"])

        assert captured[0]["playlistend"] == 3
        assert [t.video_id for t in tracks] == ["v0", "v1", "v2"]

    def test_no_cap_leaves_playlistend_unset(self, tmp_path, monkeypatch):
        captured: list[dict] = []
        self._fake_ydl(monkeypatch, [{"id": "a", "title": "A"}], captured)

        Downloader(Config(output_dir=tmp_path)).expand(
            ["https://www.youtube.com/playlist?list=PL1"])

        assert "playlistend" not in captured[0]

    def test_duplicates_do_not_eat_into_the_quota(self, tmp_path, monkeypatch):
        captured: list[dict] = []
        entries = [{"id": "a", "title": "A"}, {"id": "a", "title": "A"},
                   {"id": "b", "title": "B"}]
        self._fake_ydl(monkeypatch, entries, captured)

        downloader = Downloader(Config(output_dir=tmp_path), max_tracks=2)
        tracks = downloader.expand(["https://www.youtube.com/playlist?list=PL1"])

        assert [t.video_id for t in tracks] == ["a", "b"]


class TestBlockedDetection:
    def test_recognises_the_bot_check(self):
        assert is_blocked_error(Exception(
            "ERROR: [youtube] abc: Sign in to confirm you're not a bot."))

    def test_recognises_the_curly_apostrophe_youtube_actually_uses(self):
        assert is_blocked_error(Exception(
            "Sign in to confirm you’re not a bot. Use --cookies-from-browser"))

    def test_recognises_403(self):
        assert is_blocked_error(Exception(
            "unable to download video data: HTTP Error 403: Forbidden"))

    def test_recognises_rate_limiting(self):
        assert is_blocked_error(Exception("HTTP Error 429: Too Many Requests"))

    def test_ordinary_failures_are_not_blocks(self):
        assert not is_blocked_error(Exception("Video unavailable"))
        assert not is_blocked_error(Exception("This video is private"))


class TestBlockedAbort:
    """整批被擋下來時，剩下的幾百首照跑只是把真正的原因洗掉。"""

    def _downloader(self, tmp_path):
        return Downloader(Config(output_dir=tmp_path))

    def test_one_failure_does_not_stop_the_batch(self, tmp_path):
        # 單獨一支影片本來就可能因為年齡或地區限制回 403
        downloader = self._downloader(tmp_path)
        downloader._note_blocked()
        assert not downloader.blocked
        assert not downloader._stop.is_set()

    def test_stops_after_several_in_a_row_with_nothing_working(self, tmp_path):
        downloader = self._downloader(tmp_path)
        for _ in range(BLOCKED_ABORT_AFTER):
            downloader._note_blocked()
        assert downloader.blocked
        assert downloader._stop.is_set()

    def test_one_success_means_it_is_the_videos_not_the_block(self, tmp_path):
        """有的下得動、有的不行——那幾支是「要登入才看得到」，不是整批被擋。

        停掉整批會讓使用者連下得動的那三十幾首也拿不到，比看幾行錯誤訊息糟得多。
        實測同一秒、同一個 IP：有些影片讀得到，有些回「not a bot」。
        """
        downloader = self._downloader(tmp_path)
        downloader._note_success()
        for _ in range(BLOCKED_ABORT_AFTER * 3):
            downloader._note_blocked()
        assert not downloader.blocked
        assert not downloader._stop.is_set()

    def test_a_success_resets_the_streak(self, tmp_path):
        downloader = self._downloader(tmp_path)
        for _ in range(BLOCKED_ABORT_AFTER - 1):
            downloader._note_blocked()
        downloader._note_success()
        downloader._note_blocked()
        assert not downloader.blocked

    def test_threshold_is_high_enough_to_survive_a_few_login_only_videos(self):
        # 舊的門檻是 3：清單開頭剛好混到三支要登入的，整批就沒了
        assert BLOCKED_ABORT_AFTER >= 10

    def test_remaining_tracks_come_back_cancelled_not_failed(self, tmp_path):
        downloader = self._downloader(tmp_path)
        downloader.cancel()
        result = downloader._download_one(Track("x", "https://y/x", "X"))
        assert result.status == "cancelled"


class TestJsRuntimeOptions:
    """機器上有 node 卻不用它，等於白白讓簽章挑戰解不開。"""

    def test_non_deno_runtime_is_spelled_out_for_ytdlp(self, tmp_path, monkeypatch):
        import ytmusic.downloader as mod

        monkeypatch.setattr(mod, "find_js_runtimes", lambda: {"node": "/bin/node"})
        opts = Downloader(Config(output_dir=tmp_path))._base_opts()
        assert opts["js_runtimes"] == {"node": {}}

    def test_deno_needs_no_help_because_it_is_the_default(self, tmp_path, monkeypatch):
        import ytmusic.downloader as mod

        monkeypatch.setattr(mod, "find_js_runtimes",
                            lambda: {"deno": "/bin/deno", "node": "/bin/node"})
        assert "js_runtimes" not in Downloader(Config(output_dir=tmp_path))._base_opts()

    def test_nothing_installed_means_no_option(self, tmp_path, monkeypatch):
        import ytmusic.downloader as mod

        monkeypatch.setattr(mod, "find_js_runtimes", dict)
        assert "js_runtimes" not in Downloader(Config(output_dir=tmp_path))._base_opts()

    def test_a_runtime_yt_dlp_does_not_know_is_left_out(self, tmp_path, monkeypatch):
        # 送出沒聽過的名字，yt-dlp 是直接拋 ValueError——一個加分項不該弄死整趟下載
        import ytmusic.downloader as mod

        monkeypatch.setattr(mod, "find_js_runtimes",
                            lambda: {"node": "/bin/node", "rhino": "/bin/rhino"})
        opts = Downloader(Config(output_dir=tmp_path))._base_opts()
        assert opts["js_runtimes"] == {"node": {}}


class TestRequestSleep:
    """YouTube 看的不只是「同時幾條」，還有「多密集」。"""

    def test_sleep_reaches_ytdlp_on_both_axes(self, tmp_path):
        opts = Downloader(Config(output_dir=tmp_path, request_sleep=5))._base_opts()
        assert opts["sleep_interval_requests"] == 5
        assert opts["sleep_interval"] == 5

    def test_upper_bound_is_wider_so_the_gap_is_not_a_metronome(self, tmp_path):
        # 固定間隔本身就是一種特徵，yt-dlp 會在上下界之間隨機挑
        opts = Downloader(Config(output_dir=tmp_path, request_sleep=5))._base_opts()
        assert opts["max_sleep_interval"] > opts["sleep_interval"]

    def test_zero_means_no_sleep_options_at_all(self, tmp_path):
        opts = Downloader(Config(output_dir=tmp_path))._base_opts()
        assert "sleep_interval_requests" not in opts
        assert "sleep_interval" not in opts


class TestCookieErrors:
    """讀不到 cookies 是本機問題——一個封包都還沒送出去。"""

    def test_firefox_profile_locked_by_a_running_browser(self):
        # 實際踩到的：Firefox 沒關乾淨，cookies 資料庫被鎖住
        exc = Exception(r"[Errno 13] Permission denied: "
                        r"'C:\Users\a\AppData\Roaming\Mozilla\Firefox\Profiles\x.default'")
        assert is_cookie_error(exc)

    def test_windows_chrome_app_bound_encryption(self):
        assert is_cookie_error(Exception("2136 cookies could not be decrypted"))

    def test_chrome_database_copy_failure(self):
        assert is_cookie_error(Exception("Could not copy Chrome cookie database"))

    def test_a_cookie_problem_is_not_a_block(self):
        # 講成「被擋」的話，使用者會跑去等退燒、換 IP——而瀏覽器就開在旁邊
        exc = Exception("[Errno 13] Permission denied: 'cookies.sqlite'")
        assert not is_blocked_error(exc)

    def test_a_real_block_is_still_a_block(self):
        assert is_blocked_error(Exception("Sign in to confirm you're not a bot"))
        assert not is_cookie_error(Exception("Sign in to confirm you're not a bot"))


class TestCookieFileIsNeverModified:
    """yt-dlp 會把 cookie jar 寫回 cookiefile，所以絕不能把使用者的原檔交出去。

    症狀極難聯想到原因：第一次成功，之後每一次都被當成沒登入。實際踩到的畫面是
    doctor 的三個探針——前兩個 ✔，第三個就已經 ✖ 了。
    """

    def _downloader(self, tmp_path, body="# Netscape HTTP Cookie File\n"):
        cookies = tmp_path / "cookies.txt"
        cookies.write_text(body)
        config = Config(output_dir=tmp_path, cookies_file=str(cookies))
        return Downloader(config), cookies

    def test_ytdlp_never_sees_the_original_path(self, tmp_path):
        downloader, cookies = self._downloader(tmp_path)
        handed_over = downloader._base_opts()["cookiefile"]
        assert handed_over != str(cookies)

    def test_the_copy_has_the_same_content(self, tmp_path):
        downloader, cookies = self._downloader(tmp_path, "# real cookies\n.youtube.com\tTRUE\n")
        handed_over = Path(downloader._base_opts()["cookiefile"])
        assert handed_over.read_text() == cookies.read_text()

    def test_each_call_starts_from_the_pristine_original(self, tmp_path):
        # doctor 連跑三個探針就是這樣壞掉的：第一個把檔案寫壞，第三個就失敗了
        downloader, cookies = self._downloader(tmp_path, "original\n")
        first = Path(downloader._base_opts()["cookiefile"])
        first.write_text("rotated and now useless\n")   # 模擬 yt-dlp 寫回
        second = Path(downloader._base_opts()["cookiefile"])
        assert second.read_text() == "original\n"

    def test_writing_to_what_ytdlp_got_leaves_the_original_alone(self, tmp_path):
        downloader, cookies = self._downloader(tmp_path, "original\n")
        Path(downloader._base_opts()["cookiefile"]).write_text("clobbered\n")
        assert cookies.read_text() == "original\n"

    def test_no_cookies_configured_means_no_option(self, tmp_path):
        assert "cookiefile" not in Downloader(Config(output_dir=tmp_path))._base_opts()

    def test_an_unreadable_original_still_reaches_ytdlp(self, tmp_path):
        # 複製不動時寧可讓 yt-dlp 自己報錯，也不要在這裡把整批下載擋掉
        config = Config(output_dir=tmp_path, cookies_file=str(tmp_path / "missing.txt"))
        assert Downloader(config)._base_opts()["cookiefile"].endswith("missing.txt")


class TestAlternativeUploads:
    """鎖登入的通常是官方帳號那版；別人上傳的同一首往往沒鎖。"""

    def _downloader(self, tmp_path, **kwargs):
        return Downloader(Config(output_dir=tmp_path), **kwargs)

    def _track(self):
        return Track("orig", "https://y/orig", "JUST COMMUNICATION")

    def _hit(self, video_id, title):
        from ytmusic.search import SearchResult

        return SearchResult(video_id=video_id, url=f"https://y/{video_id}",
                            title=title, uploader="x", duration=200)

    def test_off_by_default(self, tmp_path):
        assert not self._downloader(tmp_path).find_alternatives

    def test_swaps_in_a_matching_upload(self, tmp_path, monkeypatch):
        downloader = self._downloader(tmp_path, find_alternatives=True)
        monkeypatch.setattr(downloader, "search",
                            lambda q, limit=5: [self._hit("other", "TWO-MIX - JUST COMMUNICATION")])
        attempted = []

        def fake_download(track, **kwargs):
            attempted.append(track.video_id)
            return Result(track, "ok", message=track.title)

        monkeypatch.setattr(downloader, "_download_one", fake_download)
        result = downloader._try_alternative(self._track())
        assert result is not None and result.status == "ok"
        assert attempted == ["other"]

    def test_keeps_the_original_title_so_tags_do_not_follow_the_uploader(self, tmp_path, monkeypatch):
        downloader = self._downloader(tmp_path, find_alternatives=True)
        monkeypatch.setattr(downloader, "search",
                            lambda q, limit=5: [self._hit("other", "TWO-MIX - JUST COMMUNICATION")])
        seen = {}

        def fake_download(track, **kwargs):
            seen["title"] = track.title
            return Result(track, "ok")

        monkeypatch.setattr(downloader, "_download_one", fake_download)
        downloader._try_alternative(self._track())
        assert seen["title"] == "JUST COMMUNICATION"

    def test_a_different_song_is_never_substituted(self, tmp_path, monkeypatch):
        downloader = self._downloader(tmp_path, find_alternatives=True)
        monkeypatch.setattr(downloader, "search",
                            lambda q, limit=5: [self._hit("other", "まったく別の曲です")])
        monkeypatch.setattr(downloader, "_download_one",
                            lambda *a, **k: pytest.fail("不該下載不同的歌"))
        assert downloader._try_alternative(self._track()) is None

    def test_the_same_video_is_not_retried(self, tmp_path, monkeypatch):
        downloader = self._downloader(tmp_path, find_alternatives=True)
        monkeypatch.setattr(downloader, "search",
                            lambda q, limit=5: [self._hit("orig", "JUST COMMUNICATION")])
        monkeypatch.setattr(downloader, "_download_one",
                            lambda *a, **k: pytest.fail("不該重試同一支影片"))
        assert downloader._try_alternative(self._track()) is None

    def test_a_failing_search_is_not_a_new_error(self, tmp_path, monkeypatch):
        # 這是加分項，不該把「這首下不到」變成別的失敗原因
        downloader = self._downloader(tmp_path, find_alternatives=True)

        def boom(*a, **k):
            raise RuntimeError("搜尋掛了")

        monkeypatch.setattr(downloader, "search", boom)
        assert downloader._try_alternative(self._track()) is None

    def test_the_substitute_is_reported_not_silent(self, tmp_path, monkeypatch):
        # 換了版本卻不說，使用者會以為拿到的是原本那個上傳
        downloader = self._downloader(tmp_path, find_alternatives=True)
        monkeypatch.setattr(downloader, "search",
                            lambda q, limit=5: [self._hit("other", "TWO-MIX - JUST COMMUNICATION")])
        monkeypatch.setattr(downloader, "_download_one",
                            lambda track, **k: Result(track, "ok"))
        result = downloader._try_alternative(self._track())
        assert any("TWO-MIX" in w for w in result.warnings)


class TestAlternativesDoNotDisturbTheProgressLine:
    """替代版本是同一首歌的另一次嘗試，不是新的一首。"""

    def test_inner_attempts_do_not_start_a_new_entry(self, tmp_path, monkeypatch):
        # 少了這個開關，每試一個版本就多跳一個編號，最後印出 [29/24] 這種東西
        from ytmusic.search import SearchResult

        started = []

        class Reporter:
            def start(self, video_id, label):
                started.append(video_id)

            def finish(self, *a, **k):
                pass

            def update(self, *a, **k):
                pass

            def log(self, *a, **k):
                pass

        downloader = Downloader(Config(output_dir=tmp_path, use_history=False),
                                reporter=Reporter(), find_alternatives=True)
        monkeypatch.setattr(downloader, "search", lambda q, limit=5: [
            SearchResult(video_id="other", url="https://y/other",
                         title="TWO-MIX - JUST COMMUNICATION", uploader="x", duration=200)])
        monkeypatch.setattr(downloader, "_fetch_for_test", None, raising=False)

        real = Downloader._download_one

        def only_the_swap_succeeds(self, track, **kwargs):
            if track.video_id == "other":
                return Result(track, "ok", message=track.title)
            return real(self, track, **kwargs)

        monkeypatch.setattr(Downloader, "_download_one", only_the_swap_succeeds)
        downloader._try_alternative(Track("orig", "https://y/orig", "JUST COMMUNICATION"))
        assert started == []  # 內層不該再開一個進度項目
