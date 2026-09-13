import argparse

import pytest

from ytmusic.cli import _resolve_single, build_parser


def _args(urls, single=False, playlist=False):
    return argparse.Namespace(urls=urls, single=single, playlist=playlist)


VIDEO = "https://www.youtube.com/watch?v=abc"
LIST = "https://www.youtube.com/playlist?list=PL123"
BOTH = "https://www.youtube.com/watch?v=abc&list=RDAMVMabc"


class TestResolveSingle:
    def test_explicit_single_wins(self):
        assert _resolve_single(_args([BOTH], single=True)) is True

    def test_explicit_playlist_wins(self):
        assert _resolve_single(_args([BOTH], playlist=True)) is False

    def test_conflicting_flags_are_rejected(self):
        assert _resolve_single(_args([BOTH], single=True, playlist=True)) is None

    def test_unambiguous_urls_need_no_prompt(self, monkeypatch):
        def explode(*_a, **_k):
            raise AssertionError("不該詢問使用者")

        monkeypatch.setattr("builtins.input", explode)
        assert _resolve_single(_args([VIDEO, LIST])) is False

    def test_defaults_to_single_when_not_interactive(self, monkeypatch, capsys):
        monkeypatch.setattr("sys.stdin.isatty", lambda: False)
        assert _resolve_single(_args([BOTH])) is True
        assert "只下載單曲" in capsys.readouterr().err

    def test_prompt_defaults_to_single_on_empty_input(self, monkeypatch):
        monkeypatch.setattr("sys.stdin.isatty", lambda: True)
        monkeypatch.setattr("builtins.input", lambda _p="": "")
        assert _resolve_single(_args([BOTH])) is True

    def test_prompt_choosing_two_gives_playlist(self, monkeypatch):
        monkeypatch.setattr("sys.stdin.isatty", lambda: True)
        monkeypatch.setattr("builtins.input", lambda _p="": "2")
        assert _resolve_single(_args([BOTH])) is False

    def test_prompt_warns_about_radio_playlists(self, monkeypatch, capsys):
        monkeypatch.setattr("sys.stdin.isatty", lambda: True)
        monkeypatch.setattr("builtins.input", lambda _p="": "1")
        _resolve_single(_args([BOTH]))
        assert "自動混音清單" in capsys.readouterr().err

    def test_eof_falls_back_to_single(self, monkeypatch):
        monkeypatch.setattr("sys.stdin.isatty", lambda: True)

        def eof(_p=""):
            raise EOFError

        monkeypatch.setattr("builtins.input", eof)
        assert _resolve_single(_args([BOTH])) is True


class TestParser:
    def test_video_flag_defaults_to_best(self):
        args = build_parser().parse_args(["dl", "URL", "--video"])
        assert args.video == "best"

    def test_video_flag_accepts_resolution(self):
        args = build_parser().parse_args(["dl", "URL", "--video", "1080"])
        assert args.video == "1080"

    def test_video_flag_absent_means_audio(self):
        assert build_parser().parse_args(["dl", "URL"]).video is None

    def test_rejects_unknown_resolution(self):
        with pytest.raises(SystemExit):
            build_parser().parse_args(["dl", "URL", "--video", "9000"])

    def test_dl_alias(self):
        assert build_parser().parse_args(["dl", "URL"]).urls == ["URL"]
        assert build_parser().parse_args(["download", "URL"]).urls == ["URL"]


class TestShortUrlExpander:
    """（Config 在這個類別裡自己 import，避免動到檔案頂端的既有匯入）"""
    """短網址展開會把網址送出本機，什麼時候問、什麼時候不問都得站得住腳。"""

    def _args(self, **overrides):
        import argparse

        base = dict(no_expand=False, expand=False, expander_url=None)
        base.update(overrides)
        return argparse.Namespace(**base)

    def test_absent_when_no_short_url(self):
        from ytmusic.cli import _short_url_expander
        from ytmusic.config import Config

        assert _short_url_expander(["https://www.youtube.com/watch?v=a"],
                                   self._args(), Config()) is None

    def test_absent_when_disabled(self):
        from ytmusic.cli import _short_url_expander
        from ytmusic.config import Config

        assert _short_url_expander(["https://lnkd.in/p/a"],
                                   self._args(no_expand=True), Config()) is None

    def test_config_flag_skips_the_question(self, monkeypatch):
        from ytmusic.cli import _short_url_expander
        from ytmusic.config import Config
        import ytmusic.shorturl as shorturl

        monkeypatch.setattr(shorturl, "expand", lambda url, service: "https://full/")
        monkeypatch.setattr("builtins.input", lambda *a: pytest.fail("不該再問"))
        expander = _short_url_expander(["https://lnkd.in/p/a"], self._args(),
                                       Config(expand_short_urls=True))
        assert expander("https://lnkd.in/p/a") == "https://full/"

    def test_explicit_flag_skips_the_question(self, monkeypatch):
        from ytmusic.cli import _short_url_expander
        from ytmusic.config import Config
        import ytmusic.shorturl as shorturl

        monkeypatch.setattr(shorturl, "expand", lambda url, service: "https://full/")
        monkeypatch.setattr("builtins.input", lambda *a: pytest.fail("不該再問"))
        expander = _short_url_expander(["https://lnkd.in/p/a"],
                                       self._args(expand=True), Config())
        assert expander("https://lnkd.in/p/a") == "https://full/"

    def test_never_asks_without_a_terminal(self, monkeypatch):
        from ytmusic.cli import _short_url_expander
        from ytmusic.config import Config

        monkeypatch.setattr("sys.stdin.isatty", lambda: False, raising=False)
        monkeypatch.setattr("builtins.input", lambda *a: pytest.fail("不該問"))
        expander = _short_url_expander(["https://lnkd.in/p/a"], self._args(), Config())
        assert expander("https://lnkd.in/p/a") == ""

    def test_declining_asks_only_once(self, monkeypatch):
        from ytmusic.cli import _short_url_expander
        from ytmusic.config import Config

        monkeypatch.setattr("sys.stdin.isatty", lambda: True, raising=False)
        asked = []
        monkeypatch.setattr("builtins.input", lambda *a: (asked.append(1), "n")[1])
        expander = _short_url_expander(["https://lnkd.in/p/a"], self._args(), Config())
        assert expander("https://lnkd.in/p/a") == ""
        assert expander("https://lnkd.in/p/b") == ""  # 拒絕過就不再騷擾
        assert len(asked) == 1

    def test_custom_service_is_used(self, monkeypatch):
        from ytmusic.cli import _short_url_expander
        from ytmusic.config import Config
        import ytmusic.shorturl as shorturl

        seen = {}
        monkeypatch.setattr(shorturl, "expand",
                            lambda url, service: seen.setdefault("service", service) or "https://f/")
        expander = _short_url_expander(["https://lnkd.in/p/a"],
                                       self._args(expand=True, expander_url="https://mine/{url}"),
                                       Config())
        expander("https://lnkd.in/p/a")
        assert seen["service"] == "https://mine/{url}"


