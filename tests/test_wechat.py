import pytest

from ytmusic.wechat import (
    CaptureResult, MediaCandidate, extract_video_urls, has_probable_video,
    is_feed_api, is_missing_browser_error, is_wechat_url, looks_like_media,
    looks_like_playable_video, pick_best_media, suggest_filename,
)


class TestIsWechatUrl:
    def test_share_short_link(self):
        assert is_wechat_url("https://weixin.qq.com/sph/AJq0mgzYC0")

    def test_channels_page(self):
        assert is_wechat_url(
            "https://channels.weixin.qq.com/finder-preview/pages/sph?id=AJq0mgzYC0"
        )

    def test_case_insensitive(self):
        assert is_wechat_url("HTTPS://WEIXIN.QQ.COM/SPH/ABC")

    def test_wechat_article_is_not_a_channel(self):
        # 公眾號文章不是視頻號，不該被這個指令接手
        assert not is_wechat_url("https://mp.weixin.qq.com/s/abcdefg")

    def test_other_sites(self):
        assert not is_wechat_url("https://youtu.be/abc")
        assert not is_wechat_url("https://www.bilibili.com/video/BV1")

    def test_rejects_non_http(self):
        assert not is_wechat_url("weixin.qq.com/sph/abc")
        assert not is_wechat_url("")


class TestLooksLikeMedia:
    @pytest.mark.parametrize("url", [
        "https://example.com/a.mp4",
        "https://example.com/a.m3u8?token=1",
        "https://example.com/seg.ts",
        "https://example.com/a.MP4",
    ])
    def test_by_extension(self, url):
        assert looks_like_media(url)

    def test_by_content_type(self):
        assert looks_like_media("https://example.com/stream", "video/mp4")
        assert looks_like_media("https://example.com/x", "application/x-mpegURL")

    def test_by_tencent_media_host(self):
        assert looks_like_media("https://finder.video.qq.com/251/abcdef")

    def test_plain_page_is_not_media(self):
        assert not looks_like_media("https://channels.weixin.qq.com/page", "text/html")

    def test_image_is_not_media(self):
        assert not looks_like_media("https://example.com/cover.jpg", "image/jpeg")

    def test_rejects_non_http(self):
        assert not looks_like_media("blob:https://example.com/abc")
        assert not looks_like_media("")


class TestPickBestMedia:
    def test_prefers_tencent_cdn_when_both_look_like_videos(self):
        other = MediaCandidate("https://other.com/big.mp4", size=5_000_000)
        cdn = MediaCandidate("https://finder.video.qq.com/a", size=4_000_000,
                             from_media_host=True)
        assert pick_best_media([other, cdn]) is cdn

    def test_tiny_cdn_response_loses_to_a_real_video(self):
        # 這正是使用者踩到的：47 KB 的 CDN 回應被當成影片抓走
        tiny_cdn = MediaCandidate("https://finder.video.qq.com/a", size=48_000,
                                  from_media_host=True)
        real = MediaCandidate("https://other.com/big.mp4", size=99_000_000)
        assert pick_best_media([tiny_cdn, real]) is real

    def test_prefers_larger_among_same_host(self):
        small = MediaCandidate("https://finder.video.qq.com/a", size=1000,
                               from_media_host=True)
        big = MediaCandidate("https://finder.video.qq.com/b", size=9_000_000,
                             from_media_host=True)
        assert pick_best_media([small, big]) is big

    def test_prefers_mp4_over_playlist_when_tied(self):
        playlist = MediaCandidate("https://x.com/a.m3u8", size=0)
        direct = MediaCandidate("https://x.com/a.mp4", size=0)
        assert pick_best_media([playlist, direct]) is direct

    def test_empty(self):
        assert pick_best_media([]) is None

    def test_ignores_blank_urls(self):
        assert pick_best_media([MediaCandidate("")]) is None

    def test_capture_result_exposes_best(self):
        result = CaptureResult(candidates=[
            MediaCandidate("https://x.com/small.mp4", size=10),
            MediaCandidate("https://x.com/big.mp4", size=999),
        ])
        assert result.best.url.endswith("big.mp4")


