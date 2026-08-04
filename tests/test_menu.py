import io

import pytest

from ytmusic.menu import (
    LANGUAGE_CHOICES, MENU_ITEMS, Cancelled, ask_languages, ask_required,
    ask_site, build_command, render_menu, run_menu,
)


class Asker:
    """依序回答預先排好的答案，用完就當作使用者按了 Ctrl+D。"""

    def __init__(self, *answers):
        self.answers = list(answers)
        self.prompts = []

    def __call__(self, prompt=""):
        self.prompts.append(prompt)
        if not self.answers:
            raise Cancelled
        return self.answers.pop(0)


class TestRenderMenu:
    def test_lists_every_item(self):
        text = render_menu()
        for item in MENU_ITEMS:
            assert f"[{item.key}] {item.label}" in text

    def test_has_exit_option(self):
        assert "[0] 離開" in render_menu()


class TestBuildCommand:
    def test_download_audio(self):
        assert build_command("1", Asker("https://youtu.be/a", "")) == ["dl", "https://youtu.be/a"]

    def test_empty_choice_defaults_to_download(self):
        assert build_command("", Asker("https://youtu.be/a", ""))[0] == "dl"

    def test_blank_url_retries_then_cancels(self):
        # 貼上失敗時要能重貼，連續三次空白才放棄
        assert build_command("1", Asker("   ", "", "")) is None

    def test_search_defaults_to_youtube(self):
        assert build_command("2", Asker("告白氣球", "")) == ["search", "告白氣球"]

    def test_search_on_bilibili(self):
        assert build_command("2", Asker("告白氣球", "2")) == [
            "search", "告白氣球", "--site", "bilibili"
        ]

    def test_search_explicit_youtube_adds_nothing(self):
        assert build_command("2", Asker("告白氣球", "1")) == ["search", "告白氣球"]

    def test_artist_search(self):
        assert build_command("3", Asker("周杰倫", "")) == ["search", "--artist", "周杰倫"]

    def test_artist_search_on_bilibili(self):
        assert build_command("3", Asker("周杰倫", "2")) == [
            "search", "--artist", "周杰倫", "--site", "bilibili"
        ]

    def test_artist_blank_cancels(self):
        assert build_command("3", Asker("  ", "", "")) is None

    def test_video_defaults_to_720(self):
        assert build_command("4", Asker("https://youtu.be/a", "", "")) == [
            "dl", "https://youtu.be/a", "--video", "720"
        ]

    def test_audio_lyrics_without_language_uses_default(self):
        assert build_command("1", Asker("https://youtu.be/a", "y", "")) == [
            "dl", "https://youtu.be/a", "--lyrics"
        ]

    def test_audio_lyrics_with_chosen_languages(self):
        assert build_command("1", Asker("https://youtu.be/a", "y", "1,3")) == [
            "dl", "https://youtu.be/a", "--lyrics", "繁中,英"
        ]

    def test_video_subs_without_language_uses_default(self):
        assert build_command("4", Asker("https://youtu.be/a", "", "y", "")) == [
            "dl", "https://youtu.be/a", "--video", "720", "--subs"
        ]

    def test_video_subs_with_chosen_languages(self):
        assert build_command("4", Asker("https://youtu.be/a", "", "y", "4,5")) == [
            "dl", "https://youtu.be/a", "--video", "720", "--subs", "日,韓"
        ]

    @pytest.mark.parametrize("answer,expected", [("1", "720"), ("2", "1080"), ("3", "best")])
    def test_video_quality_choices(self, answer, expected):
        command = build_command("4", Asker("https://youtu.be/a", answer, ""))
        assert command[-1] == expected

    def test_unknown_video_quality_falls_back(self):
        assert build_command("4", Asker("https://youtu.be/a", "99", ""))[-1] == "720"

    def test_sync(self):
        assert build_command("6", Asker()) == ["sync"]

    def test_wechat_asks_nothing_else(self):
        # 現在是直接問微信的 API，不再需要問視窗或登入
        assert build_command("5", Asker("https://weixin.qq.com/sph/a")) == [
            "wechat", "https://weixin.qq.com/sph/a"
        ]

    def test_wechat_blank_url_starts_login(self):
        # 掃碼常常來不及，空輸入直接進登入模式（視窗不會自動關）
        assert build_command("5", Asker("  ")) == ["wechat", "--login"]

    def test_history(self):
        assert build_command("7", Asker()) == ["history", "list"]

    def test_sync_add_with_name(self):
        assert build_command("8", Asker("https://x/1", "我的最愛")) == [
            "sync", "add", "https://x/1", "--name", "我的最愛"
        ]

    def test_sync_add_without_name(self):
        assert build_command("8", Asker("https://x/1", "")) == ["sync", "add", "https://x/1"]

    def test_unknown_choice_returns_none(self):
        assert build_command("99", Asker()) is None

    def test_url_is_stripped(self):
        assert build_command("1", Asker("  https://youtu.be/a  ", ""))[1] == "https://youtu.be/a"


