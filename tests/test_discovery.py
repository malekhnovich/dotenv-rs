import json
import os
import subprocess
import sys

import pytest


@pytest.mark.parametrize("usecwd", [True, False])
@pytest.mark.parametrize("api", ["find_dotenv", "dotenv_values", "load_dotenv"])
def test_script_discovery_matches_reference(tmp_path, usecwd, api):
    script_dir = tmp_path / "scripts"
    cwd = tmp_path / "working"
    script_dir.mkdir()
    cwd.mkdir()
    (script_dir / ".env").write_text("DOTENV_RS_DISCOVERY=script", encoding="utf-8")
    (cwd / ".env").write_text("DOTENV_RS_DISCOVERY=cwd", encoding="utf-8")
    script = script_dir / "check.py"
    script.write_text('''import json, os, sys
module = __import__(sys.argv[1])
api = sys.argv[2]
usecwd = sys.argv[3] == "True"
if api == "find_dotenv":
    value = module.find_dotenv(usecwd=usecwd)
else:
    path = module.find_dotenv(usecwd=True) if usecwd else None
    value = getattr(module, api)(path)
print(json.dumps([value, os.environ.get("DOTENV_RS_DISCOVERY")]))
''', encoding="utf-8")
    env = dict(os.environ)
    env.pop("PYTHON_DOTENV_DISABLED", None)
    env.pop("DOTENV_RS_DISCOVERY", None)
    results = []
    for module in ("dotenv", "dotenv_rs"):
        result = subprocess.run([sys.executable, str(script), module, api, str(usecwd)],
                                cwd=cwd, env=env, capture_output=True, text=True, check=True)
        results.append(json.loads(result.stdout))
    assert results[0] == results[1]
