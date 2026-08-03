import pytest

from ytmusic.search import (
    SearchResult, SelectionError, filter_by_artist, format_results, parse_results,
    parse_selection,
)
from ytmusic.utils import display_width


def make(video_id="a", title="Song", uploader="Chan", duration=200.0):
    return SearchResult(video_id=video_id, title=title, uploader=uploader,
                        duration=duration, url=f"https://youtu.be/{video_id}")


class TestParseResults:
    def test_reads_entries(self):
        info = {"entries": [
            {"id": "a", "title": "One", "uploader": "Chan A", "duration": 100,
             "url": "https://youtu.be/a"},
            {"id": "b", "title": "Two", "channel": "Chan B", "duration": 200},
        ]}
        results = parse_results(info)
        assert [r.video_id for r in results] == ["a", "b"]
        assert results[1].uploader == "Chan B"
        assert results[1].url.endswith("watch?v=b")

    def test_skips_empty_and_idless_entries(self):
        info = {"entries": [None, {"title": "no id"}, {"id": "c", "title": "ok"}]}
        assert [r.video_id for r in parse_results(info)] == ["c"]

    def test_handles_missing_info(self):
        assert parse_results(None) == []
        assert parse_results({}) == []


class TestOfficialAudio:
    def test_topic_channel_is_official(self):
        assert make(uploader="Some Artist - Topic").is_official_audio

    def test_topic_suffix_stripped_for_display(self):
        assert make(uploader="Some Artist - Topic").channel == "Some Artist"

    def test_normal_channel_is_not_official(self):
        assert not make(uploader="Random Uploader").is_official_audio


class TestFormatResults:
    def test_marks_official_audio(self):
        lines = format_results([make(uploader="A - Topic"), make(uploader="B")])
        assert "♪" in lines[0]
        assert "♪" not in lines[1]

    def test_columns_align_across_cjk_and_latin(self):
        results = [
            make(title="周杰倫 Jay Chou《告白氣球》", uploader="周杰倫"),
            make(title="Rick Astley - Never Gonna Give You Up", uploader="RickAstleyYT"),
            make(title="マッシュル -MASHLE- OP", uploader="TVアニメ"),
        ]
        lines = format_results(results, width=100)
        # 每一行的時間欄都必須落在同一個顯示欄位上
        positions = {display_width(line.split("  ")[0]) for line in lines}
        assert len(positions) == 1

    def test_never_exceeds_requested_width(self):
        long_title = "Creepy Nuts「Bling-Bang-Bang-Born」×TV Anime「マッシュル」" * 3
        for line in format_results([make(title=long_title)], width=90):
            assert display_width(line) <= 90

    def test_empty_input(self):
        assert format_results([]) == []

    def test_missing_duration_shows_placeholder(self):
        assert "--:--" in format_results([make(duration=None)])[0]


class TestParseSelection:
    def test_empty_defaults_to_first(self):
        assert parse_selection("", 5) == [0]

    def test_single_number(self):
        assert parse_selection("3", 5) == [2]

    def test_comma_list(self):
        assert parse_selection("1,3,5", 5) == [0, 2, 4]

    def test_full_width_comma(self):
        assert parse_selection("1，3", 5) == [0, 2]

    def test_range(self):
        assert parse_selection("2-4", 5) == [1, 2, 3]

    def test_reversed_range(self):
        assert parse_selection("4-2", 5) == [1, 2, 3]

    def test_mixed(self):
        assert parse_selection("1,3-5", 5) == [0, 2, 3, 4]

    def test_deduplicates_but_keeps_order(self):
        assert parse_selection("3,1,3", 5) == [2, 0]

    def test_all(self):
        assert parse_selection("a", 3) == [0, 1, 2]
        assert parse_selection("all", 3) == [0, 1, 2]

    def test_quit_returns_empty(self):
        assert parse_selection("q", 5) == []
        assert parse_selection("取消", 5) == []

    def test_out_of_range(self):
        with pytest.raises(SelectionError):
            parse_selection("9", 5)
        with pytest.raises(SelectionError):
            parse_selection("0", 5)

    def test_not_a_number(self):
        with pytest.raises(SelectionError):
            parse_selection("abc", 5)


