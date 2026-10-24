from io import StringIO

import pytest
from dotenv import dotenv_values as reference
from dotenv_rs import dotenv_values, find_dotenv, load_dotenv


@pytest.mark.parametrize("text", [
    "A=one\nB=two\n", "export A = hello # note\n", "A=foo#bar\nB=foo #bar\n",
    "A=\nB\n", "'A'='hello world'\n", 'A="first\nsecond"\n',
    r'A="one\ntwo\tthree"' + "\n", r"A='it\'s fine'" + "\n",
    "A=one\nA=two\nB=${A}\n", "A=${MISSING_DOTENV_RS:-fallback}\n",
    "A=héllo 🌎\n", "# comment\n\nA=yes\r\n", "bad line\nOK=yes\n",
    'A="quoted # value" # comment\n', "A=$UNEXPANDED\n",
    "A=\nB=${A:-fallback}\n", "A\nB=${A:-fallback}\n",
])
def test_matches_reference(text, monkeypatch):
    monkeypatch.delenv("MISSING_DOTENV_RS", raising=False)
    assert dotenv_values(stream=StringIO(text)) == reference(stream=StringIO(text))


def test_load_precedence(monkeypatch):
    monkeypatch.setenv("DOTENV_RS_TEST", "existing")
    monkeypatch.delenv("PYTHON_DOTENV_DISABLED", raising=False)
    assert load_dotenv(stream=StringIO("DOTENV_RS_TEST=new"))
    import os
    assert os.environ["DOTENV_RS_TEST"] == "existing"
    assert load_dotenv(stream=StringIO("DOTENV_RS_TEST=new"), override=True)
    assert os.environ["DOTENV_RS_TEST"] == "new"


def test_disabled(monkeypatch):
    monkeypatch.setenv("PYTHON_DOTENV_DISABLED", "true")
    assert not load_dotenv(stream=StringIO("A=one"))


def test_discovery_and_file(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text("A=one", encoding="utf-8")
    child = tmp_path / "child"
    child.mkdir()
    monkeypatch.chdir(child)
    assert find_dotenv(usecwd=True) == str(tmp_path / ".env")
    assert dotenv_values(find_dotenv(usecwd=True)) == {"A": "one"}


def test_no_interpolation():
    assert dotenv_values(stream=StringIO("A=${B}"), interpolate=False) == {"A": "${B}"}


EDGE_CASES = [
    "bad line\r\nbad line\r\nbad line\r\n",
    "\ufeffA=one\n", "A= # comment\n", "A=#literal\n",
    "''=invalid\nOK=yes\n", "'a b'=value\n", "export\nexported=yes\n",
    "A='unterminated\nOK=yes\n", 'A="unterminated\nOK=yes\n',
    'A="valid" garbage\nOK=yes\n', "A='valid'garbage\nOK=yes\n",
    'A="first\nsecond"\nOK=yes\n', "A='first\rsecond'\rOK=yes\r",
    "bad line\rOK=yes\r", "\v\f\n A = x\n", "A=one\t# comment\n",
    "A='slash\\\\'\nB=yes\n", 'A="slash\\\\"\nB=yes\n',
    r'A="unknown\q and \a\b\f\v"' + "\n",
    r"A='unknown\q and \n'" + "\n",
    "A=${}\nB=${:-default}\n", "A=${NAME-not-default}\n",
    "A=${NAME:-one:two}\n", "A=${NAME:-${OTHER}}\n",
    "A=${FORWARD}\nFORWARD=later\n", "A=one\nA=${A}-two\n",
    "A\nB=${A:-default}\n", "A=\nB=${A:-default}\n",
    "# A=ignored\rB=yes\r", "A=你好\nB=é\n", "A=one\n\ufeffB=two\n",
]


@pytest.mark.parametrize("text", EDGE_CASES)
@pytest.mark.parametrize("interpolate", [True, False])
def test_edge_cases(text, interpolate, monkeypatch):
    for name in ("NAME", "OTHER", "FORWARD", "A"):
        monkeypatch.delenv(name, raising=False)
    assert dotenv_values(stream=StringIO(text), interpolate=interpolate) == reference(
        stream=StringIO(text), interpolate=interpolate)


@pytest.mark.parametrize("override", [True, False])
@pytest.mark.parametrize("text", [
    "DOTENV_RS_X=file\nDOTENV_RS_Y=${DOTENV_RS_X}\n",
    "DOTENV_RS_X\nDOTENV_RS_Y=${DOTENV_RS_X:-fallback}\n",
    "DOTENV_RS_X=\nDOTENV_RS_Y=${DOTENV_RS_X:-fallback}\n",
    "DOTENV_RS_Y=${DOTENV_RS_X}\nDOTENV_RS_X=file\n",
    "", "DOTENV_RS_X\n",
])
def test_load_matches_reference(text, override, monkeypatch):
    import os

    from dotenv import load_dotenv as reference_load

    monkeypatch.delenv("PYTHON_DOTENV_DISABLED", raising=False)
    monkeypatch.setenv("DOTENV_RS_X", "environment")
    monkeypatch.delenv("DOTENV_RS_Y", raising=False)
    expected_return = reference_load(stream=StringIO(text), override=override)
    expected = {key: os.environ.get(key) for key in ("DOTENV_RS_X", "DOTENV_RS_Y")}
    monkeypatch.setenv("DOTENV_RS_X", "environment")
    monkeypatch.delenv("DOTENV_RS_Y", raising=False)
    assert load_dotenv(stream=StringIO(text), override=override) == expected_return
    assert {key: os.environ.get(key) for key in expected} == expected


def test_file_beats_stream(tmp_path):
    path = tmp_path / ".env"
    path.write_text("A=file", encoding="utf-8")
    assert dotenv_values(path, stream=StringIO("A=stream")) == {"A": "file"}


def test_values_does_not_mutate_environment(monkeypatch):
    import os
    monkeypatch.delenv("DOTENV_RS_UNSET", raising=False)
    assert dotenv_values(stream=StringIO("DOTENV_RS_UNSET=yes")) == {"DOTENV_RS_UNSET": "yes"}
    assert "DOTENV_RS_UNSET" not in os.environ
