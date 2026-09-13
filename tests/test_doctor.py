import pytest

from ytmusic.doctor import (
    BAD, Check, OK, WARN, conclusion, impersonation_status, missing_advice,
)


class TestCheckLine:
    def test_aligns_by_display_width(self):
        # 標籤欄要對齊，中英夾雜也不能破版
        assert Check("yt-dlp", OK, "2026.07.04").line().startswith("  ✔ yt-dlp")

    def test_includes_the_detail(self):
        assert "2026.07.04" in Check("yt-dlp", OK, "2026.07.04").line()


class TestImpersonationStatus:
    """三種情況的下一步完全不同，yt-dlp 卻一律只說「target 不可用」。"""

    def test_reports_missing_package(self, monkeypatch):
        import builtins

        real_import = builtins.__import__

        def fake(name, *args, **kwargs):
            if name == "curl_cffi":
                raise ImportError("no module")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fake)
        available, detail = impersonation_status()
        assert available is False
        assert "沒有安裝" in detail
        assert "curl_cffi>=0.10,<0.16" in detail  # 版本範圍不能漏

    def test_reports_unsupported_version(self, monkeypatch):
        import curl_cffi

        monkeypatch.setattr(curl_cffi, "_yt_dlp__version", "0.16.0 (unsupported)",
                            raising=False)
        available, detail = impersonation_status()
        assert available is False
        assert "不在 yt-dlp 支援範圍" in detail

    def test_reports_available(self, monkeypatch):
        import curl_cffi

        monkeypatch.setattr(curl_cffi, "_yt_dlp__version", "0.15.0", raising=False)
        available, detail = impersonation_status()
        assert available is True
        assert "可用" in detail


class TestConclusion:
    """測完要給一句「所以你該做什麼」，不能只丟結果讓使用者自己想。"""

    def test_plain_connection_works(self):
        assert "重跑" in conclusion([Check("一般連線", OK, "讀得到：X")])

    def test_only_ipv4_works(self):
        result = conclusion([Check("一般連線", BAD, "SSL"),
                             Check("強制 IPv4", OK, "讀得到：X")])
        assert "IPv6" in result
        assert "不用特別設定" in result  # 這招是自動的，不該叫人動手

    def test_only_impersonation_works(self):
        result = conclusion([Check("一般連線", BAD, "SSL"),
                             Check("強制 IPv4", BAD, "SSL"),
                             Check("假扮瀏覽器", OK, "讀得到：X")])
        assert "TLS 指紋" in result
        assert "config set impersonate chrome" in result

    def test_nothing_works(self):
        result = conclusion([Check("一般連線", BAD, "SSL"),
                             Check("強制 IPv4", BAD, "SSL")])
        assert "換個網路" in result

    def test_no_results(self):
        assert conclusion([]) == ""


class TestMissingAdvice:
    def test_lists_only_hard_failures(self):
        checks = [Check("ffmpeg", BAD, "找不到"),
                  Check("playwright", WARN, "沒有安裝"),
                  Check("yt-dlp", OK, "2026.07.04")]
        advice = missing_advice(checks)
        assert advice == ["ffmpeg：找不到"]

    def test_empty_when_all_good(self):
        assert missing_advice([Check("yt-dlp", OK, "x")]) == []


class TestJsRuntimeStatus:
    """缺 JS runtime 是現在 YouTube 下載最常見的絆腳石，但錯誤訊息從不明說。"""

    def test_reports_what_it_found(self, monkeypatch):
        import ytmusic.doctor as mod

        monkeypatch.setattr(mod, "t", lambda key, **kw: kw.get("names", key))
        monkeypatch.setattr("ytmusic.utils.find_js_runtimes",
                            lambda: {"deno": "/usr/bin/deno"})
        usable, detail = mod.js_runtime_status()
        assert usable
        assert "/usr/bin/deno" in detail

    def test_missing_runtime_is_not_usable(self, monkeypatch):
        import ytmusic.doctor as mod

        monkeypatch.setattr("ytmusic.utils.find_js_runtimes", dict)
        usable, _ = mod.js_runtime_status()
        assert not usable

    def test_counts_as_a_blocking_problem_not_a_warning(self, monkeypatch):
        # YouTube 現在真的要它，不是「有更好」——報成 ! 的話使用者會直接略過
        import ytmusic.doctor as mod

        monkeypatch.setattr("ytmusic.utils.find_js_runtimes", dict)
        check = next(c for c in mod.environment() if c.label == "JS runtime")
        assert check.mark == mod.BAD


