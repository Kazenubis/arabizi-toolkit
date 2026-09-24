import io

import pytest

from arabizi.cli import main


def test_translit_command(capsys):
    assert main(["translit", "ana", "3ayz", "a5ls", "el", "project"]) == 0
    assert capsys.readouterr().out == "أنا عايز اخلس البرجكت\n"


def test_digits_command(capsys):
    main(["digits", "--to", "eastern", "Flat 12"])
    assert capsys.readouterr().out == "Flat ١٢\n"


def test_normalize_reads_stdin(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("أَهْلًا   بِيك\n"))
    main(["normalize"])
    assert capsys.readouterr().out == "اهلا بيك\n"


def test_detect_command(capsys):
    main(["detect", "ana 3ayz a5ls"])
    out = capsys.readouterr().out
    assert "latin:  1.00" in out
    assert "arabizi: yes (3ayz, a5ls)" in out


def test_unknown_digit_system_is_rejected():
    with pytest.raises(SystemExit):
        main(["digits", "--to", "roman", "12"])
