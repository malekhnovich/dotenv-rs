"""Rust parsing with Python environment and filesystem integration."""
from __future__ import annotations

import logging
import os
import re
import sys
from collections import ChainMap
from pathlib import Path
from typing import IO

from ._core import parse_with_errors

__all__ = ["dotenv_values", "find_dotenv", "load_dotenv"]
_LOGGER = logging.getLogger(__name__)
_VARIABLE = re.compile(r"\$\{([^}:]*)(?::-([^}]*))?\}")


def _interactive() -> bool:
    if hasattr(sys, "ps1") or hasattr(sys, "ps2"):
        return True
    try:
        main = __import__("__main__", fromlist=["__file__"])
    except ModuleNotFoundError:
        return False
    return not hasattr(main, "__file__")


def _file_or_fifo(path) -> bool:
    candidate = Path(path)
    return candidate.is_file() or candidate.is_fifo()


def find_dotenv(filename: str = ".env", raise_error_if_not_found: bool = False,
                usecwd: bool = False) -> str:
    """Search from the caller's script, or cwd in interactive sessions."""
    if usecwd or _interactive() or sys.gettrace() is not None or getattr(sys, "frozen", False):
        start = Path.cwd()
    else:
        frame = sys._getframe()
        try:
            while frame.f_code.co_filename == __file__ or not os.path.exists(frame.f_code.co_filename):
                if frame.f_back is None:
                    raise AssertionError("No caller frame with a file")
                frame = frame.f_back
            start = Path(os.path.abspath(frame.f_code.co_filename)).parent
        finally:
            del frame
    for directory in (start, *start.parents):
        candidate = directory / filename
        if _file_or_fifo(candidate):
            return str(candidate)
    if raise_error_if_not_found:
        raise OSError("File not found")
    return ""


def _values(dotenv_path, stream, verbose, interpolate, encoding, override):
    if dotenv_path is None and stream is None:
        dotenv_path = find_dotenv()
    if dotenv_path and _file_or_fifo(dotenv_path):
        with open(dotenv_path, encoding=encoding) as source:
            text = source.read()
    elif stream is not None:
        text = stream.read()
    else:
        if verbose:
            _LOGGER.info("python-dotenv could not find configuration file %s.", dotenv_path or ".env")
        return {}
    result: dict[str, str | None] = {}
    environment = dict(os.environ)
    bindings, errors = parse_with_errors(text)
    for line in errors:
        _LOGGER.warning("python-dotenv could not parse statement starting at line %s", line)
    for key, value in bindings:
        if interpolate and value is not None:
            scope = ChainMap(result, environment) if override else ChainMap(environment, result)
            value = _VARIABLE.sub(lambda m, scope=scope: scope.get(m[1], m[2] or "") or "", value)
        result[key] = value
    return result


def dotenv_values(dotenv_path: str | os.PathLike[str] | None = None,
                  stream: IO[str] | None = None, verbose: bool = False,
                  interpolate: bool = True, encoding: str | None = "utf-8") -> dict[str, str | None]:
    """Read dotenv bindings without modifying the environment."""
    return _values(dotenv_path, stream, verbose, interpolate, encoding, True)


def load_dotenv(dotenv_path: str | os.PathLike[str] | None = None,
                stream: IO[str] | None = None, verbose: bool = False,
                override: bool = False, interpolate: bool = True,
                encoding: str | None = "utf-8") -> bool:
    """Load bindings into os.environ; existing variables win by default."""
    if os.environ.get("PYTHON_DOTENV_DISABLED", "").casefold() in {"1", "true", "t", "yes", "y"}:
        _LOGGER.debug("python-dotenv: .env loading disabled by PYTHON_DOTENV_DISABLED environment variable")
        return False
    values = _values(dotenv_path, stream, verbose, interpolate, encoding, override)
    for key, value in values.items():
        if value is not None and (override or key not in os.environ):
            os.environ[key] = value
    return bool(values)
