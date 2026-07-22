"""sint-devflow-mcp configuration."""
from pathlib import Path

NAME = "sint-devflow-mcp"
VERSION = "0.1.0"

BASE_DIR = Path(__file__).parent
CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# Style rules (C99 + Python defaults)
DEFAULT_C_STYLE = {
    "indent": 4,
    "indent_style": "spaces",
    "max_line_length": 100,
    "brace_style": "k&r",
    "naming_functions": "snake_case",
    "naming_types": "snake_case",
    "naming_macros": "UPPER_SNAKE",
    "naming_constants": "UPPER_SNAKE",
    "header_guard": "FILENAME_H",
    "comment_style": "// for inline, /** */ for doc",
    "bool_prefix": "is_",
    "error_handling": "goto cleanup pattern",
    "memory": "explicit free, no hidden alloc",
    "include_order": "own header first, then system, then project",
}

DEFAULT_PY_STYLE = {
    "indent": 4,
    "max_line_length": 88,
    "naming_functions": "snake_case",
    "naming_classes": "PascalCase",
    "naming_constants": "UPPER_SNAKE",
    "docstring": "google style",
    "type_hints": "required for public API",
    "imports": "stdlib → third-party → local, sorted",
    "line_spacing": "2 blank lines between top-level",
    "single_line_if": "for short conditions only",
    "f_strings": "preferred over .format()",
}