class TestLooksLikePlayableVideo:
    def test_mp4(self):
        assert looks_like_playable_video(b"\x00\x00\x00\x20ftypisom\x00\x00\x02\x00")

    def test_flv(self):
        assert looks_like_playable_video(b"FLV\x01\x05\x00\x00\x00\x09")

    def test_webm(self):
        assert looks_like_playable_video(b"\x1aE\xdf\xa3\x01\x00\x00\x00")

    def test_hls_playlist(self):
        assert looks_like_playable_video(b"#EXTM3U\n#EXT-X-VERSION:3")

    def test_encrypted_wechat_stream_is_rejected(self):
        # 微信客戶端的加密串流開頭是亂數，不是 ftyp——正是要擋掉的東西
        assert not looks_like_playable_video(
            bytes.fromhex("b02eabd737ffe748d199224e411178c9")
        )

    def test_html_error_page_is_rejected(self):
        assert not looks_like_playable_video(b"<!DOCTYPE html><html>")

    def test_too_short(self):
        assert not looks_like_playable_video(b"ftyp")
        assert not looks_like_playable_video(b"")


class TestSuggestFilename:
    def test_author_and_title(self):
        assert suggest_filename("小貓什麼時候上來的呢", "喵星人") == "喵星人 - 小貓什麼時候上來的呢"

    def test_title_only(self):
        assert suggest_filename("標題", "") == "標題"

    def test_author_only(self):
        assert suggest_filename("", "作者") == "作者"

    def test_both_empty_gets_placeholder(self):
        assert suggest_filename("", "") == "wechat-video"

    def test_illegal_characters_are_sanitised(self):
        assert suggest_filename("a/b:c", "d?e") == "d_e - a_b_c"


class TestMissingBrowserDetection:
    def test_detects_playwright_missing_browser(self):
        # Playwright 實際吐出的訊息
        assert is_missing_browser_error(Exception(
            "BrowserType.launch: Executable doesn't exist at "
            "/opt/pw-browsers/chromium-1234/chrome-linux/headless_shell"
        ))

    def test_detects_install_prompt(self):
        assert is_missing_browser_error(Exception(
            "Please run the following command to download new browsers"
        ))

    def test_other_errors_are_not_auto_fixable(self):
        assert not is_missing_browser_error(Exception("Target page crashed"))
        assert not is_missing_browser_error(Exception("net::ERR_CONNECTION_RESET"))


class TestInstallCommands:
    def test_always_uses_python_dash_m(self):
        # Windows 上 pip 裝的執行檔多半不在 PATH，直接打 `playwright` 會失敗，
        # 所以一律走 `python -m`
        from ytmusic.browser import browser_install_command, pip_install_command
        import sys

        assert pip_install_command("playwright") == [
            sys.executable, "-m", "pip", "install", "playwright"
        ]
        assert browser_install_command() == [
            sys.executable, "-m", "playwright", "install", "chromium"
        ]

    def test_hint_does_not_suggest_bare_playwright(self):
        from ytmusic.wechat import PLAYWRIGHT_HINT

        for line in PLAYWRIGHT_HINT.splitlines():
            stripped = line.strip()
            if stripped.startswith("playwright ") or stripped.startswith("pip install"):
                raise AssertionError(f"提示不該叫使用者直接打：{stripped}")
        assert "python -m playwright install chromium" in PLAYWRIGHT_HINT
        assert "python -m pip install playwright" in PLAYWRIGHT_HINT


class TestThumbnailsAreNotVideos:
    """使用者實測時抓到 46.9 KiB 的封面當影片——vweixinthumb 是縮圖主機。"""

    def test_thumb_host_is_recognised(self):
        assert MediaCandidate("https://vweixinthumb.tc.qq.com/abc").is_thumbnail

    def test_image_content_type_is_a_thumbnail(self):
        assert MediaCandidate("https://x.com/a", content_type="image/jpeg").is_thumbnail

    def test_video_cdn_is_not_a_thumbnail(self):
        assert not MediaCandidate("https://finder.video.qq.com/abc").is_thumbnail

    def test_thumbnail_is_never_picked(self):
        thumb = MediaCandidate("https://vweixinthumb.tc.qq.com/a", size=48_000,
                               from_media_host=True)
        assert pick_best_media([thumb]) is None

    def test_real_video_beats_thumbnail(self):
        thumb = MediaCandidate("https://vweixinthumb.tc.qq.com/a", size=48_000,
                               from_media_host=True)
        video = MediaCandidate("https://finder.video.qq.com/v", size=5_000_000,
                               from_media_host=True)
        assert pick_best_media([thumb, video]) is video


