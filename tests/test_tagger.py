from ytmusic.tagger import build_metadata, pick_thumbnail_url


class TestBuildMetadata:
    def test_prefers_youtube_music_fields(self):
        info = {
            "title": "Artist - Song (Official Video)",
            "track": "Real Song",
            "artist": "Real Artist",
            "album": "Real Album",
            "release_year": 2021,
            "uploader": "Real Artist - Topic",
        }
        meta = build_metadata(info)
        assert meta.title == "Real Song"
        assert meta.artist == "Real Artist"
        assert meta.album == "Real Album"
        assert meta.date == "2021"

    def test_falls_back_to_title_parsing(self):
        meta = build_metadata({
            "title": "Some Artist - Some Song (Official Music Video)",
            "uploader": "Some Channel",
            "upload_date": "20200315",
        })
        assert meta.artist == "Some Artist"
        assert meta.title == "Some Song"
        assert meta.date == "2020"

    def test_falls_back_to_uploader_when_title_has_no_artist(self):
        meta = build_metadata({"title": "JustASong", "uploader": "Channel Name - Topic"})
        assert meta.artist == "Channel Name"
        assert meta.title == "JustASong"

    def test_playlist_becomes_album_and_track_number(self):
        meta = build_metadata(
            {"title": "A - B", "uploader": "C"},
            playlist_title="My Mix", playlist_index=3, playlist_count=10,
        )
        assert meta.album == "My Mix"
        assert meta.track_number == 3
        assert meta.track_total == 10

    def test_explicit_album_beats_playlist_title(self):
        meta = build_metadata({"title": "A - B", "album": "Real"}, playlist_title="Mix")
        assert meta.album == "Real"

    def test_album_artist_defaults_to_artist(self):
        assert build_metadata({"title": "A - B"}).album_artist == "A"

    def test_comment_holds_source_url(self):
        meta = build_metadata({"title": "A - B", "webpage_url": "https://youtu.be/x"})
        assert meta.comment == "https://youtu.be/x"

    def test_handles_sparse_info(self):
        meta = build_metadata({"id": "abc"})
        assert meta.title == ""
        assert meta.as_display() == ""

    def test_as_display(self):
        assert build_metadata({"title": "A - B"}).as_display() == "A - B"


class TestPickThumbnailUrl:
    def test_picks_largest_jpeg(self):
        info = {"thumbnails": [
            {"url": "https://i.ytimg.com/vi/x/default.jpg", "width": 120, "height": 90},
            {"url": "https://i.ytimg.com/vi/x/maxres.jpg", "width": 1280, "height": 720},
            {"url": "https://i.ytimg.com/vi/x/mq.jpg", "width": 320, "height": 180},
        ]}
        assert pick_thumbnail_url(info).endswith("maxres.jpg")

    def test_skips_webp(self):
        info = {"thumbnails": [
            {"url": "https://i.ytimg.com/vi_webp/x/maxres.webp", "width": 1280, "height": 720},
            {"url": "https://i.ytimg.com/vi/x/hq.jpg", "width": 480, "height": 360},
        ]}
        assert pick_thumbnail_url(info).endswith("hq.jpg")

    def test_ignores_query_string_when_matching_extension(self):
        info = {"thumbnails": [
            {"url": "https://i.ytimg.com/vi/x/hq.jpg?sqp=abc", "width": 480, "height": 360},
        ]}
        assert pick_thumbnail_url(info).startswith("https://i.ytimg.com")

    def test_falls_back_to_constructed_url(self):
        assert pick_thumbnail_url({"id": "abc123"}) == (
            "https://i.ytimg.com/vi/abc123/maxresdefault.jpg"
        )

    def test_returns_none_without_id_or_thumbnails(self):
        assert pick_thumbnail_url({}) is None
