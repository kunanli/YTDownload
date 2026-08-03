from pathlib import Path

import pytest

from ytmusic.config import Config, coerce_value


def test_defaults_are_sane():
    config = Config()
    assert config.audio_format == "mp3"
    assert config.quality == "192"
    assert config.convert is True
    assert isinstance(config.output_dir, Path)
    assert config.validate() == []


def test_concurrency_is_clamped():
    assert Config(concurrency=0).concurrency == 1
    assert Config(concurrency=99).concurrency == 16


def test_validate_rejects_bad_values():
    assert Config(audio_format="aiff").validate()
    assert Config(quality="9001").validate()
    assert Config(filename_template="%(title)s").validate()


def test_validate_accepts_known_browser():
    assert Config(cookies_from_browser="chrome:Profile 1").validate() == []


def test_validate_rejects_unknown_browser():
    problems = Config(cookies_from_browser="netscape").validate()
    assert problems and "netscape" in problems[0]


def test_roundtrip_through_file(tmp_path):
    path = tmp_path / "config.json"
    Config(audio_format="flac", quality="best", concurrency=5).save(path)

    loaded = Config.load(path)
    assert loaded.audio_format == "flac"
    assert loaded.quality == "best"
    assert loaded.concurrency == 5


def test_load_missing_file_returns_defaults(tmp_path):
    assert Config.load(tmp_path / "nope.json").audio_format == "mp3"


def test_load_corrupt_file_returns_defaults(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("{not json", encoding="utf-8")
    assert Config.load(path).audio_format == "mp3"


def test_load_ignores_unknown_keys(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"audio_format": "m4a", "who_is_this": 1}', encoding="utf-8")
    assert Config.load(path).audio_format == "m4a"


def test_merged_skips_none_and_keeps_original():
    base = Config(audio_format="mp3", quality="192")
    merged = base.merged(audio_format="flac", quality=None)
    assert merged.audio_format == "flac"
    assert merged.quality == "192"
    assert base.audio_format == "mp3"  # 原物件不變


def test_merged_accepts_false():
    assert Config().merged(convert=False).convert is False


class TestCoerceValue:
    @pytest.mark.parametrize("raw,expected", [
        ("true", True), ("YES", True), ("1", True), ("on", True),
        ("false", False), ("no", False), ("0", False), ("off", False),
    ])
    def test_booleans(self, raw, expected):
        assert coerce_value("convert", raw) is expected

    def test_bad_boolean(self):
        with pytest.raises(ValueError):
            coerce_value("convert", "maybe")

    def test_int(self):
        assert coerce_value("concurrency", "4") == 4

    def test_unknown_key(self):
        with pytest.raises(KeyError):
            coerce_value("nope", "x")

    def test_clears_optional_fields(self):
        assert coerce_value("proxy", "none") is None
        assert coerce_value("cookies_file", "") is None

    def test_passes_strings_through(self):
        assert coerce_value("audio_format", "flac") == "flac"


class TestExpandShortUrls:
    """同意過一次就該記得住，不然每次下載都被問一遍。"""

    def test_defaults_to_off(self):
        # 會把網址送給第三方，所以預設關閉
        assert Config().expand_short_urls is False

    def test_accepts_boolean_strings(self):
        assert coerce_value("expand_short_urls", "true") is True
        assert coerce_value("expand_short_urls", "false") is False
        assert coerce_value("expand_short_urls", "y") is True

    def test_rejects_nonsense(self):
        with pytest.raises(ValueError):
            coerce_value("expand_short_urls", "maybe")

    def test_survives_a_save_load_round_trip(self, tmp_path):
        path = tmp_path / "config.json"
        Config().merged(expand_short_urls=True).save(path)
        assert Config.load(path).expand_short_urls is True
