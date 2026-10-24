# Launch copy

These drafts describe the published 0.1.0a1 alpha. Update version numbers and
measured results when announcing a later release.

## LinkedIn or a project showcase

I published dotenv-rs: a Python dotenv package with a Rust parser, built using
PyO3 and maturin.

The Python API stays familiar:

```python
from dotenv_rs import dotenv_values, load_dotenv

load_dotenv(".env")
config = dotenv_values(".env")
```

The first alpha supports `load_dotenv`, `dotenv_values`, and `find_dotenv`. It
ships wheels for Linux x86-64/ARM64, macOS Intel/Apple Silicon, and Windows x86-64.

I focused on checking behavior against python-dotenv 1.2.4: upstream fixtures,
219 tests, and 3,000 generated differential comparisons, with CI across CPython
3.10–3.14 on Linux, macOS, and Windows.

Synthetic in-memory loading benchmarks measured 9.9–52.6× speedups on an Apple
M4 Pro. The README includes the workload sizes, timings, methodology, and raw
samples. These results exclude file I/O and application startup.

It's an alpha, not a complete drop-in replacement. File-editing helpers, the
CLI, and IPython integration aren't implemented yet. I'd appreciate installation
reports and small examples where the supported APIs behave differently.

Try it: `pip install dotenv-rs==0.1.0a1`

GitHub: https://github.com/malekhnovich/dotenv-rs
PyPI: https://pypi.org/project/dotenv-rs/0.1.0a1/
Demo: https://github.com/malekhnovich/dotenv-rs/tree/main/examples
Feedback: https://github.com/malekhnovich/dotenv-rs/issues/new/choose

## Short post

I released dotenv-rs, a Rust-backed Python dotenv package using PyO3 and maturin.
The alpha supports the core loading APIs, with cross-platform wheels and
compatibility tests against python-dotenv. Looking for installation feedback and
behavior differences. Try `pip install dotenv-rs==0.1.0a1`.

https://github.com/malekhnovich/dotenv-rs

## Resume bullet

Published a Rust-backed Python dotenv package to PyPI using PyO3 and maturin;
shipped wheels for five platforms and automated compatibility checks across
15 operating-system/Python combinations.

If adding performance numbers, qualify them: “Measured 9.9–52.6× faster in-memory
loading on synthetic workloads,” with a link to the benchmark methodology.