class TestFilterByArtist:
    def _r(self, title, channel, duration=200.0):
        return SearchResult(video_id=title, title=title, uploader=channel,
                            duration=duration, url="u")

    def test_keeps_only_the_artists_own_channel(self):
        results = [
            self._r("晴天", "周杰倫 Jay Chou"),
            self._r("晴天 歌詞版", "某某歌詞頻道"),
            self._r("晴天 cover", "路人翻唱"),
        ]
        assert [r.uploader for r in filter_by_artist(results, "周杰倫")] == ["周杰倫 Jay Chou"]

    def test_matches_regardless_of_case_and_spacing(self):
        results = [self._r("Song", "Rick  Astley")]
        assert filter_by_artist(results, "rickastley")
        assert filter_by_artist(results, "RICK ASTLEY")

    def test_matches_topic_channels(self):
        results = [self._r("Song", "周杰倫 - Topic")]
        assert len(filter_by_artist(results, "周杰倫")) == 1

    def test_drops_long_compilations(self):
        results = [
            self._r("晴天", "周杰倫 Jay Chou", 200),
            self._r("周杰倫全部歌曲合輯", "周杰倫 Jay Chou", 8000),
        ]
        assert [r.title for r in filter_by_artist(results, "周杰倫")] == ["晴天"]

    def test_keeps_long_ones_if_that_is_all_there_is(self):
        results = [self._r("演唱會全場", "周杰倫 Jay Chou", 8000)]
        assert len(filter_by_artist(results, "周杰倫")) == 1

    def test_returns_empty_when_no_channel_matches(self):
        results = [self._r("Song", "完全無關的頻道")]
        assert filter_by_artist(results, "周杰倫") == []

    def test_blank_artist(self):
        assert filter_by_artist([self._r("Song", "Chan")], "  ") == []


class TestNonVideoResultsAreDropped:
    def test_channel_entry_is_dropped(self):
        # 使用者截圖裡的狀況：搜尋結果第一筆是頻道，長度顯示 --:--，
        # 選下去會把整個頻道抓下來
        info = {"entries": [
            {"id": "UCabcdefghijklmnopqrstuv", "title": "周杰倫 Jay Chou",
             "ie_key": "YoutubeTab", "duration": None},
            {"id": "abc12345678", "title": "晴天", "duration": 269},
        ]}
        assert [r.video_id for r in parse_results(info)] == ["abc12345678"]

    def test_playlist_entry_is_dropped(self):
        info = {"entries": [{"id": "PL123456789012345", "title": "合輯",
                             "ie_key": "YoutubePlaylist", "duration": None}]}
        assert parse_results(info) == []

    def test_video_without_duration_is_kept(self):
        # 直播等影片可能沒有長度，但 ID 是正常的 11 碼，不該被誤刪
        info = {"entries": [{"id": "abc12345678", "title": "直播中",
                             "ie_key": "Youtube", "duration": None}]}
        assert len(parse_results(info)) == 1


class TestLongMarker:
    def test_long_video_is_marked(self):
        long_one = SearchResult("a", "合輯", "Chan", 8000.0, "u")
        assert "≡" in format_results([long_one])[0]

    def test_short_video_is_not_marked(self):
        short = SearchResult("a", "單曲", "Chan", 200.0, "u")
        assert "≡" not in format_results([short])[0]

    def test_official_audio_beats_long_marker(self):
        both = SearchResult("a", "合輯", "Chan - Topic", 8000.0, "u")
        assert "♪" in format_results([both])[0]


class TestNonYouTubeIdsAreKept:
    def test_bilibili_bv_id_survives(self):
        # BV 號有 12 碼，YouTube 的長度規則會把它誤判成頻道而刪掉
        info = {"entries": [{"id": "BV1GJ411x7h7", "title": "測試",
                             "ie_key": "BiliBili", "duration": None}]}
        assert [r.video_id for r in parse_results(info)] == ["BV1GJ411x7h7"]

    def test_bilibili_with_duration(self):
        info = {"entries": [{"id": "BV1GJ411x7h7", "title": "測試",
                             "ie_key": "BiliBili", "duration": 200}]}
        assert len(parse_results(info)) == 1

    def test_bilibili_playlist_still_dropped(self):
        info = {"entries": [{"id": "x", "title": "合集",
                             "ie_key": "BilibiliPlaylist", "duration": None}]}
        assert parse_results(info) == []
