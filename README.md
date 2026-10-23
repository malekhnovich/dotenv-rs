# dotenv-rs

A Python dotenv package with a Rust parser, PyO3 bindings, and maturin packaging.
Early alpha: the distribution name is provisional and this package is not yet published.

```python
from dotenv_rs import dotenv_values, load_dotenv

load_dotenv(".env")
config = dotenv_values(".env")
```

The Rust core parses quoted and unquoted values, export directives, comments,
multiline quoted values, escapes, and keys without values. Python handles file
I/O, `${NAME}` / `${NAME:-default}` expansion, and environment updates.
It has no Python runtime dependencies.

## Development

Requires Rust 1.86+, Python 3.9+, and uv.

```sh
uv sync
uv run pytest
cargo test
cargo fmt --check
cargo clippy --all-targets -- -D warnings
uv run python benchmarks/compare.py
uv run maturin build --release --out dist
uv run maturin sdist --out dist
```

## Compatibility

Inspired by python-dotenv; this is an independent implementation. Import using
`dotenv_rs`, leaving the upstream `dotenv` namespace available for comparisons.
Differential tests compare supported behavior against python-dotenv.
Full drop-in compatibility is a goal, not a current guarantee. Discovery starts
at cwd rather than the caller's script. Invalid lines are skipped silently.
File editing helpers, IPython integration, and the upstream CLI are not implemented.
No speedup is claimed until reproducible benchmarks establish one.

## Publishing

Before a first release: select an available PyPI name, update package metadata,
expand compatibility coverage, and test wheels on Linux, macOS, and Windows.
Build a wheel and source distribution with the commands above. Configure PyPI
Trusted Publishing for the GitHub repository and a protected release environment
before adding an automated upload job. Never commit PyPI tokens or dotenv secrets.

## Portfolio

An accurate description of the current project: “Built a Python dotenv package
with a Rust parser, PyO3 bindings, maturin packaging, and differential tests.”
Add publication and measured performance results only once achieved.

## License

MIT. See LICENSE.
