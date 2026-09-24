"""Rule-based transliteration from Egyptian Arabizi (Franco-Arabic) to Arabic script.

This is a heuristic, not a dictionary. Arabizi throws away information Arabic
script needs (short vs long vowels, hamza seats, س vs ص, and the Cairene "2"
that usually stands for ق), so the rules pick the most common reading and stay
deterministic. The README lists what it gets right and where it breaks.

Pipeline for one word:
    lexicon lookup -> "el"/"al" prefix -> longest-match tokenizer
    -> collapse doubled consonants -> context rules (position, neighbours).
"""

from __future__ import annotations

import re
from typing import NamedTuple


class Token(NamedTuple):
    """One unit produced by the longest-match tokenizer."""

    kind: str  # "C" consonant, "V" vowel, "H" hamza (the digit 2)
    value: str  # Arabic letter(s) for "C"; the Latin vowel(s) for "V" and "H"


# "8" for ق is the Gulf/Levantine habit. In Cairo ق is pronounced as a glottal
# stop, so people write "2" ("2alb" = قلب) or "q"; 8 is kept for completeness.
DIGIT_LETTERS = {
    "3": "ع", "5": "خ", "6": "ط", "7": "ح", "8": "ق", "9": "ص",
    "3'": "غ", "7'": "خ", "6'": "ظ", "9'": "ض",
}
DIGRAPHS = {"sh": "ش", "ch": "ش", "kh": "خ", "gh": "غ", "th": "ث", "dh": "ذ"}
LETTERS = {
    "b": "ب", "p": "ب", "t": "ت", "g": "ج", "j": "ج", "d": "د", "r": "ر",
    "z": "ز", "s": "س", "f": "ف", "v": "ف", "q": "ق", "k": "ك", "c": "ك",
    "l": "ل", "m": "م", "n": "ن", "h": "ه", "w": "و", "y": "ي", "x": "كس",
}
SHORT_VOWELS = ("a", "e", "i", "o", "u")
LONG_VOWELS = {"aa": "ا", "ee": "ي", "ii": "ي", "oo": "و", "ou": "و", "uu": "و"}

# Very common Egyptian words that no small rule set spells right ("enta" would
# otherwise come out as "انتة"). Used only when lexicon=True.
LEXICON = {
    "ana": "أنا", "enta": "إنت", "inta": "إنت", "enti": "إنتي", "inti": "إنتي",
    "ehna": "إحنا", "e7na": "إحنا", "ento": "إنتو", "entu": "إنتو",
    "howa": "هو", "huwa": "هو", "heya": "هي", "hiya": "هي", "homa": "هما",
    "da": "ده", "dah": "ده", "de": "دي", "di": "دي", "keda": "كده",
    "elly": "اللي", "elli": "اللي", "fe": "في", "fi": "في", "men": "من", "min": "من",
    "mesh": "مش", "msh": "مش", "mish": "مش", "leh": "ليه", "eh": "إيه",
    "ezay": "إزاي", "ezzay": "إزاي", "fein": "فين", "feen": "فين", "emta": "إمتى",
    "3ala": "على", "ma3a": "مع", "yalla": "يلا", "allah": "الله",
    "wallah": "والله", "wallahi": "والله",
    "inshallah": "إن شاء الله", "insha2allah": "إن شاء الله",
}

# Stand-alone words that glue onto the next word ("el bet" -> "البت").
PREFIX_WORDS = {"el": "ال", "al": "ال", "w": "و"}
PUNCTUATION = str.maketrans({"?": "؟", ",": "،", ";": "؛"})

_INITIAL_HAMZA = {
    "": "أ", "a": "أ", "o": "أ", "u": "أ", "e": "إ", "i": "إ",
    "aa": "آ", "ee": "إي", "ii": "إي", "oo": "أو", "ou": "أو", "uu": "أو",
}
_MEDIAL_HAMZA = {
    "": "ء", "a": "أ", "e": "ئ", "i": "ئ", "o": "ؤ", "u": "ؤ",
    "aa": "آ", "ee": "ئي", "ii": "ئي", "oo": "ؤو", "ou": "ؤو", "uu": "ؤو",
}
_FINAL_VOWEL = {"a": "ا", "e": "ي", "i": "ي", "o": "و", "u": "و", **LONG_VOWELS}
_YAA = Token("C", "ي")
_HAA = Token("C", "ه")
_WORD_SPLIT = re.compile(r"([A-Za-z0-9']+)")
_SPACES = re.compile(r"[ \t]+")


def _build_table() -> dict[str, Token]:
    """Every Latin chunk the tokenizer knows, mapped to its token."""
    table: dict[str, Token] = {}
    for mapping in (LETTERS, DIGRAPHS, DIGIT_LETTERS):
        table.update({latin: Token("C", arabic) for latin, arabic in mapping.items()})
    for vowel in (*SHORT_VOWELS, *LONG_VOWELS):
        table[vowel] = Token("V", vowel)
        table["2" + vowel] = Token("H", vowel)
    table["2"] = Token("H", "")
    return table


_TABLE = _build_table()
_MAX_KEY = max(map(len, _TABLE))


def tokenize(word: str) -> list[Token]:
    """Split a lowercase Arabizi word with greedy longest-match ("sh" beats "s"+"h")."""
    tokens: list[Token] = []
    i = 0
    while i < len(word):
        for size in range(min(_MAX_KEY, len(word) - i), 0, -1):
            token = _TABLE.get(word[i:i + size])
            if token is not None:
                tokens.append(token)
                i += size
                break
        else:
            i += 1  # unknown character, e.g. a stray apostrophe
    return tokens


