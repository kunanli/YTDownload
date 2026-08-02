import pytest

from ytmusic.utils import (
    clean_title, human_size, human_time, parse_browser_spec, sanitize_filename,
    split_artist_title, strip_topic, truncate,
)


class TestCleanTitle:
    def test_removes_parenthesised_noise(self):
        assert clean_title("Song Name (Official Music Video)") == "Song Name"
        assert clean_title("Song Name (Official Video)") == "Song Name"
        assert clean_title("Song Name [Official Audio]") == "Song Name"
        assert clean_title("Song Name (Lyrics)") == "Song Name"

    def test_removes_cjk_bracket_noise(self):
        assert clean_title("周杰倫【告白氣球 官方MV】") == "周杰倫"
        assert clean_title("告白氣球【Official MV】") == "告白氣球"

    def test_keeps_meaningful_parentheses(self):
        assert clean_title("Song Name (feat. Someone)") == "Song Name (feat. Someone)"
        assert clean_title("Song Name (Acoustic)") == "Song Name (Acoustic)"

    def test_falls_back_to_original_when_everything_stripped(self):
        assert clean_title("(Official Video)") == "(Official Video)"

    def test_handles_empty(self):
        assert clean_title("") == ""


class TestSplitArtistTitle:
    def test_splits_on_hyphen(self):
        assert split_artist_title("Artist - Song") == ("Artist", "Song")

    def test_splits_on_en_dash(self):
        assert split_artist_title("Artist – Song") == ("Artist", "Song")

    def test_strips_noise_before_splitting(self):
        assert split_artist_title("Artist - Song (Official Video)") == ("Artist", "Song")

    def test_keeps_trailing_hyphens_in_title(self):
        assert split_artist_title("A - B - C") == ("A", "B - C")

    def test_cjk_quotes(self):
        assert split_artist_title("周杰倫「告白氣球」") == ("周杰倫", "告白氣球")

    def test_returns_none_artist_when_unsplittable(self):
        artist, title = split_artist_title("JustOneTitle")
        assert artist is None
        assert title == "JustOneTitle"

    def test_pipe_separator(self):
        assert split_artist_title("Artist | Song") == ("Artist", "Song")


class TestStripTopic:
    def test_removes_topic_suffix(self):
        assert strip_topic("Some Artist - Topic") == "Some Artist"

    def test_leaves_other_names_alone(self):
        assert strip_topic("Some Artist") == "Some Artist"


class TestSanitizeFilename:
    def test_replaces_illegal_characters(self):
        assert sanitize_filename('a/b:c*d?e"f<g>h|i') == "a_b_c_d_e_f_g_h_i"

    def test_strips_trailing_dots_and_spaces(self):
        assert sanitize_filename("name. ") == "name"

    def test_escapes_windows_reserved_names(self):
        assert sanitize_filename("CON") == "_CON"
        assert sanitize_filename("com1.mp3").startswith("_")

    def test_truncates(self):
        assert len(sanitize_filename("x" * 500, max_length=20)) == 20

    def test_empty_becomes_placeholder(self):
        assert sanitize_filename("") == "untitled"
        assert sanitize_filename("   ") == "untitled"

    def test_keeps_cjk(self):
        assert sanitize_filename("告白氣球") == "告白氣球"


class TestParseBrowserSpec:
    def test_plain_browser_name(self):
        assert parse_browser_spec("chrome") == ("chrome", None, None, None)

    def test_normalises_case_and_spacing(self):
        assert parse_browser_spec("  Firefox  ") == ("firefox", None, None, None)

    def test_profile(self):
        assert parse_browser_spec("chrome:Profile 1") == ("chrome", "Profile 1", None, None)

    def test_profile_path(self):
        name, profile, _, _ = parse_browser_spec("firefox:~/.mozilla/firefox/abc.default")
        assert (name, profile) == ("firefox", "~/.mozilla/firefox/abc.default")

    def test_keyring(self):
        assert parse_browser_spec("chromium+gnomekeyring") == (
            "chromium", None, "GNOMEKEYRING", None
        )

    def test_container(self):
        assert parse_browser_spec("firefox::Personal") == (
            "firefox", None, None, "Personal"
        )

    def test_profile_and_container(self):
        assert parse_browser_spec("firefox:dev-edition::Work") == (
            "firefox", "dev-edition", None, "Work"
        )

    def test_rejects_empty(self):
        with pytest.raises(ValueError):
            parse_browser_spec("")
        with pytest.raises(ValueError):
            parse_browser_spec("  ")


class TestFormatting:
    def test_human_size(self):
        assert human_size(0) == "--"
        assert human_size(None) == "--"
        assert human_size(512) == "512 B"
        assert human_size(1024) == "1.0 KiB"
        assert human_size(5 * 1024 * 1024) == "5.0 MiB"

    def test_human_time(self):
        assert human_time(None) == "--:--"
        assert human_time(65) == "01:05"
        assert human_time(3725) == "1:02:05"

    def test_truncate(self):
        assert truncate("abcdef", 10) == "abcdef"
        assert truncate("abcdef", 4) == "abc…"
