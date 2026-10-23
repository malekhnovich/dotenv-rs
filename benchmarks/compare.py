"""End-to-end parsing comparison; no file I/O. Run from the repo root."""
import platform
import statistics
import timeit
from importlib.metadata import version
from io import StringIO

from dotenv import dotenv_values as reference
from dotenv_rs import dotenv_values as rust

print(platform.platform(), platform.python_version())
print("python-dotenv", version("python-dotenv"))
for size in (10, 100, 1000):
    text = "".join(f'KEY_{i}="value {i}" # comment\n' for i in range(size))
    assert rust(stream=StringIO(text)) == reference(stream=StringIO(text))
    timings = {}
    for name, function in (("python-dotenv", reference), ("dotenv-rs", rust)):
        timings[name] = statistics.median(timeit.repeat(
            lambda function=function, text=text: function(stream=StringIO(text)), number=100, repeat=5)) / 100
    print(size, timings, "ratio", timings["python-dotenv"] / timings["dotenv-rs"])
