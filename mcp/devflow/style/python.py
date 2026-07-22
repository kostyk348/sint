"""Python style plugin for sint-devflow-mcp."""
from style.base import LanguageStyle, AntiPattern, NamingConvention, StyleRule
from typing import List


class PythonStyle(LanguageStyle):

    @property
    def name(self) -> str:
        return "python"

    @property
    def file_extensions(self) -> List[str]:
        return [".py"]

    @property
    def indent_size(self) -> int:
        return 4

    @property
    def max_line_length(self) -> int:
        return 88  # black default

    def naming_conventions(self) -> List[NamingConvention]:
        return [
            NamingConvention(
                symbol_type="function",
                pattern="snake_case",
                example_good="parse_packet", example_bad="parsePacket",
            ),
            NamingConvention(
                symbol_type="class",
                pattern="PascalCase",
                example_good="PacketParser", example_bad="packet_parser",
            ),
            NamingConvention(
                symbol_type="constant",
                pattern="UPPER_SNAKE",
                example_good="MAX_BUFFER_SIZE", example_bad="max_buffer_size",
            ),
            NamingConvention(
                symbol_type="variable",
                pattern="snake_case",
                example_good="byte_count", example_bad="byteCount",
            ),
            NamingConvention(
                symbol_type="private",
                pattern="_leading_underscore",
                example_good="_internal_method", example_bad="internal_method",
            ),
            NamingConvention(
                symbol_type="dunder",
                pattern="__double_leading_underscore",
                example_good="__init__", example_bad="_init_",
            ),
        ]

    def anti_patterns(self) -> List[AntiPattern]:
        return [
            AntiPattern(
                name="bare except",
                bad="except:\n    pass",
                good="except SpecificError as e:\n    logger.warning(f'failed: {e}')",
                rule="Never use bare except. Catch specific exceptions. Never silently swallow errors.",
                severity="error",
            ),
            AntiPattern(
                name="mutable default argument",
                bad="def foo(items=[]):",
                good="def foo(items=None):\n    items = items or []",
                rule="Never use mutable defaults. Use None and initialize inside.",
                severity="error",
            ),
            AntiPattern(
                name="import inside function",
                bad="def process():\n    import json",
                good="import json  # at top of file\n\ndef process():",
                rule="Imports at top of file. Exception: optional/conditional imports.",
                severity="warning",
            ),
            AntiPattern(
                name="string concatenation in loop",
                bad="result = ''\nfor item in items:\n    result += str(item)",
                good="result = ''.join(str(item) for item in items)",
                rule="Use join() or list comprehension instead of += in loops.",
                severity="warning",
            ),
            AntiPattern(
                name="global state mutation",
                bad="GLOBAL = {}\ndef setup():\n    global GLOBAL\n    GLOBAL = load()",
                good="class Config:\n    def __init__(self):\n        self.data = load()",
                rule="Avoid globals. Use dependency injection or class instances.",
                severity="warning",
            ),
            AntiPattern(
                name="type() instead of isinstance()",
                bad="if type(x) == str:",
                good="if isinstance(x, str):",
                rule="Use isinstance() for type checks. It handles inheritance.",
                severity="warning",
            ),
            AntiPattern(
                name="except Exception too broad",
                bad="except Exception:\n    pass",
                good="except (ValueError, KeyError) as e:\n    handle(e)",
                rule="Catch specific exceptions, not broad Exception.",
                severity="warning",
            ),
            AntiPattern(
                name="lambda assigned to variable",
                bad="f = lambda x: x + 1",
                good="def f(x):\n    return x + 1",
                rule="Use def for named functions. Lambdas are for anonymous inline use.",
                severity="info",
            ),
        ]

    def style_rules(self) -> List[StyleRule]:
        return [
            StyleRule(
                name="type hints",
                description="Public functions must have type hints",
                check="def func(x: int, y: str) -> bool:",
                severity="warning",
            ),
            StyleRule(
                name="docstring",
                description="Public functions/classes must have docstrings (Google style)",
                check="Google-style docstring with Args/Returns/Raises",
                severity="warning",
            ),
            StyleRule(
                name="import order",
                description="stdlib → third-party → local, separated by blank lines",
                check="import order: stdlib, blank, third-party, blank, local",
                severity="info",
            ),
            StyleRule(
                name="blank lines",
                description="2 blank lines between top-level definitions, 1 between methods",
                check="Two blank lines before def/class at module level",
                severity="info",
            ),
            StyleRule(
                name="f-strings preferred",
                description="Use f-strings over .format() and %",
                check="f'Hello {name}' instead of 'Hello {}'.format(name)",
                severity="info",
            ),
            StyleRule(
                name="pathlib over os.path",
                description="Use pathlib.Path instead of os.path",
                check="from pathlib import Path; p = Path('file.txt')",
                severity="info",
            ),
            StyleRule(
                name="dataclass or attrs for data",
                description="Use @dataclass instead of __init__ with many params",
                check="@dataclass\nclass Config:\n    name: str\n    size: int",
                severity="info",
            ),
        ]