class TestSizeHeuristic:
    def test_tiny_response_is_not_big_enough(self):
        assert not MediaCandidate("https://x/a.mp4", size=48_000).is_big_enough

    def test_real_video_is_big_enough(self):
        assert MediaCandidate("https://x/a.mp4", size=5_000_000).is_big_enough

    def test_unknown_size_is_not_held_against_it(self):
        # 伺服器沒給 content-length 時不該當成否定證據
        assert MediaCandidate("https://x/a.mp4", size=0).is_big_enough

    def test_big_plain_host_beats_small_cdn(self):
        small_cdn = MediaCandidate("https://finder.video.qq.com/a", size=50_000,
                                   from_media_host=True)
        big_other = MediaCandidate("https://other.com/a.mp4", size=9_000_000)
        assert pick_best_media([small_cdn, big_other]) is big_other


class TestDescribe:
    def test_marks_cdn_and_size(self):
        text = MediaCandidate("https://finder.video.qq.com/a", content_type="video/mp4",
                              size=5_000_000, from_media_host=True).describe()
        assert "CDN" in text and "MiB" in text and "video/mp4" in text

    def test_marks_thumbnail(self):
        assert "縮圖" in MediaCandidate("https://vweixinthumb.tc.qq.com/a").describe()


class TestHasProbableVideo:
    """瀏覽器提前關閉的元凶：封面圖也放在 finder.video.qq.com 上。

    只看「來自影片 CDN」的話，封面一載入就判定抓到影片、立刻關掉視窗，
    使用者連掃碼的時間都沒有。
    """

    def test_cover_on_video_cdn_does_not_count(self):
        cover = MediaCandidate("https://finder.video.qq.com/251/x/stodownload?k=1",
                               content_type="image/jpg", size=48_000,
                               from_media_host=True)
        assert not has_probable_video([cover])

    def test_real_video_counts(self):
        video = MediaCandidate("https://finder.video.qq.com/251/v",
                               content_type="video/mp4", size=8_000_000,
                               from_media_host=True)
        assert has_probable_video([video])

    def test_small_non_thumbnail_does_not_count(self):
        probe = MediaCandidate("https://finder.video.qq.com/x", size=1024,
                               from_media_host=True)
        assert not has_probable_video([probe])

    def test_empty(self):
        assert not has_probable_video([])


class TestFeedApi:
    def test_recognises_feed_info_endpoint(self):
        assert is_feed_api(
            "https://channels.weixin.qq.com/finder-preview/api/feed/get_feed_info?_rid=x"
        )

    def test_ordinary_asset_is_not_the_api(self):
        assert not is_feed_api("https://res.wx.qq.com/t/wx_fed/feed.9c135e64.js")


class TestExtractVideoUrls:
    def test_finds_nested_video_url(self):
        data = {"data": {"object": {"media": [
            {"url": "https://finder.video.qq.com/251/v?token=abc"},
        ]}}}
        assert extract_video_urls(data) == ["https://finder.video.qq.com/251/v?token=abc"]

    def test_skips_thumbnail_urls(self):
        data = {"cover": "https://vweixinthumb.tc.qq.com/cover.jpg",
                "url": "https://finder.video.qq.com/251/v"}
        assert extract_video_urls(data) == ["https://finder.video.qq.com/251/v"]

    def test_finds_plain_mp4_anywhere(self):
        assert extract_video_urls({"a": ["https://cdn.example.com/x.mp4"]}) == [
            "https://cdn.example.com/x.mp4"
        ]

    def test_ignores_unrelated_urls(self):
        assert extract_video_urls({"doc": "https://example.com/page.html"}) == []

    def test_deduplicates(self):
        url = "https://finder.video.qq.com/251/v"
        assert extract_video_urls({"a": url, "b": url}) == [url]

    def test_handles_empty_and_scalars(self):
        assert extract_video_urls({}) == []
        assert extract_video_urls(None) == []
        assert extract_video_urls(123) == []
