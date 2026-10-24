# Contributing

Installation reports, compatibility differences, and small reproducible examples
are especially useful while dotenv-rs is in alpha. Start with the
[compatibility contract](COMPATIBILITY.md) and [open an issue](https://github.com/malekhnovich/dotenv-rs/issues/new/choose).
Use synthetic configuration in reports rather than credentials or private URLs.

## Development setup

Requires Rust 1.86+, CPython 3.10+, and uv.

```sh
uv sync --locked
uv run maturin develop --release
uv run pytest
uv run python examples/demo.py
cargo test --locked
cargo fmt --check
cargo clippy --locked --all-targets -- -D warnings
uv run ruff check python tests benchmarks scripts examples
```

Rebuild with `uv run maturin develop --release` after changing Rust code.

## Compatibility fixes

The reference is pinned to python-dotenv 1.2.4. For a mismatch:

1. Reduce the input and environment to a small reproducer.
2. Add a regression test comparing both implementations, including return values,
   exceptions, environment effects, or diagnostics as appropriate.
3. Fix the behavior and run the relevant tests, then the full suite.

Do not change upstream fixture expectations to make a difference disappear.
The fixture README documents the Windows environment adapter; platform-native
comparisons also run on Windows. Keep the upstream license and provenance with
any adapted tests. Broader API additions should start with an issue describing
expected behavior and compatibility requirements.

## Performance changes

Use an optimized extension and the existing benchmark harness:

```sh
uv run maturin develop --release
uv run python benchmarks/compare.py --update-readme
```

Include raw samples and hardware details when sharing results. Check output
equality before comparing speed, and distinguish in-memory loading from file I/O
or application startup. A speed improvement must not weaken compatibility checks.

See [RELEASING.md](RELEASING.md) for the publishing procedure.
