from pathlib import Path

import pytest

from ytmusic.lyrics import (
    Cue, embed_lyrics, find_subtitle_files, language_of, normalise_languages,
    parse_subtitles, parse_timestamp, to_lrc, to_plain,
)

SRT = """1
00:00:01,360 --> 00:00:04,000
[♪♪♪]

2
00:00:18,640 --> 00:00:22,000
We're no strangers to love

3
00:01:02,500 --> 00:01:05,000
You know the rules
and so do I
"""

VTT = """WEBVTT
Kind: captions
Language: zh-TW

00:00:05.000 --> 00:00:08.000
<c>你好</c>世界

00:00:10.000 --> 00:00:12.000
再見
"""


class TestParseTimestamp:
    def test_with_hours(self):
        assert parse_timestamp("01:02:03,500") == 3723.5

    def test_without_hours(self):
        assert parse_timestamp("02:03.250") == 123.25

    def test_dot_and_comma_both_work(self):
        assert parse_timestamp("00:00:01,360") == parse_timestamp("00:00:01.360")

    def test_invalid(self):
        assert parse_timestamp("nope") is None


class TestParseSubtitles:
    def test_srt(self):
        cues = parse_subtitles(SRT)
        assert [c.text for c in cues] == [
            "[♪♪♪]", "We're no strangers to love", "You know the rules and so do I",
        ]
        assert cues[1].start == 18.64

    def test_vtt_strips_inline_tags(self):
        cues = parse_subtitles(VTT)
        assert [c.text for c in cues] == ["你好世界", "再見"]

    def test_drops_consecutive_duplicates(self):
        # 自動字幕會為了滾動效果重複整行
        text = ("00:00:01.000 --> 00:00:02.000\nsame\n\n"
                "00:00:02.000 --> 00:00:03.000\nsame\n\n"
                "00:00:03.000 --> 00:00:04.000\nother\n")
        assert [c.text for c in parse_subtitles(text)] == ["same", "other"]

    def test_sorted_by_time(self):
        text = ("00:00:09.000 --> 00:00:10.000\nlate\n\n"
                "00:00:01.000 --> 00:00:02.000\nearly\n")
        assert [c.text for c in parse_subtitles(text)] == ["early", "late"]

    def test_empty_input(self):
        assert parse_subtitles("") == []


class TestToLrc:
    def test_includes_metadata_tags(self):
        lrc = to_lrc([Cue(1.0, "hi")], title="T", artist="A", album="B")
        assert "[ti:T]" in lrc and "[ar:A]" in lrc and "[al:B]" in lrc

    def test_timestamp_format(self):
        assert "[00:01.36]hi" in to_lrc([Cue(1.36, "hi")])

    def test_minutes_roll_over(self):
        assert "[02:03.50]x" in to_lrc([Cue(123.5, "x")])

    def test_no_tags_when_metadata_missing(self):
        assert to_lrc([Cue(0.0, "x")]).startswith("[00:00.00]")

    def test_plain_output(self):
        assert to_plain([Cue(1.0, "a"), Cue(2.0, "b")]) == "a\nb"


class TestNormaliseLanguages:
    def test_chinese_aliases(self):
        assert normalise_languages("繁中,簡中,英,日,韓,西班牙") == [
            "zh-TW", "zh-Hans", "en", "ja", "ko", "es"
        ]

    def test_raw_codes_pass_through(self):
        assert normalise_languages("zh-TW,en") == ["zh-TW", "en"]

    def test_full_width_comma(self):
        assert normalise_languages("繁中，英") == ["zh-TW", "en"]

    def test_deduplicates(self):
        assert normalise_languages("繁中,zh-TW") == ["zh-TW"]

    def test_empty(self):
        assert normalise_languages("") == []


class TestFindSubtitleFiles:
    def _make(self, tmp_path, *names):
        (tmp_path / "Song.mp3").write_bytes(b"x")
        for name in names:
            (tmp_path / name).write_text("x", encoding="utf-8")
        return tmp_path / "Song.mp3"

    def test_orders_by_language_preference(self, tmp_path):
        media = self._make(tmp_path, "Song.en.srt", "Song.ja.srt", "Song.zh-TW.srt")
        found = find_subtitle_files(media, ["zh-TW", "en", "ja"])
        assert [language_of(p) for p in found] == ["zh-TW", "en", "ja"]

    def test_alphabetical_order_would_have_picked_english(self, tmp_path):
        media = self._make(tmp_path, "Song.en.srt", "Song.zh-TW.srt")
        assert language_of(find_subtitle_files(media, ["zh-TW"])[0]) == "zh-TW"

    def test_matches_extended_codes(self, tmp_path):
        media = self._make(tmp_path, "Song.en.srt", "Song.zh-Hant-TW.srt")
        assert language_of(find_subtitle_files(media, ["zh-Hant"])[0]) == "zh-Hant-TW"

    def test_unlisted_languages_go_last(self, tmp_path):
        media = self._make(tmp_path, "Song.de.srt", "Song.en.srt")
        assert language_of(find_subtitle_files(media, ["en"])[0]) == "en"

    def test_ignores_other_files(self, tmp_path):
        media = self._make(tmp_path, "Song.en.srt", "Other.en.srt", "Song.txt")
        assert [p.name for p in find_subtitle_files(media)] == ["Song.en.srt"]

    def test_missing_directory(self):
        assert find_subtitle_files(Path("/nope/Song.mp3")) == []


class TestLanguageOf:
    def test_extracts_code(self):
        assert language_of(Path("Song.zh-TW.srt")) == "zh-TW"

    def test_no_language_part(self):
        assert language_of(Path("Song.srt")) == ""


class TestEmbedLyrics:
    def test_refuses_empty_text(self, tmp_path):
        media = tmp_path / "a.mp3"
        media.write_bytes(b"x")
        assert embed_lyrics(media, "   ") is False

    def test_unsupported_container_returns_false(self, tmp_path):
        media = tmp_path / "a.wav"
        media.write_bytes(b"x")
        assert embed_lyrics(media, "text") is False
