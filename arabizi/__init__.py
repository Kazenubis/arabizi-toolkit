"""Arabizi Toolkit: clean Arabic text and turn Egyptian Franco-Arabic into Arabic script."""

from .arabizi import transliterate, transliterate_word
from .detect import ScriptRatio, arabizi_words, is_arabizi, script_ratio
from .digits import convert_digits, to_eastern, to_persian, to_western
from .normalize import (
    collapse_whitespace,
    normalize,
    normalize_alef,
    normalize_taa_marbuta,
    normalize_yaa,
    remove_tatweel,
    strip_tashkeel,
)

__version__ = "0.1.0"

__all__ = [
    "ScriptRatio",
    "arabizi_words",
    "collapse_whitespace",
    "convert_digits",
    "is_arabizi",
    "normalize",
    "normalize_alef",
    "normalize_taa_marbuta",
    "normalize_yaa",
    "remove_tatweel",
    "script_ratio",
    "strip_tashkeel",
    "to_eastern",
    "to_persian",
    "to_western",
    "transliterate",
    "transliterate_word",
]
