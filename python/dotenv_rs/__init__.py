"""Rust parsing with Python environment and filesystem integration."""
from __future__ import annotations

import os
import re
import warnings
from pathlib import Path
from typing import IO

from ._core import parse

__all__ = ["dotenv_values", "find_dotenv", "load_dotenv"]
_VARIABLE = re.compile(r"\$\{([^}:]*)(?::-([^}]*))?\}")


def find_dotenv(filename: str = ".env", raise_error_if_not_found: bool = False,
                usecwd: bool = True) -> str:
    """Search cwd and parents. Caller-file discovery is not implemented yet."""
    if not usecwd:
        raise NotImplementedError("Caller-file discovery is not implemented; use usecwd=True")
    start = Path.cwd()
    for directory in (start, *start.parents):
        candidate = directory / filename
        if candidate.is_file():
            return str(candidate)
    if raise_error_if_not_found:
        raise OSError("File not found")
    return ""


def _values(dotenv_path, stream, verbose, interpolate, encoding, override):
    if dotenv_path is None and stream is not None:
        text = stream.read()
    else:
        path = dotenv_path if dotenv_path is not None else find_dotenv()
        if not path or not Path(path).is_file():
            if verbose:
                warnings.warn("dotenv file not found", stacklevel=3)
            return {}
        text = Path(path).read_text(encoding=encoding)
    result: dict[str, str | None] = {}
    environment = dict(os.environ)
    for key, value in parse(text):
        if interpolate and value is not None:
            scope = {**environment, **result} if override else {**result, **environment}
            value = _VARIABLE.sub(lambda m, scope=scope: scope.get(m[1], m[2] or "") or "", value)
        result[key] = value
    return result


def dotenv_values(dotenv_path: str | os.PathLike[str] | None = None,
                  stream: IO[str] | None = None, verbose: bool = False,
                  interpolate: bool = True, encoding: str = "utf-8") -> dict[str, str | None]:
    """Read dotenv bindings without modifying the environment."""
    return _values(dotenv_path, stream, verbose, interpolate, encoding, True)


def load_dotenv(dotenv_path: str | os.PathLike[str] | None = None,
                stream: IO[str] | None = None, verbose: bool = False,
                override: bool = False, interpolate: bool = True,
                encoding: str = "utf-8") -> bool:
    """Load bindings into os.environ; existing variables win by default."""
    if os.environ.get("PYTHON_DOTENV_DISABLED", "").lower() in {"1", "true", "t", "yes", "y"}:
        return False
    values = _values(dotenv_path, stream, verbose, interpolate, encoding, override)
    for key, value in values.items():
        if value is not None and (override or key not in os.environ):
            os.environ[key] = value
    return bool(values)
