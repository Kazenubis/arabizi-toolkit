"""Command-line interface: python -m arabizi {normalize,digits,translit,detect} ..."""

from __future__ import annotations

import argparse
import sys
from typing import TextIO

from .arabizi import transliterate
from .detect import arabizi_words, is_arabizi, script_ratio
from .digits import SYSTEMS, convert_digits
from .normalize import normalize


def use_utf8_streams() -> None:
    """Windows consoles default to a legacy code page; switch the std streams to UTF-8."""
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8")
        except (ValueError, OSError):
            continue


def read_text(words: list[str], stdin: TextIO) -> str:
    """Join the positional words, or read stdin when none were given."""
    if words:
        return " ".join(words)
    return stdin.read().rstrip("\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="arabizi", description="Clean Arabic text and convert Egyptian Arabizi.")
    sub = parser.add_subparsers(dest="command", required=True)

    norm = sub.add_parser("normalize", help="strip tashkeel/tatweel and unify letter variants")
    norm.add_argument("--keep-tashkeel", action="store_true", help="keep harakat, shadda, sukun")
    norm.add_argument("--keep-tatweel", action="store_true", help="keep the ـ stretching character")
    norm.add_argument("--no-alef", action="store_true", help="keep أ إ آ ٱ as they are")
    norm.add_argument("--no-yaa", action="store_true", help="keep ى as it is")
    norm.add_argument("--taa-marbuta", action="store_true", help="also map ة to ه")
    norm.add_argument("--keep-whitespace", action="store_true", help="do not collapse whitespace")

    digits = sub.add_parser("digits", help="convert between digit systems")
    digits.add_argument("--to", choices=sorted(SYSTEMS), default="western", help="target system (default: western)")

    translit = sub.add_parser("translit", help="Egyptian Arabizi -> Arabic script")
    translit.add_argument("--no-taa-marbuta", action="store_true", help="final 'a' stays ا instead of ة")
    translit.add_argument("--no-tanween", action="store_true", help="final 'an' stays ن instead of ا")
    translit.add_argument("--no-lexicon", action="store_true", help="rules only, skip the common-word list")

    sub.add_parser("detect", help="show script ratio and whether the text looks like Arabizi")

    for subparser in sub.choices.values():
        subparser.add_argument("text", nargs="*", help="text to process (reads stdin if omitted)")
    return parser


def run(args: argparse.Namespace, text: str) -> str:
    """Execute one parsed command and return what should be printed."""
    if args.command == "normalize":
        return normalize(
            text,
            tashkeel=not args.keep_tashkeel,
            tatweel=not args.keep_tatweel,
            alef=not args.no_alef,
            yaa=not args.no_yaa,
            taa_marbuta=args.taa_marbuta,
            whitespace=not args.keep_whitespace,
        )
    if args.command == "digits":
        return convert_digits(text, args.to)
    if args.command == "translit":
        return transliterate(
            text,
            taa_marbuta=not args.no_taa_marbuta,
            tanween=not args.no_tanween,
            lexicon=not args.no_lexicon,
        )
    ratio = script_ratio(text)
    verdict = f"yes ({', '.join(arabizi_words(text))})" if is_arabizi(text) else "no"
    return f"arabic: {ratio.arabic:.2f}\nlatin:  {ratio.latin:.2f}\narabizi: {verdict}"


def main(argv: list[str] | None = None) -> int:
    use_utf8_streams()
    args = build_parser().parse_args(argv)
    print(run(args, read_text(args.text, sys.stdin)))
    return 0
