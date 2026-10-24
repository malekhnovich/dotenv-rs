# Releasing dotenv-rs

The first release is **0.1.0a1**. Do not describe it as a complete drop-in replacement.
See COMPATIBILITY.md for supported APIs and known differences.

## One-time account setup

Create PyPI and TestPyPI accounts and enable two-factor authentication.
For a new project, add a pending publisher at:

- https://pypi.org/manage/account/publishing/
- https://test.pypi.org/manage/account/publishing/

Use these exact fields on both services:

| Field | Value |
| --- | --- |
| PyPI project name | `dotenv-rs` |
| Owner | `malekhnovich` |
| Repository | `dotenv-rs` |
| Workflow filename | `release.yml` |
| Environment | `pypi` on PyPI; `testpypi` on TestPyPI |

A 404 on the PyPI project endpoint is not a guarantee that a name can be registered.
Pending publishers do not reserve names. If PyPI rejects the name, choose a new
one and update pyproject.toml, the lockfile, and publisher configuration together.

Create matching GitHub environments (`pypi`, `testpypi`) under repository settings.
Set required reviewers for the production environment if available for this repo.
Trusted Publishing uses short-lived OIDC credentials, not a committed API token.

Official guide: https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/

## Release procedure

1. Wait for CI and Portable wheels to pass on the exact commit.
2. Verify `pyproject.toml` and Cargo.toml versions agree (PEP 440 vs SemVer spellings).
3. Build/install the release extension and regenerate README benchmarks if code changed:

   ```sh
   uv sync --locked
   uv run maturin develop --release
   uv run python benchmarks/compare.py --update-readme
   uv run pytest
   ```

4. Commit results and tag the reviewed commit:

   ```sh
   git tag v0.1.0a1
   git push origin v0.1.0a1
   ```

5. Run `Release` from the **tag** with `index=testpypi`:

   ```sh
   gh workflow run release.yml --ref v0.1.0a1 -f index=testpypi
   ```

6. Confirm TestPyPI artifacts install without a Rust compiler on supported platforms:

   ```sh
   uv venv /tmp/dotenv-release-check
   uv pip install --python /tmp/dotenv-release-check/bin/python --index-url https://test.pypi.org/simple/ --only-binary=:all: dotenv-rs==0.1.0a1
   /tmp/dotenv-release-check/bin/python -c 'from dotenv_rs import dotenv_values; print(dotenv_values)'
   ```

   On Windows use an appropriate temporary path and `Scripts/python.exe`.

7. Run the same tag with `index=pypi`, then verify a clean installation from PyPI.
   Create a GitHub release describing supported behavior and known gaps.

The workflow requires a tag matching the Python version, reruns the compatibility
suite, builds portable wheels, installs each wheel in a clean environment, and
checks metadata before uploading. Initial wheel targets: Linux x86-64/ARM64,
macOS Intel/Apple Silicon, Windows x86-64. Source builds require Rust.
PyPI versions cannot be overwritten; fixes need a new version.
