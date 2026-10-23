use pyo3::prelude::*;
use regex::Regex;
use std::sync::LazyLock;

type Entry = (String, Option<String>);
static BINDING: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
    r#"(?x)\A[^\S\r\n]*(?:export[^\S\r\n]+)?(?:'(?P<qkey>[^']*)'|(?P<key>[^=\#\s]+))[^\S\r\n]*(?:=[^\S\r\n]*(?:'(?P<single>(?:\\'|[^'])*)'|"(?P<double>(?:\\"|[^"])*)"|(?P<plain>[^\r\n]*)))?[^\S\r\n]*(?:\#[^\r\n]*)?(?:\r\n|\n|\r|\z)"#
).unwrap()
});

fn decode(value: &str, double: bool) -> String {
    let mut out = String::with_capacity(value.len());
    let mut chars = value.chars().peekable();
    while let Some(c) = chars.next() {
        if c == '\\' {
            if let Some(&next) = chars.peek() {
                let replacement = match next {
                    '\\' => Some('\\'),
                    '\'' => Some('\''),
                    '"' if double => Some('"'),
                    'n' if double => Some('\n'),
                    'r' if double => Some('\r'),
                    't' if double => Some('\t'),
                    'a' if double => Some('\x07'),
                    'b' if double => Some('\x08'),
                    'f' if double => Some('\x0c'),
                    'v' if double => Some('\x0b'),
                    _ => None,
                };
                if let Some(decoded) = replacement {
                    chars.next();
                    out.push(decoded);
                    continue;
                }
            }
        }
        out.push(c);
    }
    out
}

fn parse_impl(mut text: &str) -> Vec<Entry> {
    let mut result = Vec::new();
    while !text.is_empty() {
        if let Some(caps) = BINDING.captures(text) {
            let key = caps
                .name("key")
                .or_else(|| caps.name("qkey"))
                .unwrap()
                .as_str();
            let value = if let Some(v) = caps.name("single") {
                Some(decode(v.as_str(), false))
            } else if let Some(v) = caps.name("double") {
                Some(decode(v.as_str(), true))
            } else {
                caps.name("plain").map(|v| {
                    let s = v.as_str();
                    let end = s
                        .char_indices()
                        .find(|&(i, c)| c == '#' && i > 0 && s[..i].ends_with(char::is_whitespace))
                        .map_or(s.len(), |(i, _)| i);
                    s[..end].trim_end().to_owned()
                })
            };
            result.push((key.to_owned(), value));
            text = &text[caps.get(0).unwrap().end()..];
        } else {
            text = text.find('\n').map_or("", |i| &text[i + 1..]);
        }
    }
    result
}

/// Parse bindings in order; duplicate keys are preserved for interpolation.
#[pyfunction]
fn parse(text: &str) -> Vec<Entry> {
    parse_impl(text)
}

#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn quoted_multiline_and_missing() {
        assert_eq!(
            parse_impl("export A=hello # comment\nB=\"one\\ntwo\"\nEMPTY=\nMISSING\n"),
            vec![
                ("A".into(), Some("hello".into())),
                ("B".into(), Some("one\ntwo".into())),
                ("EMPTY".into(), Some("".into())),
                ("MISSING".into(), None)
            ]
        );
    }
    #[test]
    fn malformed_line_recovers() {
        assert_eq!(
            parse_impl("bad line\nOK=yes\n"),
            vec![("OK".into(), Some("yes".into()))]
        );
    }
}
