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
