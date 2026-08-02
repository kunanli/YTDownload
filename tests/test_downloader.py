from pathlib import Path

from ytmusic.config import Config
from ytmusic.downloader import (
    Downloader, Track, _final_path, _parse_rate, _rename_from_meta, _unique_path, _walk,
)
from ytmusic.history import History
from ytmusic.tagger import TrackMeta


class TestWalk:
    def test_single_video(self):
        tracks = _walk({"id": "abc", "title": "Song", "webpage_url": "https://youtu.be/abc"})
        assert len(tracks) == 1
        assert tracks[0].video_id == "abc"
        assert tracks[0].url == "https://youtu.be/abc"

    def test_constructs_url_when_missing(self):
        assert _walk({"id": "abc", "title": "S"})[0].url.endswith("watch?v=abc")

    def test_playlist_flattens_and_numbers_entries(self):
        info = {
            "_type": "playlist",
            "title": "My Mix",
            "playlist_count": 2,
            "entries": [
                {"id": "a", "title": "One", "url": "https://youtu.be/a"},
                {"id": "b", "title": "Two", "url": "https://youtu.be/b"},
            ],
        }
        tracks = _walk(info)
        assert [t.video_id for t in tracks] == ["a", "b"]
        assert [t.playlist_index for t in tracks] == [1, 2]
        assert all(t.playlist_title == "My Mix" for t in tracks)
        assert all(t.playlist_count == 2 for t in tracks)

    def test_nested_playlists(self):
        info = {
            "_type": "playlist", "title": "Channel",
            "entries": [
                {"_type": "playlist", "title": "Inner",
                 "entries": [{"id": "a", "title": "One"}]},
                {"id": "b", "title": "Two"},
            ],
        }
        tracks = _walk(info)
        assert [t.video_id for t in tracks] == ["a", "b"]
        assert tracks[0].playlist_title == "Inner"

    def test_skips_empty_entries(self):
        info = {"_type": "playlist", "entries": [None, {"id": "a", "title": "One"}]}
        assert [t.video_id for t in _walk(info)] == ["a"]

    def test_skips_unexpanded_playlist_references(self):
        info = {"_type": "url", "ie_key": "YoutubeTab", "id": "UC123"}
        assert _walk({"_type": "playlist", "entries": [info]}) == []

    def test_entry_without_id_is_dropped(self):
        assert _walk({"title": "no id"}) == []


class TestFinalPath:
    def test_reads_requested_downloads(self):
        info = {"requested_downloads": [{"filepath": "/music/song.mp3"}]}
        assert _final_path(info) == Path("/music/song.mp3")

    def test_falls_back_to_filename(self):
        assert _final_path({"_filename": "/music/song.webm"}) == Path("/music/song.webm")

    def test_returns_none_when_unknown(self):
        assert _final_path({}) is None


class TestParseRate:
    def test_suffixes(self):
        assert _parse_rate("500K") == 500 * 1024
        assert _parse_rate("1.5M") == int(1.5 * 1024 ** 2)
        assert _parse_rate("2G") == 2 * 1024 ** 3
        assert _parse_rate("1000") == 1000
        assert _parse_rate("500KB") == 500 * 1024

    def test_invalid(self):
        assert _parse_rate("fast") is None
        assert _parse_rate("") is None


class TestFilterNew:
    def _downloader(self, tmp_path, history, **overrides):
        config = Config(output_dir=tmp_path, **overrides)
        return Downloader(config, history=history)

    def test_splits_by_history(self, tmp_path):
        with History(tmp_path / "h.db") as history:
            history.add("seen")
            downloader = self._downloader(tmp_path, history)
            tracks = [Track("seen", "u", "A"), Track("fresh", "u", "B")]
            pending, skipped = downloader.filter_new(tracks)
            assert [t.video_id for t in pending] == ["fresh"]
            assert [t.video_id for t in skipped] == ["seen"]

    def test_force_ignores_history(self, tmp_path):
        with History(tmp_path / "h.db") as history:
            history.add("seen")
            downloader = self._downloader(tmp_path, history)
            pending, skipped = downloader.filter_new([Track("seen", "u", "A")], force=True)
            assert len(pending) == 1
            assert skipped == []

    def test_history_disabled(self, tmp_path):
        downloader = self._downloader(tmp_path, None, use_history=False)
        pending, skipped = downloader.filter_new([Track("seen", "u", "A")])
        assert len(pending) == 1
        assert skipped == []


