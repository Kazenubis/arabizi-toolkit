# Arabizi Toolkit

A stdlib-only Python library and CLI for cleaning Arabic text and turning Egyptian Franco-Arabic ("3ayz", "7abibi") into Arabic script.

## Why I built this

I'm from Egypt, and almost every chat I'm in is written in Franco: "ana 3ayz", "ma3lesh", "6ab3an". It works fine between people, but it's awkward for search, for pasting into anything that expects Arabic, or for comparing it with text written in Arabic script. I wanted to see how far a small set of honest rules could get, and pair it with the normalization steps I kept rewriting whenever I touched Arabic text.

## Features

- `normalize`: strip tashkeel (harakat, tanween, shadda, sukun, superscript alef), remove tatweel (ـ), map أ إ آ ٱ to ا, optionally map ى to ي and ة to ه, collapse whitespace. Each step is its own function, and `normalize()` wraps them behind keyword flags.
- `digits`: convert between Western (0-9), Eastern Arabic (٠-٩) and Persian (۰-۹) digits.
- `translit`: rule-based Egyptian Arabizi to Arabic script, using a longest-match tokenizer (digit letters like 3/7/5/2, `3'` for غ, digraphs sh/kh/gh/th/dh, long vowels, the `el`/`al` prefix, ta marbuta and tanween heuristics, and a short list of very common words).
- `detect`: Arabic vs Latin letter ratio, plus an `is_arabizi()` heuristic that looks for 2/3/5/7 inside Latin words and ignores things like `7pm`, `3rd` and `mp3`.
- CLI reads from arguments or stdin and switches stdout to UTF-8, so Arabic prints correctly in the Windows console.

### Transliteration is a heuristic

Arabizi leaves out a lot of what Arabic script needs, so the output is a best guess, and it's always the same guess for the same input. The rules:

| Arabizi | Arabic | Notes |
| --- | --- | --- |
| `2` | ء / أ / إ / ئ / ؤ | seat chosen from the position and the nearby vowel |
| `3` `3'` | ع غ | `'` after a digit adds the dot (also `7'` خ, `6'` ظ, `9'` ض) |
| `5` `6` `7` `9` | خ ط ح ص | |
| `8` | ق | Gulf/Levantine habit. In Egypt people usually write `2` or `q` for ق, so 8 is rare |
| `sh kh gh th dh` | ش خ غ ث ذ | longest match wins, so `sh` never becomes س + ه |
| `aa ee/ii oo/ou` | ا ي و | long vowels |
| `a e o u` in the middle of a word | dropped | short vowels. `i` in the middle becomes ي, since Egyptians mostly use it for a long vowel |
| a vowel at the start | ا | |
| `el`/`al` + word | ال | as a separate word (`el beet`) or joined (`elbeet`) |
| `w` + word | و | `ahlan w sahlan` → اهلا وسهلا |
| final `a`/`ah` | ة | only after 2+ consonants (`7elwa` → حلوة, but `ana` → انا). Can be turned off |
| final `an` | ا | tanween, only after a 3+ letter stem (`shukran` → شكرا, `zaman` → زمن). Can be turned off |

What it gets right:

```
7abibi → حبيبي     shukran → شكرا     ma3lesh → معلش     kwayyes → كويس
3ayza  → عايزة     saa3a   → ساعة     mas2ala → مسألة    3'areeb → غريب
```

Known limitations:

- In Cairo, `2` usually stands for ق, which is pronounced as a glottal stop. The rules can't tell the two apart, so `el 2ahwa` comes out as `الأهوة` and not `القهوة`.
- `s` is always س and `t` is always ت. `a5ls` gives `اخلس`, not `اخلص`. Writing `9` or `6` fixes it.
- A short `a` inside a word is dropped even when the Arabic word has an alef: `sa3a` gives `سعة`. Writing `saa3a` gives `ساعة`.
- English words get transliterated letter by letter: `project` becomes `برجكت`.
- The ta marbuta rule fires on any word ending in `-a`, so the suffix `-na` ("us/our") also gets ة: `bina` gives `بينة` instead of `بينا`.

## Run it

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m arabizi translit "ana 3ayz a5ls el project"
```

More examples (real output):

```
> python -m arabizi translit "ana 3ayz a5ls el project"
أنا عايز اخلس البرجكت

> python -m arabizi translit "ahlan w sahlan, ezayak ya 7abibi?"
اهلا وسهلا، ازيك يا حبيبي؟

> python -m arabizi normalize "  أَهْلًا   وَسَهْلًا يا مُصْطَفَى، إزيّك؟  "
اهلا وسهلا يا مصطفي، ازيك؟

> python -m arabizi digits --to western "السنة ٢٠٢٦ والرقم ۱۴۰۵"
السنة 2026 والرقم 1405

> python -m arabizi detect "ana 3ayz a5ls el project"
arabic: 0.00
latin:  1.00
arabizi: yes (3ayz, a5ls)

> echo yalla nemshi ya 7abibi | python -m arabizi translit
يلا نمشي يا حبيبي
```

Useful flags: `translit --no-lexicon --no-taa-marbuta --no-tanween`, `normalize --taa-marbuta --no-yaa --keep-tashkeel`, `digits --to western|eastern|persian`. Run `python -m arabizi <command> -h` for the full list.

As a library:

```python
from arabizi import normalize, to_western, transliterate, is_arabizi

normalize("مُسْتَشْفَى", yaa=True)   # 'مستشفي'
to_western("٢٠٢٦")                   # '2026'
transliterate("3afwan ya 7abibi")    # 'عفوا يا حبيبي'
is_arabizi("meet me at 7pm")         # False
```

## Run the tests

```
python -m pytest -q
```

## Project structure

```
arabizi-toolkit/
├── arabizi/
│   ├── __init__.py
│   ├── __main__.py     # python -m arabizi
│   ├── cli.py          # argparse subcommands, stdin, UTF-8 streams
│   ├── normalize.py    # tashkeel, tatweel, alef/yaa/taa marbuta, whitespace
│   ├── digits.py       # Western / Eastern Arabic / Persian digits
│   ├── arabizi.py      # tokenizer + transliteration rules
│   └── detect.py       # script ratio and Arabizi detection
├── tests/
├── conftest.py
├── requirements.txt
└── LICENSE
```

## What I practiced

- A greedy longest-match tokenizer, then a second pass where context rules (word position, neighbouring tokens, consonant count) pick the output letter.
- Working with Unicode directly: code point ranges, `str.translate` tables, NFC composition for decomposed alef madda, and telling letters apart from combining marks.
- Writing a heuristic, being clear about where it breaks, and pinning its exact behaviour with tests, including the known wrong outputs.
- An `argparse` CLI with subcommands that reads stdin and reconfigures stdout to UTF-8 for the Windows console.
