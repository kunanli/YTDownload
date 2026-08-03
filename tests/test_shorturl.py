from ytmusic.shorturl import (
    DEFAULT_EXPANDER, EXPANDER_NOTICE, SHORTENER_HOSTS, is_short_url,
    parse_expanded, short_host,
)


class TestShortHost:
    def test_detects_lnkd_in(self):
        assert short_host("https://lnkd.in/p/gMf2KcjH") == "lnkd.in"

    def test_ignores_www_prefix(self):
        assert short_host("https://www.bit.ly/abc") == "bit.ly"

    def test_ignores_port(self):
        assert short_host("https://t.co:443/abc") == "t.co"

    def test_normal_urls_are_not_short(self):
        assert short_host("https://www.linkedin.com/posts/x-ugcPost-748/") == ""
        assert not is_short_url("https://www.youtube.com/watch?v=abc")

    def test_youtu_be_is_not_treated_as_a_shortener(self):
        # yt-dlp 直接認得，而且從來不是連不上的原因
        assert "youtu.be" not in SHORTENER_HOSTS
        assert not is_short_url("https://youtu.be/dQw4w9WgXcQ")

    def test_rejects_non_http(self):
        assert short_host("lnkd.in/p/abc") == ""
        assert short_host("") == ""


class TestParseExpanded:
    LONG = "https://www.linkedin.com/posts/x-ugcPost-7489903959202029568-RGJU/"

    def test_reads_resolved_url(self):
        payload = {"success": True, "resolved_url": self.LONG}
        assert parse_expanded(payload, "https://lnkd.in/p/a") == self.LONG

    def test_rejects_unchanged_url(self):
        # 展開後還是同一個網址等於沒幫上忙，不值得再重試一次
        same = "https://lnkd.in/p/a"
        assert parse_expanded({"success": True, "resolved_url": same}, same) == ""

    def test_ignores_trailing_slash_difference(self):
        same = "https://lnkd.in/p/a"
        assert parse_expanded({"resolved_url": same + "/"}, same) == ""

    def test_rejects_failure_payload(self):
        assert parse_expanded({"success": False, "resolved_url": self.LONG}, "x") == ""

    def test_rejects_non_http_result(self):
        assert parse_expanded({"resolved_url": "javascript:alert(1)"}, "x") == ""

    def test_survives_junk(self):
        assert parse_expanded({}, "x") == ""
        assert parse_expanded(None, "x") == ""
        assert parse_expanded("nope", "x") == ""


class TestExpanderNotice:
    def test_says_it_is_third_party(self):
        assert "第三方" in EXPANDER_NOTICE

    def test_says_credentials_are_not_sent(self):
        assert "cookies" in EXPANDER_NOTICE

    def test_has_a_service_placeholder(self):
        assert "{service}" in EXPANDER_NOTICE

    def test_default_service_is_https_and_templated(self):
        assert DEFAULT_EXPANDER.startswith("https://")
        assert "{url}" in DEFAULT_EXPANDER
