# A one-minute demo

From a checkout of this repository, install the published alpha and run:

```sh
python -m pip install dotenv-rs==0.1.0a1
python examples/demo.py
```

Or run it in an isolated uv environment without building the Rust source:

```sh
uv run --no-project --with dotenv-rs==0.1.0a1 python examples/demo.py
```

The demo reads the adjacent `.env.example`, containing only synthetic values.
It demonstrates parsing, `${NAME}` interpolation, escaped newlines, and the
choice to preserve or override existing environment variables. Environment
changes are confined to the Python process and restored before the demo exits.
It does not read your own `.env` or print your shell's configuration.

Expected output:

```text
1. Read configuration without changing the environment
{
  "DOTENV_RS_DEMO_APP": "dotenv-rs",
  "DOTENV_RS_DEMO_DOMAIN": "example.test",
  "DOTENV_RS_DEMO_URL": "https://example.test/api",
  "DOTENV_RS_DEMO_MESSAGE": "Hello from Python.\nParsed by Rust."
}

2. Preserve an existing environment variable (the default)
DOTENV_RS_DEMO_APP=existing-shell-value

3. Explicitly override it with the file value
DOTENV_RS_DEMO_APP=dotenv-rs

Demo passed.
```

To record a short terminal demo, show the install command, the sample file, and
`python examples/demo.py`. Finish with the README benchmark table and its
single-machine, in-memory measurement context. The demo itself is not a benchmark.

Found a difference from python-dotenv? [Report it here](https://github.com/malekhnovich/dotenv-rs/issues/new?template=bug_report.yml).
