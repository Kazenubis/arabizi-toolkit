import pytest

from arabizi.digits import EASTERN, PERSIAN, WESTERN, convert_digits, to_eastern, to_persian, to_western


def test_eastern_and_persian_to_western():
    assert to_western("٢٠٢٦") == "2026"
    assert to_western("۱۴۰۵") == "1405"


def test_letters_are_left_alone():
    assert to_western("عندي ٣ قطط") == "عندي 3 قطط"
    assert to_eastern("Flat 12") == "Flat ١٢"


def test_round_trip_all_systems():
    assert to_eastern(WESTERN) == EASTERN
    assert to_persian(WESTERN) == PERSIAN
    assert to_western(to_eastern(WESTERN)) == WESTERN
    assert to_western(to_persian(WESTERN)) == WESTERN
    assert to_eastern(PERSIAN) == EASTERN


def test_unknown_system_raises():
    with pytest.raises(ValueError):
        convert_digits("123", "roman")


def test_empty_string():
    assert to_western("") == ""
