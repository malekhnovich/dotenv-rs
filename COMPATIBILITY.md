# Compatibility contract

Reference: python-dotenv **1.2.4**. A passing suite is evidence for the tested
behavior, not proof that every possible input or integration is equivalent.

## Supported surface

- `dotenv_values`: files, text streams, file precedence and stream fallback,
  encoding, interpolation defaults, duplicate keys, and absent values.
- `load_dotenv`: the above plus environment precedence, return values, and
  `PYTHON_DOTENV_DISABLED`.
- `find_dotenv`: caller discovery, cwd mode, interactive/debugger mode, parent
  traversal, and missing-file errors. Regular files and POSIX FIFOs are accepted.
- Parser: export, quoted keys/values, escapes, multiline input, BOM, line endings,
  Unicode, invalid-line recovery, and diagnostic line numbers.

## Known differences

- Package import is `dotenv_rs`, not `dotenv`.
- Public mappings are `dict`, not `collections.OrderedDict`; insertion order is preserved.
- Logs use the `dotenv_rs` logger; message text and levels follow the reference.
- Internal classes/token APIs, file editing helpers, CLI, and IPython are out of scope.
- CPython 3.10+ with the standard GIL is the initial target; PyPy and free-threaded
  CPython are not supported or advertised.
- Text input must contain Unicode scalar values; Python strings containing unpaired
  surrogates cannot cross the Rust UTF-8 boundary and raise UnicodeEncodeError.
- Performance characteristics and Python/Rust allocation behavior differ.

## Release gates

1. Pinned upstream parser/value fixtures pass, with no xfail or ignored differences.
2. Generated parser and value comparisons pass (3,000 examples per suite).
3. Environment effects, diagnostic messages, file fallback, encodings, and script discovery pass.
4. Linux, macOS, Windows and supported Python CI tests pass.
5. Release wheels install in clean environments and load the native extension.
6. A source distribution rebuilds successfully; metadata checks pass.
7. Benchmark outputs equal the reference; published timings include raw samples and methodology.

Every discovered mismatch gets a focused regression test before a fix. Update
the pinned reference and fixtures together when intentionally targeting a newer
python-dotenv release. Do not equate a growing test count with complete parity.
