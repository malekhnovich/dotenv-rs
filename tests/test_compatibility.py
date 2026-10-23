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
    assert find_dotenv() == str(tmp_path / ".env")
    assert dotenv_values() == {"A": "one"}


def test_no_interpolation():
    assert dotenv_values(stream=StringIO("A=${B}"), interpolate=False) == {"A": "${B}"}