class TestBlockedConclusion:
    """全滅有兩種：被站台擋，和網路根本不通。處置相反，不能給同一句話。"""

    def _fail(self, label, detail):
        from ytmusic.doctor import BAD, Check

        return Check(label, BAD, detail)

    def test_bot_check_is_not_reported_as_a_network_problem(self):
        # 講成「這條網路不通」會害人整晚去查一個根本沒壞的防毒
        from ytmusic.doctor import conclusion, t

        said = conclusion([
            self._fail("一般連線", "Sign in to confirm you're not a bot"),
            self._fail("強制 IPv4", "Sign in to confirm you're not a bot"),
        ])
        assert said == t("conclusion.blocked")
        assert said != t("conclusion.none")

    def test_403_counts_as_blocked_too(self):
        from ytmusic.doctor import conclusion, t

        said = conclusion([
            self._fail("一般連線", "HTTP Error 403: Forbidden"),
            self._fail("強制 IPv4", "HTTP Error 403: Forbidden"),
        ])
        assert said == t("conclusion.blocked")

    def test_real_network_failure_still_says_network(self):
        from ytmusic.doctor import conclusion, t

        said = conclusion([
            self._fail("一般連線", "[SSL: UNEXPECTED_EOF_WHILE_READING]"),
            self._fail("強制 IPv4", "[SSL: UNEXPECTED_EOF_WHILE_READING]"),
        ])
        assert said == t("conclusion.none")

    def test_one_success_still_wins(self):
        from ytmusic.doctor import OK, Check, conclusion, t

        said = conclusion([
            self._fail("一般連線", "Sign in to confirm you're not a bot"),
            Check("強制 IPv4", OK, "讀得到：某某"),
        ])
        assert said != t("conclusion.blocked")


class TestCookieErrorConclusion:
    def test_locked_firefox_profile_is_not_a_network_verdict(self, tmp_path):
        # 講成「這條網路不通」，使用者會去查防毒和 VPN——而正解是把瀏覽器關掉
        from ytmusic.doctor import BAD, Check, conclusion, t

        detail = r"[Errno 13] Permission denied: 'C:\...\Firefox\Profiles\x.default'"
        said = conclusion([Check("一般連線", BAD, detail),
                           Check("強制 IPv4", BAD, detail)])
        assert said == t("cookies.unreadable")
        assert said != t("conclusion.none")

    def test_it_beats_the_blocked_verdict_too(self, tmp_path):
        # cookies 讀不到的時候根本還沒連上站台，不可能是被站台擋
        from ytmusic.doctor import BAD, Check, conclusion, t

        said = conclusion([Check("一般連線", BAD, "[Errno 13] Permission denied: 'cookies.sqlite'")])
        assert said == t("cookies.unreadable")


class TestCookieErrorKeepsTheFullPath:
    """本機檔案問題的訊息裡，那條路徑就是全部的線索。"""

    def test_long_profile_path_is_not_truncated(self, monkeypatch, tmp_path):
        import ytmusic.doctor as mod
        from ytmusic.config import Config

        path = (r"C:\Users\andyd\AppData\Roaming\Mozilla\Firefox"
                r"\Profiles\0ajogb2d.default-release\cookies.sqlite")
        message = f"[Errno 13] Permission denied: '{path}'"
        assert len(message) > 110  # 舊的截斷剛好切在檔名前面

        class Boom:
            def __init__(self, opts):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def extract_info(self, url, download=False):
                raise PermissionError(message)

        import yt_dlp
        monkeypatch.setattr(yt_dlp, "YoutubeDL", Boom)
        monkeypatch.setattr(mod, "probes", lambda config: [("一般連線", "", {})])
        checks = mod.probe_url("https://y/x", Config(output_dir=tmp_path),
                               out=open(tmp_path / "log", "w"))
        assert "cookies.sqlite" in checks[0].detail

    def test_ordinary_errors_are_still_kept_short(self, monkeypatch, tmp_path):
        import ytmusic.doctor as mod
        from ytmusic.config import Config

        class Boom:
            def __init__(self, opts):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def extract_info(self, url, download=False):
                raise RuntimeError("x" * 300)

        import yt_dlp
        monkeypatch.setattr(yt_dlp, "YoutubeDL", Boom)
        monkeypatch.setattr(mod, "probes", lambda config: [("一般連線", "", {})])
        checks = mod.probe_url("https://y/x", Config(output_dir=tmp_path),
                               out=open(tmp_path / "log", "w"))
        assert len(checks[0].detail) <= 110
