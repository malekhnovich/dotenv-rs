"""Compare public dotenv_values APIs in memory; write reproducible JSON results."""
from __future__ import annotations

import argparse
import json
import os
import platform
import random
import statistics
import subprocess
import timeit
from datetime import datetime, timezone
from importlib.metadata import version
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from dotenv import dotenv_values as reference
from dotenv_rs import _core
from dotenv_rs import dotenv_values as rust


def workload(kind: str, size: int) -> str:
    if kind == "plain":
        return "".join(f"KEY_{i}=value_{i}\n" for i in range(size))
    if kind == "quoted":
        return "".join(f'KEY_{i}="value {i}" # comment\n' for i in range(size))
    if kind == "interpolation":
        return "BASE=example.org\n" + "".join(f"KEY_{i}=${{BASE}}/path/{i}\n" for i in range(size - 1))
    return "".join(f'KEY_{i}="héllo 🌎 {i}\\nsecond line"\n' for i in range(size))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("benchmarks/results.json"))
    parser.add_argument("--update-readme", action="store_true")
    args = parser.parse_args()
    if _core.build_profile != "release":
        parser.error("Build the optimized extension first: uv run maturin develop --release")
    cpu = platform.processor() or platform.machine()
    if platform.system() == "Darwin":
        cpu = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], text=True).strip()
    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(), "cpu": cpu, "python": platform.python_version(),
        "python_dotenv": version("python-dotenv"), "dotenv_rs": version("dotenv-rs"),
        "build_profile": _core.build_profile,
        "environment_variables": 40, "repeats": 7,
        "statistic": "median seconds per call", "rows": [],
    }
    # A fixed, synthetic environment makes interpolation cost reproducible and records no secrets.
    environment = {f"BENCH_ENV_{i}": f"value_{i}" for i in range(40)}
    rng = random.Random(42)
    with patch.dict(os.environ, environment, clear=True):
        for kind in ("plain", "quoted", "interpolation", "unicode_multiline"):
            for size in (10, 100, 1000):
                text = workload(kind, size)
                assert rust(stream=StringIO(text)) == reference(stream=StringIO(text))
                number = max(5, 3000 // size)
                samples = {"python_dotenv": [], "dotenv_rs": []}
                for _ in range(7):
                    order = [("python_dotenv", reference), ("dotenv_rs", rust)]
                    rng.shuffle(order)
                    for name, function in order:
                        samples[name].append(timeit.timeit(
                            lambda function=function, text=text: function(stream=StringIO(text)),
                            number=number) / number)
                medians = {name: statistics.median(values) for name, values in samples.items()}
                row = dict(workload=kind, bindings=size, calls_per_repeat=number,
                           **medians, speedup=medians["python_dotenv"] / medians["dotenv_rs"],
                           samples_seconds=samples)
                report["rows"].append(row)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = ["| Workload | Bindings | python-dotenv | dotenv-rs | Speedup |",
             "| --- | ---: | ---: | ---: | ---: |"]
    for row in report["rows"]:
        lines.append(f'| {row["workload"]} | {row["bindings"]:,} | '
                     f'{row["python_dotenv"] * 1e6:,.1f} µs | {row["dotenv_rs"] * 1e6:,.1f} µs | '
                     f'{row["speedup"]:.1f}× |')
    table = "\n".join(lines)
    description = (f'Measured {report["timestamp_utc"][:10]} UTC on {cpu}, {report["platform"]}, '
                   f'CPython {report["python"]}; python-dotenv {report["python_dotenv"]} '
                   f'and dotenv-rs {report["dotenv_rs"]}. Rust release build.\n\n')
    print(description + table)
    if args.update_readme:
        path = Path("README.md")
        before, rest = path.read_text(encoding="utf-8").split("<!-- BENCHMARKS:START -->")
        _, after = rest.split("<!-- BENCHMARKS:END -->")
        path.write_text(before + "<!-- BENCHMARKS:START -->\n" + description + table
                        + "\n<!-- BENCHMARKS:END -->" + after, encoding="utf-8")


if __name__ == "__main__":
    main()