def _collapse_doubles(tokens: list[Token]) -> list[Token]:
    """Casual Arabic skips the shadda, so "kwayyes" keeps a single ي."""
    collapsed: list[Token] = []
    for token in tokens:
        if token.kind == "C" and collapsed and collapsed[-1] == token:
            continue
        collapsed.append(token)
    return collapsed


def _hamza(tokens: list[Token], idx: int) -> str:
    """Pick a hamza seat for the digit 2 from its position and vowels."""
    value = tokens[idx].value
    if idx == 0:
        return _INITIAL_HAMZA[value]
    if value:
        return _MEDIAL_HAMZA[value]
    previous = tokens[idx - 1]
    if idx == len(tokens) - 1 or previous.kind != "V" or previous.value not in SHORT_VOWELS:
        return "ء"
    return _MEDIAL_HAMZA[previous.value]


def _vowel(tokens: list[Token], idx: int, *, taa_marbuta: bool, final_h: bool) -> str:
    """Resolve a vowel by position: initial -> ا, medial short -> dropped, final -> letter."""
    value = tokens[idx].value
    last = idx == len(tokens) - 1
    if last and idx > 0 and value == "a":
        consonants = sum(token.kind != "V" for token in tokens[:idx])
        if taa_marbuta and consonants >= 2:
            return "ة"
        return "ه" if final_h else "ا"
    if idx == 0:
        initial = "ا" if value in SHORT_VOWELS or value == "aa" else "ا" + LONG_VOWELS[value]
        return initial + ("ه" if last and final_h else "")
    if last:
        return _FINAL_VOWEL[value]
    if value == "a" and idx + 2 < len(tokens) and tokens[idx + 1] == _YAA and tokens[idx + 2].kind != "V":
        return "ا"  # active participles: "3ayz" -> عايز
    if value == "i":
        return "ي"  # in Egyptian texting "i" nearly always marks a long ي
    return LONG_VOWELS.get(value, "")


def _resolve(tokens: list[Token], *, taa_marbuta: bool, final_h: bool = False) -> str:
    """Turn a token list into Arabic letters using the context rules."""
    parts: list[str] = []
    for idx, token in enumerate(tokens):
        if token.kind == "C":
            parts.append(token.value)
        elif token.kind == "H":
            parts.append(_hamza(tokens, idx))
        else:
            parts.append(_vowel(tokens, idx, taa_marbuta=taa_marbuta, final_h=final_h))
    return "".join(parts)


def _apply_rules(word: str, *, taa_marbuta: bool, tanween: bool) -> str:
    """Transliterate one lowercase word with the rules only (no lexicon, no prefix)."""
    tokens = _collapse_doubles(tokenize(word))
    ends_an = len(tokens) >= 3 and tokens[-2] == Token("V", "a") and tokens[-1] == Token("C", "ن")
    if tanween and ends_an and tokens[-3].kind != "V":
        stem = _resolve(tokens[:-2], taa_marbuta=taa_marbuta)
        if len(stem) >= 3:
            return stem + "ا"  # "shukran" -> شكرا (tanween fath is written as a plain alef)
    final_h = len(tokens) >= 2 and tokens[-1] == _HAA and tokens[-2] == Token("V", "a")
    if final_h:
        tokens = tokens[:-1]
    return _resolve(tokens, taa_marbuta=taa_marbuta, final_h=final_h)


def transliterate_word(
    word: str, *, taa_marbuta: bool = True, tanween: bool = True, lexicon: bool = True
) -> str:
    """Transliterate a single Arabizi word. Pure numbers are returned unchanged."""
    lowered = word.lower()
    if not any(ch.isalpha() for ch in lowered):
        return word
    if lexicon and lowered in LEXICON:
        return LEXICON[lowered]
    if lowered[:2] in ("el", "al") and len(lowered) >= 5:
        return "ال" + _apply_rules(lowered[2:], taa_marbuta=taa_marbuta, tanween=tanween)
    return _apply_rules(lowered, taa_marbuta=taa_marbuta, tanween=tanween)


def transliterate(
    text: str,
    *,
    taa_marbuta: bool = True,
    tanween: bool = True,
    lexicon: bool = True,
    arabic_punctuation: bool = True,
) -> str:
    """Transliterate a whole Arabizi sentence, keeping spacing and non-Latin text as is.

    taa_marbuta: final "a"/"ah" after 2+ consonants becomes ة ("7elwa" -> حلوة).
    tanween: final "an" after a 3+ letter stem becomes ا ("3afwan" -> عفوا).
    lexicon: look up a short list of very common Egyptian words first.
    arabic_punctuation: ? , ; become ؟ ، ؛
    """
    pieces = _WORD_SPLIT.split(text)  # odd indices are words, even ones separators
    out: list[str] = []
    i = 0
    while i < len(pieces):
        piece = pieces[i]
        if i % 2 == 0:
            out.append(piece.translate(PUNCTUATION) if arabic_punctuation else piece)
            i += 1
            continue
        prefix = PREFIX_WORDS.get(piece.lower())
        joins_next = (
            prefix is not None
            and i + 2 < len(pieces)
            and _SPACES.fullmatch(pieces[i + 1]) is not None
            and any(ch.isalpha() for ch in pieces[i + 2])
        )
        if joins_next:
            out.append(prefix)
            i += 2  # skip the space so the prefix sticks to the next word
            continue
        out.append(transliterate_word(piece, taa_marbuta=taa_marbuta, tanween=tanween, lexicon=lexicon))
        i += 1
    return "".join(out)
