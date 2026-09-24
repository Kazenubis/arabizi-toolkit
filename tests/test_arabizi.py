import pytest

from arabizi.arabizi import Token, tokenize, transliterate, transliterate_word


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        ("7abibi", "حبيبي"),
        ("shukran", "شكرا"),
        ("3afwan", "عفوا"),
        ("7elwa", "حلوة"),
        ("keteer", "كتير"),
        ("kwayyes", "كويس"),
        ("ma3lesh", "معلش"),
        ("saa3a", "ساعة"),
        ("3ayza", "عايزة"),
        ("ya3ni", "يعني"),
        ("ma9r", "مصر"),
        ("6ab3an", "طبعا"),
    ],
)
def test_rule_based_words(word, expected):
    assert transliterate_word(word, lexicon=False) == expected


def test_longest_match_prefers_digraphs():
    assert tokenize("sh") == [Token("C", "ش")]
    assert transliterate_word("shams", lexicon=False) == "شمس"
    assert transliterate_word("dhahab", lexicon=False) == "ذهب"
    assert transliterate_word("kharoof", lexicon=False) == transliterate_word("5aroof", lexicon=False) == "خروف"


def test_apostrophe_digit_letters():
    assert transliterate_word("3'areeb", lexicon=False) == "غريب"
    assert transliterate_word("3arabi", lexicon=False) == "عربي"


def test_el_prefix_inside_word_and_standalone():
    assert transliterate_word("elbeet") == "البيت"
    assert transliterate("el beet") == "البيت"
    assert transliterate("el shams") == "الشمس"
    # too short to be a prefix: "alam" is ألم, not ال + ام
    assert transliterate_word("alam", lexicon=False) == "الم"


def test_w_joins_next_word():
    assert transliterate("ahlan w sahlan") == "اهلا وسهلا"


def test_taa_marbuta_is_configurable():
    assert transliterate_word("madrasa", lexicon=False) == "مدرسة"
    assert transliterate_word("madrasa", taa_marbuta=False, lexicon=False) == "مدرسا"
    assert transliterate_word("7elwah", taa_marbuta=False, lexicon=False) == "حلوه"
    # one consonant is not enough for ة
    assert transliterate_word("ana", lexicon=False) == "انا"


def test_hamza_seats_for_digit_2():
    assert transliterate_word("sa2al", lexicon=False) == "سأل"
    assert transliterate_word("mas2ala", lexicon=False) == "مسألة"
    assert transliterate_word("samaa2", lexicon=False) == "سماء"
    # known limitation: Cairene "2" is often ق (قلب), the rules can't know that
    assert transliterate_word("2alb", lexicon=False) == "ألب"


def test_lexicon_overrides_rules():
    assert transliterate_word("enta") == "إنت"
    assert transliterate_word("enta", lexicon=False) == "انتة"


def test_sentence_numbers_and_punctuation():
    assert transliterate("ana 3ayz a5ls el project") == "أنا عايز اخلس البرجكت"
    assert transliterate("7abibi, 2026?") == "حبيبي، 2026؟"
    assert transliterate("7abibi?", arabic_punctuation=False) == "حبيبي?"


def test_case_insensitive_and_arabic_passthrough():
    assert transliterate("7ABIBI") == "حبيبي"
    assert transliterate("مصر w 7abibi") == "مصر وحبيبي"


def test_empty_input():
    assert transliterate("") == ""
    assert tokenize("") == []
