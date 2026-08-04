"""啟動檔的把關測試。

這兩個檔案是新使用者碰到的第一個東西，而且完全不在 Python 的測試範圍內——
壞了不會有任何測試變紅，只有使用者會看到。所以至少把踩過的坑釘住。
"""

import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
BAT = ROOT / "下載.bat"
COMMAND = ROOT / "下載.command"


class TestBatchFileEncoding:
    """cmd.exe 對編碼與換行極度敏感，錯了會把整個檔案切碎。"""

    def test_is_pure_ascii(self):
        assert all(byte < 128 for byte in BAT.read_bytes())

    def test_uses_crlf_everywhere(self):
        raw = BAT.read_bytes()
        assert raw.count(b"\n") == raw.count(b"\r\n")

    def test_command_file_uses_lf(self):
        raw = COMMAND.read_bytes()
        assert b"\r\n" not in raw


class TestPythonDetection:
    """where python 會被 Windows 的 Store 佔位程式騙過去。

    那支程式在 PATH 裡、名字找得到，執行卻只印「Python was not found」。
    使用者實際踩到：設定看似通過，下一步才莫名其妙失敗。
    """

    def test_bat_runs_the_interpreter_instead_of_just_locating_it(self):
        text = BAT.read_text(encoding="ascii")
        assert "import sys" in text and "version_info" in text

    def test_bat_does_not_trust_bare_where_python(self):
        text = BAT.read_text(encoding="ascii")
        # 只准用來「解釋 Store 佔位程式」，不能拿來決定 PY
        assert 'set "PY=%%~C"' in text
        assert 'where python >nul 2>&1 && set "PY=python"' not in text

    def test_bat_explains_the_store_placeholder(self):
        text = BAT.read_text(encoding="ascii")
        assert "Microsoft Store" in text
        assert "App execution aliases" in text

    def test_bat_requires_a_new_enough_python(self):
        assert "(3,9)" in BAT.read_text(encoding="ascii")

    def test_command_runs_the_interpreter_too(self):
        text = COMMAND.read_text(encoding="utf-8")
        assert "version_info" in text

    def test_both_try_several_candidates(self):
        assert "py -3" in BAT.read_text(encoding="ascii")
        assert "python3 python" in COMMAND.read_text(encoding="utf-8")


class TestGuidedSetup:
    """沒裝 Python 的人需要被牽著走，不是看到一句 error 就卡死。"""

    @pytest.mark.parametrize("path", [BAT, COMMAND])
    def test_numbered_steps(self, path):
        text = path.read_text(encoding="utf-8" if path is COMMAND else "ascii")
        assert "step 1 of 2" in text and "step 2 of 2" in text

    def test_bat_offers_winget(self):
        text = BAT.read_text(encoding="ascii")
        assert "winget install -e --id Python.Python.3.12" in text

    def test_command_offers_brew(self):
        assert "brew install python" in COMMAND.read_text(encoding="utf-8")

    @pytest.mark.parametrize("path", [BAT, COMMAND])
    def test_tells_the_user_to_reopen_the_window(self, path):
        # 新裝的 Python 進不了已經開著的視窗的 PATH，不講的話下一次一樣失敗
        text = path.read_text(encoding="utf-8" if path is COMMAND else "ascii")
        assert "reopen this window" in text

    def test_bat_mentions_add_to_path_checkbox(self):
        # 官方安裝程式最常被漏勾的一格
        assert "Add python.exe to PATH" in BAT.read_text(encoding="ascii")

    @pytest.mark.parametrize("path", [BAT, COMMAND])
    def test_suggests_ensurepip_when_install_fails(self, path):
        text = path.read_text(encoding="utf-8" if path is COMMAND else "ascii")
        assert "ensurepip" in text


class TestGitAttributes:
    """換行格式的真正保證在 .gitattributes——它決定 checkout 時寫出什麼。"""

    def test_bat_is_forced_to_crlf(self):
        text = (ROOT / ".gitattributes").read_text(encoding="utf-8")
        assert "*.bat text eol=crlf" in text

    def test_command_is_forced_to_lf(self):
        text = (ROOT / ".gitattributes").read_text(encoding="utf-8")
        assert "*.command text eol=lf" in text
