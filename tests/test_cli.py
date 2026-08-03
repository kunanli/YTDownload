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