class TestMaxFlag:
    def test_absent_means_no_explicit_cap(self):
        assert build_parser().parse_args(["dl", "URL"]).max_tracks is None

    def test_accepts_a_number(self):
        assert build_parser().parse_args(["dl", "URL", "--max", "20"]).max_tracks == 20

    def test_zero_is_allowed_and_means_no_limit(self):
        assert build_parser().parse_args(["dl", "URL", "--max", "0"]).max_tracks == 0

    def test_search_and_sync_take_it_too(self):
        # 三個子指令共用同一組下載選項，漏掉一個就會在那裡爆掉
        assert build_parser().parse_args(["search", "x", "--max", "5"]).max_tracks == 5
        assert build_parser().parse_args(["sync", "--max", "5"]).max_tracks == 5

    def test_does_not_collide_with_search_result_count(self):
        args = build_parser().parse_args(["search", "x", "-n", "3", "--max", "9"])
        assert (args.limit, args.max_tracks) == (3, 9)


class TestSummaryHints:
    """被擋跟「要帳號才看得到」是兩回事，給錯建議會讓人白試一輪。"""

    def _result(self, message, status="error"):
        from ytmusic.downloader import Result, Track

        return Result(Track("x", "https://y/x", "X"), status, message=message)

    def _summarize(self, results, tmp_path, **kwargs):
        from ytmusic.cli import _summarize
        from ytmusic.config import Config

        return _summarize(results, Config(output_dir=tmp_path), **kwargs)

    def test_bot_check_gets_the_blocked_advice(self, tmp_path, capsys):
        self._summarize([self._result("Sign in to confirm you're not a bot")],
                        tmp_path)
        err = capsys.readouterr().err
        assert "--cookies-from-browser firefox" in err
        assert "-j 1" in err  # 少開幾條同時下載才是根治的那一半

    def test_members_only_gets_the_plain_cookie_advice(self, tmp_path, capsys):
        self._summarize([self._result("Join this channel: members-only content")],
                        tmp_path)
        err = capsys.readouterr().err
        assert "--cookies" in err
        assert "not a bot" not in err  # 不是被擋，別扯到機器人

    def test_ordinary_failure_gets_no_cookie_advice(self, tmp_path, capsys):
        self._summarize([self._result("Video unavailable")], tmp_path)
        assert "--cookies" not in capsys.readouterr().err

    def test_windows_is_warned_off_chrome(self, tmp_path, capsys, monkeypatch):
        monkeypatch.setattr("sys.platform", "win32")
        self._summarize([self._result("HTTP Error 403: Forbidden")], tmp_path)
        assert "Chrome" in capsys.readouterr().err

    def test_cancelled_tracks_are_counted_not_listed(self, tmp_path, capsys):
        # 停手之後沒輪到的那幾百首逐條印出來，只會把真正的原因洗掉
        results = [self._result("Sign in to confirm you're not a bot")]
        results += [self._result("已取消", status="cancelled") for _ in range(200)]
        self._summarize(results, tmp_path, blocked=True)
        err = capsys.readouterr().err
        assert err.count("已取消") <= 1
        assert "200" in err


class TestJsRuntimeAdvice:
    """403 長得像「被擋」，但缺 JS runtime 也是這個症狀——而那個是自己就能修的。"""

    def _summarize(self, tmp_path, **kwargs):
        from ytmusic.cli import _summarize
        from ytmusic.config import Config
        from ytmusic.downloader import Result, Track

        failed = [Result(Track("x", "https://y/x", "X"), "error",
                         message="HTTP Error 403: Forbidden")]
        return _summarize(failed, Config(output_dir=tmp_path), **kwargs)

    def test_missing_runtime_is_raised_first(self, tmp_path, capsys, monkeypatch):
        monkeypatch.setattr("ytmusic.cli.find_js_runtimes", dict)
        self._summarize(tmp_path)
        err = capsys.readouterr().err
        assert "deno" in err
        assert err.index("deno") < err.index("--cookies-from-browser")

    def test_installed_runtime_is_not_mentioned(self, tmp_path, capsys, monkeypatch):
        monkeypatch.setattr("ytmusic.cli.find_js_runtimes",
                            lambda: {"deno": "/bin/deno"})
        self._summarize(tmp_path)
        assert "deno" not in capsys.readouterr().err
