# dotenv-rs

[![CI](https://github.com/malekhnovich/dotenv-rs/actions/workflows/ci.yml/badge.svg)](https://github.com/malekhnovich/dotenv-rs/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/dotenv-rs?include_prereleases)](https://pypi.org/project/dotenv-rs/)

A Python dotenv package with a Rust parser, PyO3 bindings, and maturin packaging.
An independent implementation of the core `python-dotenv` loading APIs.
[Available on PyPI](https://pypi.org/project/dotenv-rs/0.1.0a1/) as an alpha release.
Requires CPython 3.10+.

```sh
pip install dotenv-rs==0.1.0a1
```

```python
from dotenv_rs import dotenv_values, load_dotenv

load_dotenv(".env")
config = dotenv_values(".env")
```

The Rust core parses quoted and unquoted values, export directives, comments,
multiline quoted values, escapes, and keys without values. Python handles file
I/O, `${NAME}` / `${NAME:-default}` expansion, and environment updates.
It has no Python runtime dependencies.

## Try the demo

The [one-minute demo](examples/README.md) shows interpolation, escaped newlines,
and environment precedence using synthetic values:

```sh
uv run --no-project --with dotenv-rs==0.1.0a1 python examples/demo.py
```

Run this from a checkout of the repo. You can also use the pip installation above
and run `python examples/demo.py`. No Rust compiler is needed on the wheel targets:
Linux x86-64/ARM64, macOS Intel/Apple Silicon, and Windows x86-64.

Moving from python-dotenv? Change `from dotenv import ...` to
`from dotenv_rs import ...` for the three supported loading APIs. Review the
[compatibility limits](COMPATIBILITY.md) before replacing it in an application.

## Benchmarks

<!-- BENCHMARKS:START -->
Measured 2026-10-24 UTC on Apple M4 Pro, macOS-26.2-arm64-arm-64bit-Mach-O, CPython 3.13.2; python-dotenv 1.2.4 and dotenv-rs 0.1.0a1. Rust release build.

| Workload | Bindings | python-dotenv | dotenv-rs | Speedup |
| --- | ---: | ---: | ---: | ---: |
| plain | 10 | 136.5 µs | 11.2 µs | 12.2× |
| plain | 100 | 1,444.1 µs | 42.7 µs | 33.8× |
| plain | 1,000 | 19,157.1 µs | 364.3 µs | 52.6× |
| quoted | 10 | 146.8 µs | 11.7 µs | 12.6× |
| quoted | 100 | 1,506.0 µs | 46.0 µs | 32.8× |
| quoted | 1,000 | 20,107.5 µs | 393.2 µs | 51.1× |
| interpolation | 10 | 145.7 µs | 14.7 µs | 9.9× |
| interpolation | 100 | 1,556.0 µs | 79.3 µs | 19.6× |
| interpolation | 1,000 | 19,415.0 µs | 732.0 µs | 26.5× |
| unicode_multiline | 10 | 148.8 µs | 12.6 µs | 11.8× |
| unicode_multiline | 100 | 1,516.2 µs | 52.6 µs | 28.8× |
| unicode_multiline | 1,000 | 20,078.0 µs | 461.3 µs | 43.5× |
<!-- BENCHMARKS:END -->

Median time per `dotenv_values(stream=StringIO(...))` call, including Python/Rust
conversion and interpolation. Seven repeats per workload; implementation order
is shuffled with a fixed seed. Both implementations receive identical data and
40 synthetic environment variables; outputs are checked for equality first.
File I/O, interpreter startup, and package import are excluded.
These are synthetic single-machine measurements, not guarantees for every `.env`
file or evidence that application startup becomes proportionally faster.

Reproduce (requires Rust):

```sh
uv sync --locked
uv run maturin develop --release
uv run python benchmarks/compare.py --update-readme
```

[Raw timings and environment](benchmarks/results.json) · [Benchmark source](benchmarks/compare.py)

## Development

Requires Rust 1.86+, Python 3.10+, and uv.
After changing Rust code, run `uv run maturin develop --release` to rebuild the extension.

```sh
uv sync
uv run pytest
uv run python examples/demo.py
cargo test
cargo fmt --check
cargo clippy --all-targets -- -D warnings
uv run maturin develop --release
uv run python benchmarks/compare.py --update-readme
uv run maturin build --release --out dist
uv run maturin sdist --out dist
```

## Compatibility

Inspired by python-dotenv; this is an independent implementation. Import using
`dotenv_rs`, leaving the upstream `dotenv` namespace available for comparisons.
Compatibility is checked against **python-dotenv 1.2.4**, pinned in development dependencies:

- All upstream parameterized parser cases and value/interpolation cases are retained
  as fixtures, with their original license and source provenance in [tests/upstream](tests/upstream).
- Hypothesis runs 2,000 parser comparisons and 1,000 public API comparisons per suite,
  including malformed input, Unicode, escapes, and duplicate bindings.
- Tests compare environment precedence, return values, error line numbers, and
  discovery from scripts launched outside their working directory.
- CI checks Linux, macOS, and Windows, plus clean installations of built wheels.

**Scope:** `load_dotenv`, `dotenv_values`, and `find_dotenv`. Import from `dotenv_rs`.
The internal `DotEnv` class, `get_key`/`set_key`/`unset_key`, CLI, and IPython
integration are not implemented. The original `dotenv` namespace stays available.
Returned mappings are ordinary insertion-ordered Python dictionaries rather than
`OrderedDict`. Text containing unpaired Unicode surrogates is unsupported. Diagnostics use the `dotenv_rs` logger, with upstream message text.
This is an alpha, not a claim of complete drop-in compatibility or zero bugs.
See [COMPATIBILITY.md](COMPATIBILITY.md) for the release criteria.

## Publishing

The [release workflow](.github/workflows/release.yml) builds portable wheels,
runs clean-install checks, validates metadata, and uploads through PyPI Trusted
Publishing. [RELEASING.md](RELEASING.md) has the one-time setup and release commands.
Releases remain alpha until the compatibility criteria pass.

## Feedback and contributing

Testing the alpha? [Report a bug or installation problem](https://github.com/malekhnovich/dotenv-rs/issues/new?template=bug_report.yml)
with your package version, Python version, OS/architecture, and a small reproducer.
For compatibility differences, include the result from python-dotenv 1.2.4.
Use synthetic values instead of real secrets.

[Contribution guide](CONTRIBUTING.md) · [Feature requests](https://github.com/malekhnovich/dotenv-rs/issues/new?template=feature_request.yml)

## License

Original code: MIT. Adapted upstream portions: BSD-3-Clause.
See [LICENSE](LICENSE) and [third-party notices](THIRD_PARTY_NOTICES.md).
