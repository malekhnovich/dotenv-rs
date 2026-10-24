import logging
from io import StringIO

import pytest
from dotenv import dotenv_values as reference
from dotenv_rs import dotenv_values, load_dotenv


@pytest.mark.parametrize("path", ["missing.env", "", "."])
def test_missing_path_stream_fallback(path, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert dotenv_values(path, stream=StringIO("A=stream")) == reference(path, stream=StringIO("A=stream"))


@pytest.mark.parametrize("encoding", ["utf-8", "utf-8-sig", "utf-16", "latin-1"])
def test_encoding(tmp_path, encoding):
    path = tmp_path / ".env"
    path.write_text("A=héllo\nB=${A}", encoding=encoding)
    assert dotenv_values(path, encoding=encoding) == reference(path, encoding=encoding)


def test_decode_error_matches(tmp_path):
    path = tmp_path / ".env"
    path.write_bytes(b"A=\xff")
    for function in (reference, dotenv_values):
        with pytest.raises(UnicodeDecodeError):
            function(path)


@pytest.mark.parametrize("text", ["bad line\r\nbad line\r\nbad line\r\n", "bad line\nOK=yes", '\n\nA="valid\nquote" junk\nB=yes', "A='unterminated\rOK=yes\r"])
def test_invalid_line_logs_match(text, caplog):
    results = []
    for function in (reference, dotenv_values):
        caplog.clear()
        with caplog.at_level(logging.WARNING):
            function(stream=StringIO(text))
        results.append([(r.levelno, r.getMessage()) for r in caplog.records])
    assert results[0] == results[1]


def test_missing_file_logs_match(tmp_path, caplog):
    results = []
    for function in (reference, dotenv_values):
        caplog.clear()
        with caplog.at_level(logging.INFO):
            function(tmp_path / "missing", verbose=True)
        results.append([(r.levelno, r.getMessage()) for r in caplog.records])
    assert results[0] == results[1]


@pytest.mark.parametrize("flag", ["1", "true", "TRUE", "t", "yes", "y", "0", "false", " true ", ""])
def test_disabled_flags_match(flag, monkeypatch):
    from unittest.mock import patch

    from dotenv import load_dotenv as reference_load

    results = []
    for function in (reference_load, load_dotenv):
        with patch.dict("os.environ", {"PYTHON_DOTENV_DISABLED": flag}, clear=True):
            import os
            result = function(stream=StringIO("DOTENV_RS_FLAG=yes"))
            results.append((result, dict(os.environ)))
    assert results[0] == results[1]


@pytest.mark.parametrize("env_key", ["dotenv_rs_case", "DOTENV_RS_CASE"])
@pytest.mark.parametrize("lookup", ["dotenv_rs_case", "DOTENV_RS_CASE"])
def test_environment_name_case_matches_reference(env_key, lookup):
    from unittest.mock import patch

    # Exercise the native environment on Windows too: do not assume POSIX casing.
    with patch.dict("os.environ", {env_key: "environment"}, clear=True):
        text = f"VALUE=${{{lookup}:-fallback}}"
        assert dotenv_values(stream=StringIO(text)) == reference(stream=StringIO(text))
