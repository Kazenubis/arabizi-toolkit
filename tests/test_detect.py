from arabizi.detect import ScriptRatio, arabizi_words, is_arabizi, script_ratio


def test_script_ratio_mixed_text():
    assert script_ratio("مرحبا hello") == ScriptRatio(0.5, 0.5)


def test_script_ratio_ignores_marks_tatweel_and_digits():
    assert script_ratio("مُـحَمَّد 2026") == ScriptRatio(1.0, 0.0)


def test_script_ratio_empty():
    assert script_ratio("") == ScriptRatio(0.0, 0.0)


def test_arabizi_words_found_in_order():
    assert arabizi_words("ana 3ayz a5ls el project") == ["3ayz", "a5ls"]


def test_is_arabizi_positive():
    assert is_arabizi("ana 3ayz a5ls el project")
    assert is_arabizi("7abibi")


def test_is_arabizi_rejects_english_with_numbers():
    assert not is_arabizi("meet me at 7pm, 3rd floor")
    assert not is_arabizi("my mp3 player has covid19 stickers")
    assert not is_arabizi("hello world")


def test_is_arabizi_rejects_arabic_script_and_empty():
    assert not is_arabizi("انا عايز اخلص")
    assert not is_arabizi("")
