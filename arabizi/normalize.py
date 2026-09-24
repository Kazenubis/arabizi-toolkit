"""Arabic text normalization: diacritics, tatweel, letter variants and whitespace.

Every operation is a small standalone function, and `normalize()` chains them
behind keyword flags so callers can pick exactly what they want.
"""

from __future__ import annotations

import re
import unicodedata

# Tanween (U+064B-U+064D), harakat (U+064E-U+0650), shadda (U+0651),
# sukun (U+0652) and the superscript (dagger) alef (U+0670).
TASHKEEL = "".join(chr(code) for code in range(0x064B, 0x0653)) + "ٰ"
TATWEEL = "ـ"
ALEF_VARIANTS = "أإآٱ"

_TASHKEEL_TABLE = str.maketrans("", "", TASHKEEL)
_ALEF_TABLE = str.maketrans({variant: "ا" for variant in ALEF_VARIANTS})
_WHITESPACE = re.compile(r"\s+")


def strip_tashkeel(text: str) -> str:
    """Remove harakat, tanween, shadda, sukun and the superscript alef."""
    return text.translate(_TASHKEEL_TABLE)


def remove_tatweel(text: str) -> str:
    """Remove the kashida/tatweel stretching character (ـ)."""
    return text.replace(TATWEEL, "")


def normalize_alef(text: str) -> str:
    """Map أ إ آ ٱ to a bare alef (ا).

    The text is NFC-composed first, so a decomposed "ا + madda" is caught too.
    """
    return unicodedata.normalize("NFC", text).translate(_ALEF_TABLE)


def normalize_yaa(text: str) -> str:
    """Map alef maksura (ى) to yaa (ي), the way most Egyptians type it anyway."""
    return text.replace("ى", "ي")


def normalize_taa_marbuta(text: str) -> str:
    """Map taa marbuta (ة) to haa (ه)."""
    return text.replace("ة", "ه")


def collapse_whitespace(text: str) -> str:
    """Squash any run of whitespace into one space and trim the ends."""
    return _WHITESPACE.sub(" ", text).strip()


def normalize(
    text: str,
    *,
    tashkeel: bool = True,
    tatweel: bool = True,
    alef: bool = True,
    yaa: bool = True,
    taa_marbuta: bool = False,
    whitespace: bool = True,
) -> str:
    """Apply the selected normalization steps in a fixed, predictable order."""
    steps = (
        (tashkeel, strip_tashkeel),
        (tatweel, remove_tatweel),
        (alef, normalize_alef),
        (yaa, normalize_yaa),
        (taa_marbuta, normalize_taa_marbuta),
        (whitespace, collapse_whitespace),
    )
    for enabled, step in steps:
        if enabled:
            text = step(text)
    return text