class TestRunMenu:
    def _run(self, *answers, runner=None):
        out = io.StringIO()
        calls = []

        def default_runner(argv):
            calls.append(argv)
            return 0

        code = run_menu(runner or default_runner, ask=Asker(*answers), out=out)
        return code, calls, out.getvalue()

    def test_exit_immediately(self):
        code, calls, text = self._run("0")
        assert code == 0
        assert calls == []
        assert "再見" in text

    def test_runs_selected_command(self):
        _, calls, _ = self._run("1", "https://youtu.be/a", "", "")
        assert calls == [["dl", "https://youtu.be/a"]]

    def test_loops_until_exit(self):
        _, calls, _ = self._run("7", "", "7", "", "0")
        assert calls == [["history", "list"], ["history", "list"]]

    def test_blank_input_cancels_back_to_menu_without_running(self):
        _, calls, _ = self._run("1", "", "", "", "0")
        assert calls == []

    def test_eof_ends_cleanly_instead_of_looping(self):
        # 這正是原本 .bat 無窮迴圈的情境：輸入被關掉時必須收尾，不能空轉
        code, calls, text = self._run()
        assert code == 0
        assert calls == []
        assert "再見" in text

    def test_returns_last_exit_code(self):
        code, _, _ = self._run("7", "", "0", runner=lambda argv: 4)
        assert code == 4

    def test_keyboard_interrupt_during_command_is_survivable(self):
        def boom(argv):
            raise KeyboardInterrupt

        code, _, text = self._run("7", "", "0", runner=boom)
        assert "已中斷" in text
        assert code == 130

    def test_q_also_exits(self):
        _, calls, _ = self._run("q")
        assert calls == []


class TestAskLanguages:
    def test_enter_means_use_default(self):
        assert ask_languages(Asker(""), "subs") == ""

    def test_single_choice(self):
        assert ask_languages(Asker("1"), "subs") == "繁中"

    def test_multiple_choices_keep_order(self):
        assert ask_languages(Asker("3,1"), "subs") == "英,繁中"

    def test_full_width_comma(self):
        assert ask_languages(Asker("1，3"), "subs") == "繁中,英"

    def test_all_six(self):
        assert ask_languages(Asker("1,2,3,4,5,6"), "subs") == "繁中,簡中,英,日,韓,西班牙"

    def test_deduplicates(self):
        assert ask_languages(Asker("1,1,3"), "subs") == "繁中,英"

    def test_invalid_tokens_ignored(self):
        assert ask_languages(Asker("1,99,abc"), "subs") == "繁中"

    def test_all_invalid_falls_back_to_default(self):
        assert ask_languages(Asker("99"), "subs") == ""

    def test_prompt_lists_every_language(self):
        asker = Asker("")
        ask_languages(asker, "subs")
        for _, name in LANGUAGE_CHOICES:
            assert name in asker.prompts[0]


