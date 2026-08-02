import io

import pytest

from ytmusic.menu import MENU_ITEMS, Cancelled, build_command, render_menu, run_menu


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

    def test_blank_url_cancels(self):
        assert build_command("1", Asker("   ")) is None

    def test_search(self):
        assert build_command("2", Asker("告白氣球")) == ["search", "告白氣球"]

    def test_artist_search(self):
        assert build_command("3", Asker("周杰倫")) == ["search", "--artist", "周杰倫"]

    def test_artist_blank_cancels(self):
        assert build_command("3", Asker("  ")) is None

    def test_video_defaults_to_720(self):
        assert build_command("4", Asker("https://youtu.be/a", "", "")) == [
            "dl", "https://youtu.be/a", "--video", "720"
        ]

    def test_audio_can_ask_for_lyrics(self):
        assert build_command("1", Asker("https://youtu.be/a", "y")) == [
            "dl", "https://youtu.be/a", "--lyrics"
        ]

    def test_video_can_ask_for_subs(self):
        assert build_command("4", Asker("https://youtu.be/a", "", "y")) == [
            "dl", "https://youtu.be/a", "--video", "720", "--subs"
        ]

    @pytest.mark.parametrize("answer,expected", [("1", "720"), ("2", "1080"), ("3", "best")])
    def test_video_quality_choices(self, answer, expected):
        command = build_command("4", Asker("https://youtu.be/a", answer, ""))
        assert command[-1] == expected

    def test_unknown_video_quality_falls_back(self):
        assert build_command("4", Asker("https://youtu.be/a", "99", ""))[-1] == "720"

    def test_sync(self):
        assert build_command("5", Asker()) == ["sync"]

    def test_history(self):
        assert build_command("6", Asker()) == ["history", "list"]

    def test_sync_add_with_name(self):
        assert build_command("7", Asker("https://x/1", "我的最愛")) == [
            "sync", "add", "https://x/1", "--name", "我的最愛"
        ]

    def test_sync_add_without_name(self):
        assert build_command("7", Asker("https://x/1", "")) == ["sync", "add", "https://x/1"]

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
        _, calls, _ = self._run("6", "", "6", "", "0")
        assert calls == [["history", "list"], ["history", "list"]]

    def test_blank_input_cancels_back_to_menu_without_running(self):
        _, calls, _ = self._run("1", "", "0")
        assert calls == []

    def test_eof_ends_cleanly_instead_of_looping(self):
        # 這正是原本 .bat 無窮迴圈的情境：輸入被關掉時必須收尾，不能空轉
        code, calls, text = self._run()
        assert code == 0
        assert calls == []
        assert "再見" in text

    def test_returns_last_exit_code(self):
        code, _, _ = self._run("6", "", "0", runner=lambda argv: 4)
        assert code == 4

    def test_keyboard_interrupt_during_command_is_survivable(self):
        def boom(argv):
            raise KeyboardInterrupt

        code, _, text = self._run("6", "", "0", runner=boom)
        assert "已中斷" in text
        assert code == 130

    def test_q_also_exits(self):
        _, calls, _ = self._run("q")
        assert calls == []
