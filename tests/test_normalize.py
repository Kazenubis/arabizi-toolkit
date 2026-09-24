from arabizi.normalize import (
    collapse_whitespace,
    normalize,
    normalize_alef,
    normalize_taa_marbuta,
    normalize_yaa,
    remove_tatweel,
    strip_tashkeel,
)


def test_strip_tashkeel_removes_harakat_tanween_shadda_sukun():
    assert strip_tashkeel("مُحَمَّدٌ") == "محمد"
    assert strip_tashkeel("أَهْلًا") == "أهلا"


def test_strip_tashkeel_removes_superscript_alef():
    assert strip_tashkeel("هٰذا") == "هذا"


def test_remove_tatweel():
    assert remove_tatweel("جـــميل") == "جميل"


def test_normalize_alef_variants():
    assert normalize_alef("أحمد إبراهيم آمن ٱلله") == "احمد ابراهيم امن الله"


def test_normalize_alef_handles_decomposed_madda():
    assert normalize_alef("آ") == "ا"


def test_yaa_and_taa_marbuta_helpers():
    assert normalize_yaa("مصطفى") == "مصطفي"
    assert normalize_taa_marbuta("مدرسة") == "مدرسه"


def test_collapse_whitespace():
    assert collapse_whitespace("  صباح \t\n الخير  ") == "صباح الخير"


def test_normalize_defaults_keep_taa_marbuta():
    text = "  مُسْتَشْفَى   الجـــامِعَة  "
    assert normalize(text) == "مستشفي الجامعة"


def test_normalize_flags():
    text = "مستشفى الجامعة"
    assert normalize(text, taa_marbuta=True) == "مستشفي الجامعه"
    assert normalize(text, yaa=False) == "مستشفى الجامعة"
    assert normalize("أَحمد", tashkeel=False, alef=False) == "أَحمد"


def test_normalize_empty_string():
    assert normalize("") == ""
    assert strip_tashkeel("") == ""
    assert collapse_whitespace("   ") == ""
