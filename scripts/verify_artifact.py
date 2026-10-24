"""Install a wheel or sdist in a clean venv and test without the source tree on sys.path."""
import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SMOKE = r'''
from io import StringIO
from pathlib import Path
import os
import dotenv_rs
from dotenv_rs import _core, dotenv_values, load_dotenv
assert not str(Path(dotenv_rs.__file__).resolve()).startswith(str(Path.cwd().resolve()))
assert any(str(_core.__file__).endswith(suffix) for suffix in (".so", ".pyd"))
assert dotenv_values(stream=StringIO('\ufeffA="héllo 🌎"\nB=${A}\nC= # comment')) == {
    "A": "héllo 🌎", "B": "héllo 🌎", "C": ""}
os.environ.pop("PYTHON_DOTENV_DISABLED", None)
os.environ["DOTENV_RS_ARTIFACT"] = "environment"
assert load_dotenv(stream=StringIO("DOTENV_RS_ARTIFACT=file"))
assert os.environ["DOTENV_RS_ARTIFACT"] == "environment"
assert load_dotenv(stream=StringIO("DOTENV_RS_ARTIFACT=file"), override=True)
assert os.environ["DOTENV_RS_ARTIFACT"] == "file"
assert Path(dotenv_rs.__file__).with_name("py.typed").is_file()
assert Path(dotenv_rs.__file__).with_name("_core.pyi").is_file()
print("Clean installation passed:", dotenv_rs.__file__)
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()
    artifact = args.artifact.resolve()
    with tempfile.TemporaryDirectory(prefix="dotenv-install-") as directory:
        root = Path(directory)
        subprocess.run(["uv", "venv", "--python", sys.executable, str(root / "venv")], check=True)
        python = root / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        subprocess.run(["uv", "pip", "install", "--python", str(python), "--no-deps", str(artifact)], check=True)
        subprocess.run([str(python), "-I", "-c", SMOKE], check=True)


if __name__ == "__main__":
    main()
