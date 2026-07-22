"""Rust style plugin for sint-devflow-mcp."""
from style.base import LanguageStyle, AntiPattern, NamingConvention, StyleRule
from typing import List


class RustStyle(LanguageStyle):

    @property
    def name(self) -> str:
        return "rust"

    @property
    def file_extensions(self) -> List[str]:
        return [".rs"]

    @property
    def indent_size(self) -> int:
        return 4

    @property
    def max_line_length(self) -> int:
        return 100

    def naming_conventions(self) -> List[NamingConvention]:
        return [
            NamingConvention(
                symbol_type="function",
                pattern="snake_case",
                example_good="parse_packet", example_bad="ParsePacket",
            ),
            NamingConvention(
                symbol_type="type/struct",
                pattern="PascalCase",
                example_good="PacketParser", example_bad="packet_parser",
            ),
            NamingConvention(
                symbol_type="constant",
                pattern="UPPER_SNAKE",
                example_good="MAX_BUFFER_SIZE", example_bad="maxBufferSize",
            ),
            NamingConvention(
                symbol_type="trait",
                pattern="PascalCase",
                example_good="IntoIterator", example_bad="into_iterator",
            ),
            NamingConvention(
                symbol_type="lifetime",
                pattern="'lowercase",
                example_good="'a, 'buf", example_bad="'A, 'Buf",
            ),
        ]

    def anti_patterns(self) -> List[AntiPattern]:
        return [
            AntiPattern(
                name="unwrap() in production code",
                bad="let val = some_option.unwrap();",
                good="let val = some_option.ok_or(Error::NotFound)?;",
                rule="Never use unwrap() in production. Use ? or match.",
                severity="error",
            ),
            AntiPattern(
                name="clone() to avoid borrow checker",
                bad="let data = big_struct.clone();",
                good="let data = &big_struct;  // or Arc<Mutex<T>>",
                rule="Don't clone to silence the borrow checker. Rethink ownership.",
                severity="warning",
            ),
            AntiPattern(
                name="panic!() for errors",
                bad='panic!("something went wrong");',
                good='return Err(MyError::SomethingWrong);',
                rule="Use Result<T, E> for recoverable errors. panic! only for unrecoverable.",
                severity="error",
            ),
            AntiPattern(
                name="String where &str suffices",
                bad="fn greet(name: String) {",
                good="fn greet(name: &str) {",
                rule="Accept &str instead of String when ownership isn't needed.",
                severity="warning",
            ),
            AntiPattern(
                name="print!() instead of logging",
                bad='println!("debug: {:?}", x);',
                good='tracing::debug!(?x, "debug info");',
                rule="Use tracing/log macros, not print! in library code.",
                severity="info",
            ),
        ]

    def style_rules(self) -> List[StyleRule]:
        return [
            StyleRule(
                name="clippy",
                description="Run cargo clippy with all warnings",
                check="cargo clippy -- -D warnings",
                severity="error",
            ),
            StyleRule(
                name="error handling",
                description="Use thiserror for library errors, anyhow for applications",
                check="#[derive(thiserror::Error)] for library error types",
                severity="warning",
            ),
            StyleRule(
                name="module organization",
                description="pub mod, private internals. One struct per file when large.",
                check="Small focused modules, re-export in lib.rs",
                severity="info",
            ),
            StyleRule(
                name="doc comments",
                description="/// doc comments on all pub items",
                check="/// Description\\n/// # Examples\\n/// ```",
                severity="warning",
            ),
            StyleRule(
                name="test module",
                description="#[cfg(test)] mod tests at bottom of file",
                check="Tests in same file as implementation",
                severity="info",
            ),
        ]
