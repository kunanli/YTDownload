import pytest

from ytmusic.search import (
    SearchResult, SelectionError, format_results, parse_results, parse_selection,
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