class TestOptions:
    def test_postprocessor_uses_configured_codec(self, tmp_path):
        config = Config(output_dir=tmp_path, audio_format="flac", quality="320")
        pps = Downloader(config)._postprocessors()
        assert pps[0]["preferredcodec"] == "flac"
        assert pps[0]["preferredquality"] == "320"

    def test_best_quality_maps_to_vbr_zero(self, tmp_path):
        config = Config(output_dir=tmp_path, quality="best")
        assert Downloader(config)._postprocessors()[0]["preferredquality"] == "0"

    def test_no_convert_means_no_postprocessors(self, tmp_path):
        config = Config(output_dir=tmp_path, convert=False)
        assert Downloader(config)._postprocessors() == []

    def test_outtmpl_uses_playlist_subfolder(self, tmp_path):
        config = Config(output_dir=tmp_path, playlist_folder=True)
        track = Track("a", "u", "t", playlist_title="My: Mix")
        tmpl = Downloader(config)._outtmpl(track)
        assert "My_ Mix" in tmpl
        assert (tmp_path / "My_ Mix").is_dir()

    def test_outtmpl_without_playlist(self, tmp_path):
        config = Config(output_dir=tmp_path, playlist_folder=True)
        tmpl = Downloader(config)._outtmpl(Track("a", "u", "t"))
        assert tmpl == str(tmp_path / config.filename_template)

    def test_base_opts_carry_network_settings(self, tmp_path):
        config = Config(output_dir=tmp_path, proxy="socks5://127.0.0.1:1080",
                        rate_limit="500K", cookies_from_browser="firefox")
        opts = Downloader(config)._base_opts()
        assert opts["proxy"] == "socks5://127.0.0.1:1080"
        assert opts["ratelimit"] == 500 * 1024
        assert opts["cookiesfrombrowser"] == ("firefox", None, None, None)

    def test_base_opts_parse_browser_profile(self, tmp_path):
        config = Config(output_dir=tmp_path, cookies_from_browser="chrome:Profile 1")
        opts = Downloader(config)._base_opts()
        assert opts["cookiesfrombrowser"] == ("chrome", "Profile 1", None, None)


class TestRenameFromMeta:
    def _file(self, tmp_path, name="raw.mp3"):
        path = tmp_path / name
        path.write_bytes(b"audio")
        return path

    def test_renames_to_artist_and_title(self, tmp_path):
        path = self._file(tmp_path)
        result = _rename_from_meta(path, TrackMeta(title="Song", artist="Artist"))
        assert result.name == "Artist - Song.mp3"
        assert result.is_file()
        assert not path.exists()

    def test_title_only_when_artist_unknown(self, tmp_path):
        result = _rename_from_meta(self._file(tmp_path), TrackMeta(title="Song"))
        assert result.name == "Song.mp3"

    def test_adds_track_number_when_requested(self, tmp_path):
        meta = TrackMeta(title="Song", artist="Artist", track_number=3)
        result = _rename_from_meta(self._file(tmp_path), meta, number=True)
        assert result.name == "03 - Artist - Song.mp3"

    def test_track_number_omitted_by_default(self, tmp_path):
        meta = TrackMeta(title="Song", artist="Artist", track_number=3)
        assert _rename_from_meta(self._file(tmp_path), meta).name == "Artist - Song.mp3"

    def test_sanitizes_illegal_characters(self, tmp_path):
        meta = TrackMeta(title="A/B: C", artist="D?E")
        assert _rename_from_meta(self._file(tmp_path), meta).name == "D_E - A_B_ C.mp3"

    def test_no_title_leaves_file_alone(self, tmp_path):
        path = self._file(tmp_path)
        assert _rename_from_meta(path, TrackMeta()) is None
        assert path.is_file()

    def test_avoids_clobbering_a_different_file(self, tmp_path):
        (tmp_path / "Artist - Song.mp3").write_bytes(b"existing")
        path = self._file(tmp_path)
        result = _rename_from_meta(path, TrackMeta(title="Song", artist="Artist"))
        assert result.name == "Artist - Song (2).mp3"
        assert (tmp_path / "Artist - Song.mp3").read_bytes() == b"existing"

    def test_replaces_its_own_previous_download(self, tmp_path):
        previous = tmp_path / "Artist - Song.mp3"
        previous.write_bytes(b"old")
        path = self._file(tmp_path)
        result = _rename_from_meta(
            path, TrackMeta(title="Song", artist="Artist"), replaceable=previous
        )
        assert result == previous
        assert previous.read_bytes() == b"audio"
        assert not list(tmp_path.glob("* (2).mp3"))

    def test_already_correct_name_is_a_no_op(self, tmp_path):
        path = self._file(tmp_path, "Artist - Song.mp3")
        result = _rename_from_meta(path, TrackMeta(title="Song", artist="Artist"))
        assert result == path
        assert path.read_bytes() == b"audio"


class TestUniquePath:
    def test_free_name_is_returned_as_is(self, tmp_path):
        assert _unique_path(tmp_path / "a.mp3") == tmp_path / "a.mp3"

    def test_increments_until_free(self, tmp_path):
        (tmp_path / "a.mp3").touch()
        (tmp_path / "a (2).mp3").touch()
        assert _unique_path(tmp_path / "a.mp3").name == "a (3).mp3"


class TestPreflight:
    def test_rejects_invalid_config(self, tmp_path):
        from ytmusic.downloader import DownloadAborted

        downloader = Downloader(Config(output_dir=tmp_path, audio_format="aiff"))
        try:
            downloader.preflight()
        except DownloadAborted as exc:
            assert "aiff" in str(exc)
        else:
            raise AssertionError("預期會因為格式不合法而中止")

    def test_creates_output_dir_when_not_converting(self, tmp_path):
        target = tmp_path / "nested" / "out"
        Downloader(Config(output_dir=target, convert=False)).preflight()
        assert target.is_dir()