class TestPlaylistPrompts:
    def test_plain_video_asks_nothing_extra(self):
        # 單曲網址：只會問歌詞，不會問清單
        assert build_command("1", Asker("https://youtu.be/a", "")) == [
            "dl", "https://youtu.be/a"
        ]

    def test_pure_playlist_offers_folder(self):
        url = "https://www.youtube.com/playlist?list=PL1"
        assert build_command("1", Asker(url, "", "y")) == [
            "dl", url, "--playlist-folder"
        ]

    def test_pure_playlist_folder_declined(self):
        url = "https://www.youtube.com/playlist?list=PL1"
        assert build_command("1", Asker(url, "", "")) == ["dl", url]

    def test_ambiguous_url_can_choose_single(self):
        url = "https://www.youtube.com/watch?v=a&list=PL1"
        assert build_command("1", Asker(url, "", "")) == ["dl", url, "--single"]

    def test_ambiguous_url_can_choose_whole_playlist(self):
        url = "https://www.youtube.com/watch?v=a&list=PL1"
        assert build_command("1", Asker(url, "", "y", "y")) == [
            "dl", url, "--playlist", "--playlist-folder"
        ]

    def test_batch_video_with_subtitles(self):
        # 使用者要的：整張清單下載影片，而且能選字幕語言
        url = "https://www.youtube.com/playlist?list=PL1"
        assert build_command("4", Asker(url, "2", "y", "1,3", "y")) == [
            "dl", url, "--video", "1080", "--subs", "繁中,英", "--playlist-folder"
        ]


class TestWechatAutoRedirect:
    """微信網址貼進音樂／影片選項時，應自動改走微信那條路。

    使用者不該需要知道哪個選單編號對應哪個平台。
    """

    WX = "https://weixin.qq.com/sph/AJq0mgzYC0"

    def test_music_option_redirects(self):
        assert build_command("1", Asker(self.WX)) == ["wechat", self.WX]

    def test_video_option_redirects(self):
        assert build_command("4", Asker(self.WX)) == ["wechat", self.WX]

    def test_normal_url_is_not_redirected(self):
        assert build_command("1", Asker("https://youtu.be/a", ""))[0] == "dl"

    def test_bilibili_url_is_not_redirected(self):
        url = "https://www.bilibili.com/video/BV1xx411c7mD"
        assert build_command("1", Asker(url, ""))[:2] == ["dl", url]


class TestAskSite:
    def test_enter_means_youtube(self):
        assert ask_site(Asker("")) == []

    def test_bilibili(self):
        assert ask_site(Asker("2")) == ["--site", "bilibili"]

    def test_invalid_falls_back_to_youtube(self):
        assert ask_site(Asker("99")) == []

    def test_prompt_lists_both_sites(self):
        asker = Asker("")
        ask_site(asker)
        assert "YouTube" in asker.prompts[0] and "Bilibili" in asker.prompts[0]


class TestAskRequired:
    """使用者回報「貼上功能失效」：選了項目、貼上網址，卻立刻跳回選單。

    不論根因是貼上沒進去還是內容夾帶換行，一收到空值就踢回選單都是錯的——
    連重貼的機會都沒有。
    """

    def test_returns_first_non_empty(self):
        assert ask_required(Asker("https://x/1"), "p") == "https://x/1"

    def test_retries_after_blank(self):
        assert ask_required(Asker("", "  ", "https://x/2"), "p") == "https://x/2"

    def test_gives_up_after_three_blanks(self):
        assert ask_required(Asker("", "", ""), "p") == ""

    def test_q_cancels_immediately(self):
        assert ask_required(Asker("q"), "p") == ""
        assert ask_required(Asker("取消"), "p") == ""

    def test_retry_prompt_explains_how_to_paste(self):
        asker = Asker("", "https://x/3")
        ask_required(asker, "p")
        assert "Ctrl+V" in asker.prompts[1]
        assert "右鍵" in asker.prompts[1]

    def test_strips_whitespace(self):
        assert ask_required(Asker("  https://x/4  "), "p") == "https://x/4"

    def test_menu_lets_user_retry_a_failed_paste(self):
        # 第一次貼上落空，第二次成功——不該中途跳回選單
        assert build_command("4", Asker("", "https://youtu.be/a", "", "")) == [
            "dl", "https://youtu.be/a", "--video", "720"
        ]


