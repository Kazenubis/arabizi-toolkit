"""Script detection: how Arabic vs Latin a text is, and whether it looks like Arabizi."""

from __future__ import annotations

import re
import unicodedata
from typing import NamedTuple

# Arabic, Arabic Supplement, Arabic Extended-A, Presentation Forms A and B.
_ARABIC_RANGES = ((0x0600, 0x06FF), (0x0750, 0x077F), (0x08A0, 0x08FF), (0xFB50, 0xFDFF), (0xFE70, 0xFEFF))
_TATWEEL = "ـ"

# 2/3/5/7 are the digit letters almost every Egyptian uses. 6, 8 and 9 are left
# out on purpose: they are rarer in Egypt and far more often real numbers.
DIGIT_LETTERS = "2357"
_WORD = re.compile(r"[A-Za-z0-9']+")
# English tokens that mix letters and digits: 3rd, 7pm, 5g, 2x, 3kg ...
_ENGLISH_NUMERIC = re.compile(r"\d+(st|nd|rd|th|am|pm|s|k|m|g|x|d|h|kg|km|gb|mb)")
_ENGLISH_WORDS = frozenset({"mp3", "mp4", "h2o", "b2b", "b2c", "p2p", "g2g", "f2f", "w3c"})


class ScriptRatio(NamedTuple):
    """Share of Arabic and Latin letters among the letters of those two scripts."""

    arabic: float
    latin: float


def _is_arabic_letter(ch: str) -> bool:
    code = ord(ch)
    return ch.isalpha() and ch != _TATWEEL and any(lo <= code <= hi for lo, hi in _ARABIC_RANGES)


def _is_latin_letter(ch: str) -> bool:
    return ch.isalpha() and unicodedata.name(ch, "").startswith("LATIN")


def script_ratio(text: str) -> ScriptRatio:
    """Fraction of Arabic vs Latin letters. Digits, marks and punctuation are ignored."""
    arabic = sum(_is_arabic_letter(ch) for ch in text)
    latin = sum(_is_latin_letter(ch) for ch in text)
    total = arabic + latin
    if total == 0:
        return ScriptRatio(0.0, 0.0)
    return ScriptRatio(arabic / total, latin / total)


def _looks_arabizi(word: str) -> bool:
    lowered = word.lower()
    if lowered in _ENGLISH_WORDS or _ENGLISH_NUMERIC.fullmatch(lowered):
        return False
    if re.search(r"\d\d", lowered):  # "covid19", "win32": real numbers, not letters
        return False
    has_letter = any(ch.isalpha() for ch in lowered)
    return has_letter and any(digit in lowered for digit in DIGIT_LETTERS)


def arabizi_words(text: str) -> list[str]:
    """Words that mix Latin letters with the digit letters 2/3/5/7, in order."""
    return [word for word in _WORD.findall(text) if _looks_arabizi(word)]


def is_arabizi(text: str) -> bool:
    """Heuristic: mostly Latin letters, with at least one word like "3ayz" or "7abibi"."""
    if not arabizi_words(text):
        return False
    return script_ratio(text).latin >= 0.5
