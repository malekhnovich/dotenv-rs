# Upstream compatibility fixtures

Extracted without changing inputs or expected values from python-dotenv v1.2.4:
https://github.com/theskumar/python-dotenv/tree/v1.2.4/tests

- parser.json: all parameterized `test_parse_stream` cases; entries and error line numbers.
- values.json: all parameterized `test_dotenv_values_string_io` cases.

The interactive discovery tests in ../test_interactive.py are also adapted from
`test_is_interactive.py`, with only the import changed and this attribution added.

These cover selected upstream surfaces, not the entire upstream suite. Internal token metadata,
file editing, CLI, IPython, and utility tests are not represented here.
Retained under the upstream BSD-3-Clause license in LICENSE.

Source archive SHA-256: 5ce3633ec9607b8a949aa457f0c7e8438af50d01d4bcc0784f679bc5171711c4
