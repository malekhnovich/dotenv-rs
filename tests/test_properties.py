"""Generated differential checks against the pinned reference implementation."""
from io import StringIO
from unittest.mock import patch

from dotenv import dotenv_values as reference
from dotenv.parser import parse_stream
from dotenv_rs import dotenv_values
from dotenv_rs._core import parse_with_errors
from hypothesis import given, settings
from hypothesis import strategies as st

# Include arbitrary Unicode scalar values and characters likely to affect syntax.
CHAR = st.one_of(st.sampled_from(list("A='\"# \n\r\t${}:-\\")),
                 st.characters(blacklist_categories=("Cs",)))
RAW = st.text(CHAR, max_size=300)
KEY = st.text(alphabet="ABC_xyz012é", min_size=1, max_size=12)
VALUE = st.text(alphabet="abc XYZ012#${}:-é🌎\\", max_size=40)
LINE = st.builds(lambda key, value, quote: f"{key}={quote}{value}{quote}",
                 KEY, VALUE, st.sampled_from(["", "'", '"']))
DOCUMENT = st.one_of(RAW, st.builds(lambda lines, ending: ending.join(lines), st.lists(LINE, max_size=20),
                                        st.sampled_from(["\n", "\r", "\r\n"])))


@settings(max_examples=2000, deadline=None, derandomize=True)
@given(DOCUMENT)
def test_parser_matches_reference(text):
    bindings = list(parse_stream(StringIO(text)))
    expected = [(b.key, b.value) for b in bindings if b.key is not None]
    errors = [b.original.line for b in bindings if b.error]
    assert parse_with_errors(text) == (expected, errors)


@settings(max_examples=500, deadline=None, derandomize=True)
@given(DOCUMENT, st.booleans())
def test_values_match_reference(text, interpolate):
    with patch.dict("os.environ", {"A": "env", "B": "", "xyz": "value"}, clear=True):
        assert dotenv_values(stream=StringIO(text), interpolate=interpolate) == reference(
            stream=StringIO(text), interpolate=interpolate)


@settings(max_examples=500, deadline=None, derandomize=True)
@given(DOCUMENT, st.booleans(), st.booleans())
def test_load_effects_and_exceptions_match_reference(text, override, interpolate):
    import os

    from dotenv import load_dotenv as reference_load
    from dotenv_rs import load_dotenv

    results = []
    for function in (reference_load, load_dotenv):
        with patch.dict(os.environ, {"A": "existing", "B": ""}, clear=True):
            try:
                outcome = ("returned", function(stream=StringIO(text), override=override,
                                                interpolate=interpolate))
            except (ValueError, OSError) as error:
                outcome = (type(error).__name__, str(error))
            results.append((outcome, dict(os.environ)))
    assert results[0] == results[1]
