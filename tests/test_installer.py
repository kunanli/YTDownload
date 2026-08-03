import sys

from ytmusic.installer import (
    Dependency, ffmpeg_command, install_all, notice, offer, pip_command,
)


def dep(key="ffmpeg", *, required=True, command=None):
    return Dependency(key, key, f"缺了{key}會怎樣", required, command, f"  手動裝 {key}")


class TestPipCommand:
    def test_uses_python_m_pip(self):
        # Windows 上 pip 的執行檔常常不在 PATH，跟 playwright 同一個坑
        assert pip_command("mutagen") == [sys.executable, "-m", "pip", "install", "mutagen"]

    def test_keeps_version_specifier_intact(self):
        assert pip_command("curl_cffi>=0.10,<0.16")[-1] == "curl_cffi>=0.10,<0.16"


class TestFfmpegCommand:
    def test_windows_uses_winget(self):
        command = ffmpeg_command("Windows", {"winget": True})
        assert command[:2] == ["winget", "install"]
        assert "Gyan.FFmpeg" in command

    def test_macos_uses_brew(self):
        assert ffmpeg_command("Darwin", {"brew": True}) == ["brew", "install", "ffmpeg"]

    def test_none_without_a_package_manager(self):
        assert ffmpeg_command("Windows", {"winget": False}) is None
        assert ffmpeg_command("Darwin", {"brew": False}) is None

    def test_linux_is_left_manual(self):
        # apt 需要 sudo，替使用者提權太超過了
        assert ffmpeg_command("Linux", {"winget": True, "brew": True}) is None


class TestNotice:
    def test_silent_when_nothing_missing(self):
        assert notice([]) == ""

    def test_marks_required_and_optional(self):
        text = notice([dep("ffmpeg"), dep("curl_cffi", required=False)])
        assert "[必要] ffmpeg" in text
        assert "[選用] curl_cffi" in text

    def test_says_what_breaks(self):
        assert "缺了ffmpeg會怎樣" in notice([dep("ffmpeg")])


class TestInstallAll:
    def test_reports_uninstallable_items(self, monkeypatch, capsys):
        import ytmusic.installer as mod

        monkeypatch.setattr(mod, "run", lambda command, out: True)
        still = install_all([dep("ffmpeg", command=None), dep("mutagen", command=["x"])],
                            out=sys.stderr)
        assert [d.key for d in still] == ["ffmpeg"]

    def test_reports_failed_installs(self, monkeypatch):
        import ytmusic.installer as mod

        monkeypatch.setattr(mod, "run", lambda command, out: False)
        still = install_all([dep("mutagen", command=["x"])], out=sys.stderr)
        assert [d.key for d in still] == ["mutagen"]


class TestOffer:
    def test_does_nothing_when_nothing_missing(self):
        assert offer([], ask=lambda p: "y", out=sys.stderr) == []

    def test_optional_only_is_not_pushed(self, capsys):
        still = offer([dep("curl_cffi", required=False, command=["x"])],
                      ask=lambda p: pytest_fail(), out=sys.stderr)
        # 沒問就代表沒打擾使用者
        assert [d.key for d in still] == ["curl_cffi"]

    def test_declining_leaves_manual_steps(self, monkeypatch, capsys):
        import ytmusic.installer as mod

        monkeypatch.setattr(mod.sys.stdin, "isatty", lambda: True, raising=False)
        monkeypatch.setattr(mod, "run", lambda command, out: pytest_fail())
        still = offer([dep("ffmpeg", command=["x"])], ask=lambda p: "n", out=sys.stderr)
        assert [d.key for d in still] == ["ffmpeg"]
        assert "手動裝 ffmpeg" in capsys.readouterr().err

    def test_installs_after_consent(self, monkeypatch):
        import ytmusic.installer as mod

        monkeypatch.setattr(mod.sys.stdin, "isatty", lambda: True, raising=False)
        ran = []
        monkeypatch.setattr(mod, "run", lambda command, out: (ran.append(command), True)[1])
        assert offer([dep("ffmpeg", command=["winget"])], ask=lambda p: "",
                     out=sys.stderr) == []
        assert ran == [["winget"]]

    def test_never_installs_without_a_terminal(self, monkeypatch, capsys):
        import ytmusic.installer as mod

        monkeypatch.setattr(mod.sys.stdin, "isatty", lambda: False, raising=False)
        monkeypatch.setattr(mod, "run", lambda command, out: pytest_fail())
        still = offer([dep("ffmpeg", command=["x"])], ask=lambda p: "y", out=sys.stderr)
        assert [d.key for d in still] == ["ffmpeg"]
        assert "手動裝 ffmpeg" in capsys.readouterr().err


def pytest_fail():
    raise AssertionError("不該走到這裡")
