"""C99/C11 style plugin for sint-devflow-mcp."""
from style.base import LanguageStyle, AntiPattern, NamingConvention, StyleRule
from typing import List


class CStyle(LanguageStyle):

    @property
    def name(self) -> str:
        return "c"

    @property
    def file_extensions(self) -> List[str]:
        return [".c", ".h"]

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
                symbol_type="type",
                pattern="snake_case",
                example_good="struct packet_info", example_bad="PacketInfo",
            ),
            NamingConvention(
                symbol_type="macro",
                pattern="UPPER_SNAKE",
                example_good="MAX_BUFFER_SIZE", example_bad="maxBufferSize",
            ),
            NamingConvention(
                symbol_type="constant",
                pattern="UPPER_SNAKE",
                example_good="TIMEOUT_MS", example_bad="timeoutMs",
            ),
            NamingConvention(
                symbol_type="local_variable",
                pattern="snake_case",
                example_good="byte_count", example_bad="byteCount",
            ),
            NamingConvention(
                symbol_type="parameter",
                pattern="snake_case",
                example_good="buf_size", example_bad="bufSize",
            ),
        ]

    def anti_patterns(self) -> List[AntiPattern]:
        return [
            AntiPattern(
                name="malloc without null check",
                bad='char *buf = malloc(1024);',
                good='char *buf = malloc(1024);\nif (!buf) goto cleanup;',
                rule="Always check malloc return. Use goto cleanup pattern.",
                severity="error",
            ),
            AntiPattern(
                name="unbounded string copy",
                bad="strcpy(dst, src);",
                good="strncpy(dst, src, sizeof(dst) - 1);\ndst[sizeof(dst) - 1] = '\\0';",
                rule="Never use strcpy/strcat. Use bounded variants.",
                severity="error",
            ),
            AntiPattern(
                name="magic numbers",
                bad='if (buf[3] == 0x42) {',
                good='#define HEADER_MAGIC 0x42\nif (buf[3] == HEADER_MAGIC) {',
                rule="Define constants for all magic numbers.",
                severity="warning",
            ),
            AntiPattern(
                name="deeply nested if",
                bad='if (a) { if (b) { if (c) { ... } } }',
                good='if (!a) goto cleanup;\nif (!b) goto cleanup;\nif (!c) goto cleanup;\n// main logic flat',
                rule="Use early-return / guard clauses. Flatten nesting.",
                severity="warning",
            ),
            AntiPattern(
                name="sprintf (unbounded)",
                bad='sprintf(buf, "value: %d", x);',
                good='snprintf(buf, sizeof(buf), "value: %d", x);',
                rule="Always use snprintf. Never sprintf.",
                severity="error",
            ),
            AntiPattern(
                name="goto into block",
                bad='goto label;\n...\nlabel:\n    { int x = 1; ... }',
                good='// goto should jump to cleanup at end of function',
                rule="Only goto forward, only to cleanup labels.",
                severity="warning",
            ),
            AntiPattern(
                name="void* implicit cast",
                bad='int *p = malloc(sizeof(int));',
                good='int *p = malloc(sizeof(int));\n// or in C11: int *p = malloc(sizeof *p);',
                rule="In C++ this is an error. In C, prefer explicit cast for portability.",
                severity="info",
            ),
        ]

    def style_rules(self) -> List[StyleRule]:
        return [
            StyleRule(
                name="include guard",
                description="Use #ifndef HEADER_H / #define HEADER_H / #endif",
                check="Every .h file must have include guard",
                severity="error",
            ),
            StyleRule(
                name="one function per purpose",
                description="Functions should do one thing. Max ~50 lines.",
                check="Split long functions",
                severity="warning",
            ),
            StyleRule(
                name="error handling",
                description="Use goto cleanup pattern for resource management",
                check="All allocations have corresponding frees in cleanup",
                severity="warning",
            ),
            StyleRule(
                name="const correctness",
                description="Mark read-only parameters as const",
                check="Pointer params that are not modified should be const",
                severity="info",
            ),
            StyleRule(
                name="header include order",
                description="1) own header, 2) system headers, 3) project headers",
                check="Includes follow recommended order",
                severity="info",
            ),
        ]
