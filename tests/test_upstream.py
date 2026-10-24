"""Pinned upstream cases; original inputs and expected outputs are vendored as data."""
import json
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest
from dotenv_rs import dotenv_values
from dotenv_rs._core import parse_with_errors

FIXTURES = Path(__file__).parent / "upstream"


@pytest.mark.parametrize("case", json.loads((FIXTURES / "parser.json").read_text(encoding="utf-8")))
def test_upstream_parser(case):
    entries, errors = parse_with_errors(case["text"])
    assert [list(entry) for entry in entries] == case["entries"]
    assert errors == case["errors"]


@pytest.mark.parametrize("case", json.loads((FIXTURES / "values.json").read_text(encoding="utf-8")))
def test_upstream_values(case):
    with patch.dict("os.environ", case["env"], clear=True):
        assert dotenv_values(stream=StringIO(case["text"]), interpolate=case["interpolate"]) == case["expected"]
