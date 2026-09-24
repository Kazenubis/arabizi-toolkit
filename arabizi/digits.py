"""Convert between Western (0-9), Eastern Arabic (٠-٩) and Persian (۰-۹) digits."""

from __future__ import annotations

WESTERN = "0123456789"
EASTERN = "٠١٢٣٤٥٦٧٨٩"
PERSIAN = "۰۱۲۳۴۵۶۷۸۹"

SYSTEMS: dict[str, str] = {"western": WESTERN, "eastern": EASTERN, "persian": PERSIAN}


def _build_table(target: str) -> dict[int, str]:
    """Translation table mapping every other digit system onto `target`."""
    destination = SYSTEMS[target]
    table: dict[int, str] = {}
    for name, source in SYSTEMS.items():
        if name != target:
            table.update({ord(src): dst for src, dst in zip(source, destination)})
    return table


_TABLES = {name: _build_table(name) for name in SYSTEMS}


def convert_digits(text: str, to: str = "western") -> str:
    """Rewrite every digit in `text` into the `to` system; other characters are untouched."""
    if to not in _TABLES:
        choices = ", ".join(SYSTEMS)
        raise ValueError(f"unknown digit system {to!r} (choose from: {choices})")
    return text.translate(_TABLES[to])


def to_western(text: str) -> str:
    """Eastern Arabic and Persian digits -> 0-9."""
    return convert_digits(text, "western")


def to_eastern(text: str) -> str:
    """Western and Persian digits -> ٠-٩."""
    return convert_digits(text, "eastern")


def to_persian(text: str) -> str:
    """Western and Eastern Arabic digits -> ۰-۹."""
    return convert_digits(text, "persian")
