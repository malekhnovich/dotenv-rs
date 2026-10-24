"""Demonstrate the published Python API using only synthetic configuration."""
from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv_rs import dotenv_values, load_dotenv


def main() -> None:
    source = Path(__file__).with_name(".env.example")
    print("1. Read configuration without changing the environment")
    config = dotenv_values(source)
    assert config["DOTENV_RS_DEMO_URL"] == "https://example.test/api"
    assert config["DOTENV_RS_DEMO_MESSAGE"] == "Hello from Python.\nParsed by Rust."
    print(json.dumps(config, indent=2, ensure_ascii=False))

    # Keep the output reproducible even when launched from a configured shell.
    saved = {key: os.environ.get(key) for key in (*config, "PYTHON_DOTENV_DISABLED")}
    try:
        os.environ.pop("PYTHON_DOTENV_DISABLED", None)
        os.environ["DOTENV_RS_DEMO_APP"] = "existing-shell-value"
        print("\n2. Preserve an existing environment variable (the default)")
        assert load_dotenv(source)
        assert os.environ["DOTENV_RS_DEMO_APP"] == "existing-shell-value"
        print("DOTENV_RS_DEMO_APP=" + os.environ["DOTENV_RS_DEMO_APP"])

        print("\n3. Explicitly override it with the file value")
        assert load_dotenv(source, override=True)
        assert os.environ["DOTENV_RS_DEMO_APP"] == "dotenv-rs"
        print("DOTENV_RS_DEMO_APP=" + os.environ["DOTENV_RS_DEMO_APP"])
    finally:
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
    print("\nDemo passed.")


if __name__ == "__main__":
    main()
