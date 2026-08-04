import pytest

from ytmusic.i18n import (
    DEFAULT, LANGUAGE_CODES, LANGUAGES, MESSAGES, detect, language,
    language_name, match, set_language, t,
)


@pytest.fixture(autouse=True)
def restore_language():
    before = language()
    yield
    set_language(before)


class TestCatalogueIsComplete:
    """少一句翻譯就會在畫面上冒出另一種語言，所以整份表都要驗。"""

    def test_every_message_has_every_language(self):
        missing = {
            f"{key}/{code}"
            for key, entry in MESSAGES.items()
            for code in LANGUAGE_CODES
            if not entry.get(code)
        }
        assert missing == set()

    def test_no_stray_languages(self):
        extra = {
            f"{key}/{code}"
            for key, entry in MESSAGES.items()
            for code in entry
            if code not in LANGUAGE_CODES
        }
        assert extra == set()

    def test_placeholders_match_across_languages(self):
        import re

        for key, entry in MESSAGES.items():
            wanted = set(re.findall(r"\{(\w+)\}", entry[DEFAULT]))
            for code, text in entry.items():
                assert set(re.findall(r"\{(\w+)\}", text)) == wanted, f"{key}/{code}"

    def test_six_languages_as_requested(self):
        assert LANGUAGE_CODES == ("zh-Hant", "ja", "en", "ko", "es", "fi")

    def test_each_language_names_itself(self):
        # 看不懂目前介面的人，只認得出自己母語長什麼樣
        assert dict(LANGUAGES)["ja"] == "日本語"
        assert dict(LANGUAGES)["ko"] == "한국어"
        assert dict(LANGUAGES)["fi"] == "Suomi"


class TestSetLanguage:
    def test_switches(self):
        assert set_language("fi") == "fi"
        assert t("menu.quit") == "Poistu"

    def test_ignores_unknown_codes(self):
        set_language("en")
        assert set_language("klingon") == "en"

    def test_ignores_empty(self):
        set_language("ja")
        assert set_language("") == "ja"
        assert set_language(None) == "ja"

    def test_language_name(self):
        assert language_name("es") == "Español"
        assert language_name("xx") == "xx"


class TestTranslate:
    def test_formats_placeholders(self):
        set_language("en")
        assert t("ui.saved", name="Suomi") == "Switched to Suomi."

    def test_unknown_key_returns_the_key(self):
        # 畫面上出現代號很醜，但比整個崩掉好，而且一眼看得出漏了什麼
        assert t("no.such.key") == "no.such.key"

    def test_falls_back_to_source_language(self, monkeypatch):
        monkeypatch.setitem(MESSAGES, "tmp.key", {DEFAULT: "原文"})
        set_language("fi")
        assert t("tmp.key") == "原文"


class TestMatch:
    def test_posix_locales(self):
        assert match("ja_JP.UTF-8") == "ja"
        assert match("fi_FI.UTF-8") == "fi"
        assert match("ko_KR") == "ko"
        assert match("es-ES") == "es"

    def test_any_chinese_maps_to_traditional(self):
        # 簡體圈的使用者看繁體仍讀得懂，比丟英文給他們好
        assert match("zh_TW") == "zh-Hant"
        assert match("zh_CN.UTF-8") == "zh-Hant"
        assert match("zh") == "zh-Hant"

    def test_unknown_falls_back_to_english(self):
        assert match("de_DE.UTF-8") == "en"
        assert match("") == "en"
        assert match(None) == "en"


class TestDetect:
    def test_reads_environment(self):
        assert detect({"LANG": "ko_KR.UTF-8"}) == "ko"

    def test_lc_all_wins(self):
        assert detect({"LC_ALL": "fi_FI.UTF-8", "LANG": "ja_JP"}) == "fi"


class TestExplanationsAreTranslated:
    """切了語言卻只有選單變，等於沒切——真正要看懂的是失敗時那幾行。"""

    @pytest.fixture(autouse=True)
    def restore(self):
        before = language()
        yield
        set_language(before)

    def test_download_flow_follows_the_language(self):
        set_language("en")
        assert t("dl.resolving", what=t("noun.url")) == "Resolving the URL…"
        assert t("dl.nothing") == "Nothing found to download."
        assert t("dl.plan", total=3, pending=2) == "3 found, 2 to download"

    def test_failure_lines_follow_the_language(self):
        set_language("es")
        assert t("err.unreadable", url="x", error="y").startswith("✖ No se pudo leer")
        assert "conexión" in t("net.hint")

    def test_doctor_follows_the_language(self):
        set_language("fi")
        assert t("doctor.env") == "Ympäristön tarkistus"
        assert "verko" in t("conclusion.none")  # 芬蘭語會變格：verkosta / verkossa

    def test_wechat_follows_the_language(self):
        set_language("ko")
        assert t("wx.asking").startswith("위챗")
        assert "위챗" in t("wx.blocked_hint")

    def test_long_hints_exist_in_every_language(self):
        # 這幾段是失敗時唯一的線索，缺譯會讓使用者卡死
        for key in ("net.hint", "wx.blocked_hint", "conclusion.short_blocked"):
            for code in LANGUAGE_CODES:
                assert len(MESSAGES[key][code]) > 40, f"{key}/{code}"
