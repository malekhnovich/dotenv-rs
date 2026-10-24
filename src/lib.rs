use pyo3::prelude::*;

type Entry = (String, Option<String>);

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

// Positions are UTF-8 byte offsets. Every advance follows a char boundary.
struct Cursor<'a> {
    text: &'a str,
    pos: usize,
}

fn whitespace(c: char) -> bool {
    // Python str.isspace also includes these four ASCII separators.
    c.is_whitespace() || ('\u{1c}'..='\u{1f}').contains(&c)
}

impl<'a> Cursor<'a> {
    fn rest(&self) -> &'a str {
        &self.text[self.pos..]
    }
    fn peek(&self) -> Option<char> {
        self.rest().chars().next()
    }
    fn advance(&mut self) {
        if let Some(c) = self.peek() {
            self.pos += c.len_utf8();
        }
    }
    fn take_while(&mut self, predicate: impl Fn(char) -> bool) -> &'a str {
        let start = self.pos;
        while self.peek().is_some_and(&predicate) {
            self.advance();
        }
        &self.text[start..self.pos]
    }
    fn horizontal(&mut self) -> &'a str {
        self.take_while(|c| whitespace(c) && c != '\r' && c != '\n')
    }
    fn line_end(&mut self) -> Result<(), ()> {
        match self.peek() {
            None => Ok(()),
            Some('\r') => {
                self.advance();
                if self.peek() == Some('\n') {
                    self.advance();
                }
                Ok(())
            }
            Some('\n') => {
                self.advance();
                Ok(())
            }
            _ => Err(()),
        }
    }
    fn recover(&mut self) {
        self.take_while(|c| c != '\r' && c != '\n');
        // The reference recovery consumes one newline character, including only
        // CR from CRLF. Preserve this detail for subsequent diagnostic line numbers.
        self.advance();
    }
    fn quoted(&mut self, quote: char, escapes: bool) -> Result<&'a str, ()> {
        // Do not advance on an unterminated quote: recovery starts at the opening quote.
        let start = self.pos + 1;
        let mut chars = self.text[start..].char_indices();
        while let Some((i, c)) = chars.next() {
            if c == quote {
                self.pos = start + i + 1;
                return Ok(&self.text[start..start + i]);
            }
            if escapes && c == '\\' {
                chars.next();
            }
        }
        Err(())
    }
    fn binding(&mut self) -> Result<Option<Entry>, ()> {
        self.take_while(whitespace);
        if self.peek().is_none() {
            return Ok(None);
        }
        if self
            .rest()
            .strip_prefix("export")
            .and_then(|s| s.chars().next())
            .is_some_and(|c| whitespace(c) && c != '\r' && c != '\n')
        {
            self.pos += "export".len();
            self.horizontal();
        }
        let key = match self.peek() {
            Some('#') => {
                self.take_while(|c| c != '\r' && c != '\n');
                self.line_end()?;
                return Ok(None);
            }
            Some('\'') => {
                let key = self.quoted('\'', false)?;
                if key.is_empty() {
                    return Err(());
                }
                key
            }
            _ => {
                let key = self.take_while(|c| !whitespace(c) && c != '=' && c != '#');
                if key.is_empty() {
                    return Err(());
                }
                key
            }
        };
        self.horizontal();
        let value = if self.peek() == Some('=') {
            self.advance();
            let space = !self.horizontal().is_empty();
            Some(match self.peek() {
                Some('#') if space => String::new(),
                Some('\'') => decode(self.quoted('\'', true)?, false),
                Some('"') => decode(self.quoted('"', true)?, true),
                _ => {
                    let raw = self.take_while(|c| c != '\r' && c != '\n');
                    let mut previous_space = false;
                    let mut end = raw.len();
                    for (i, c) in raw.char_indices() {
                        if c == '#' && previous_space {
                            end = i;
                            break;
                        }
                        previous_space = whitespace(c);
                    }
                    raw[..end].trim_end_matches(whitespace).to_owned()
                }
            })
        } else {
            None
        };
        self.horizontal();
        if self.peek() == Some('#') {
            self.take_while(|c| c != '\r' && c != '\n');
        }
        self.line_end()?;
        Ok(Some((key.to_owned(), value)))
    }
}

fn parse_report(text: &str) -> (Vec<Entry>, Vec<usize>) {
    let mut cursor = Cursor {
        text: text.strip_prefix('\u{feff}').unwrap_or(text),
        pos: 0,
    };
    let mut result = Vec::new();
    let mut errors = Vec::new();
    let mut line = 1;
    while cursor.peek().is_some() {
        let start = cursor.pos;
        match cursor.binding() {
            Ok(Some(entry)) => result.push(entry),
            Ok(None) => {}
            Err(()) => {
                errors.push(line);
                cursor.recover();
            }
        }
        let consumed = &cursor.text[start..cursor.pos];
        line += consumed.chars().filter(|&c| c == '\n' || c == '\r').count()
            - consumed.matches("\r\n").count();
    }
    (result, errors)
}

fn parse_impl(text: &str) -> Vec<Entry> {
    parse_report(text).0
}

#[pyfunction]
fn parse_with_errors(text: &str) -> (Vec<Entry>, Vec<usize>) {
    parse_report(text)
}

/// Parse bindings in order; duplicate keys are preserved for interpolation.
#[pyfunction]
fn parse(text: &str) -> Vec<Entry> {
    parse_impl(text)
}

#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add(
        "build_profile",
        if cfg!(debug_assertions) {
            "debug"
        } else {
            "release"
        },
    )?;
    m.add_function(wrap_pyfunction!(parse, m)?)?;
    m.add_function(wrap_pyfunction!(parse_with_errors, m)?)?;
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