class TestInterfaceLanguage:
    """介面語言切換：選單、提示、字幕語言名稱都要跟著換。"""

    @pytest.fixture(autouse=True)
    def restore(self):
        from ytmusic.i18n import language, set_language

        before = language()
        yield
        set_language(before)

    def test_menu_renders_in_each_language(self):
        from ytmusic.i18n import LANGUAGE_CODES, set_language

        expected = {"zh-Hant": "離開", "ja": "終了", "en": "Quit",
                    "ko": "종료", "es": "Salir", "fi": "Poistu"}
        for code in LANGUAGE_CODES:
            set_language(code)
            assert f"[0] {expected[code]}" in render_menu()

    def test_language_option_is_always_findable(self):
        # 看不懂目前語言的人得找得到出口，所以每個語言都留著 "Language"
        from ytmusic.i18n import LANGUAGE_CODES, set_language

        for code in LANGUAGE_CODES:
            set_language(code)
            assert "language" in render_menu().lower()

    def test_prompts_follow_the_language(self):
        from ytmusic.i18n import set_language

        set_language("fi")
        asker = Asker("https://youtu.be/a", "", "")
        build_command("1", asker)
        assert any("Liitä URL" in p for p in asker.prompts)

    def test_subtitle_values_stay_chinese(self):
        # 送進 --subs 的值是 lyrics.py 認得的中文別名，不能跟著介面語言變
        from ytmusic.i18n import set_language

        set_language("en")
        assert ask_languages(Asker("1,3"), "subs") == "繁中,英"

    def test_subtitle_names_are_translated_on_screen(self):
        from ytmusic.i18n import set_language

        set_language("ja")
        asker = Asker("1")
        ask_languages(asker, "subs")
        assert "スペイン語" in asker.prompts[0]

    def test_yes_answers_work_in_other_languages(self):
        from ytmusic.menu import YES

        assert {"kyllä", "예", "はい", "sí"} <= YES


class TestChooseLanguage:
    @pytest.fixture(autouse=True)
    def restore(self):
        from ytmusic.i18n import language, set_language

        before = language()
        yield
        set_language(before)

    def test_marks_the_current_language(self):
        from ytmusic.i18n import set_language
        from ytmusic.menu import render_language_menu

        set_language("ko")
        line = [l for l in render_language_menu().splitlines() if "한국어" in l][0]
        assert "*" in line

    def test_applies_and_saves(self, tmp_path, monkeypatch):
        from ytmusic import config as config_mod
        from ytmusic.i18n import language, set_language
        from ytmusic.menu import choose_language

        monkeypatch.setattr(config_mod.Config, "path",
                            classmethod(lambda cls: tmp_path / "c.json"))
        set_language("zh-Hant")
        out = io.StringIO()
        assert choose_language(Asker("6"), out) == "fi"
        assert language() == "fi"
        assert config_mod.Config.load(tmp_path / "c.json").ui_language == "fi"

    def test_blank_keeps_current(self):
        from ytmusic.i18n import set_language
        from ytmusic.menu import choose_language

        set_language("ja")
        assert choose_language(Asker(""), io.StringIO()) == "ja"

    def test_out_of_range_keeps_current(self):
        from ytmusic.i18n import set_language
        from ytmusic.menu import choose_language

        set_language("ja")
        assert choose_language(Asker("99"), io.StringIO()) == "ja"
