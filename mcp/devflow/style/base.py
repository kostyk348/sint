"""Base class for language style modules.

Every language plugin inherits from LanguageStyle and registers itself
with the registry. New language = new file, no changes to server.py.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AntiPattern:
    """A known bad practice with good alternative."""
    name: str
    bad: str
    good: str
    rule: str
    severity: str = "warning"  # warning | error | info


@dataclass
class NamingConvention:
    """Naming rules for a symbol type."""
    symbol_type: str  # function, class, constant, macro, variable, etc.
    pattern: str      # snake_case, PascalCase, UPPER_SNAKE, camelCase, etc.
    regex: str = ""   # optional validation regex
    example_good: str = ""
    example_bad: str = ""


@dataclass
class StyleRule:
    """A single style rule."""
    name: str
    description: str
    check: str  # human-readable check description
    severity: str = "warning"


class LanguageStyle(ABC):
    """Base class for language style plugins.

    Subclass this, implement abstract methods, and register:
        registry.register("c", CStyle())
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Language name (e.g. 'c', 'python', 'rust')."""

    @property
    @abstractmethod
    def file_extensions(self) -> List[str]:
        """File extensions for this language (e.g. ['.c', '.h'])."""

    @property
    @abstractmethod
    def indent_size(self) -> int:
        """Recommended indent size."""

    @property
    @abstractmethod
    def max_line_length(self) -> int:
        """Max line length before warning."""

    @abstractmethod
    def naming_conventions(self) -> List[NamingConvention]:
        """Return naming rules for this language."""

    @abstractmethod
    def anti_patterns(self) -> List[AntiPattern]:
        """Return known anti-patterns with fixes."""

    @abstractmethod
    def style_rules(self) -> List[StyleRule]:
        """Return additional style rules."""

    def get_config(self) -> dict:
        """Export full config as dict (for JSON serialization)."""
        return {
            "language": self.name,
            "extensions": self.file_extensions,
            "indent": self.indent_size,
            "max_line_length": self.max_line_length,
            "naming": [
                {"type": n.symbol_type, "pattern": n.pattern,
                 "example_good": n.example_good, "example_bad": n.example_bad}
                for n in self.naming_conventions()
            ],
            "anti_patterns": [
                {"name": a.name, "bad": a.bad, "good": a.good,
                 "rule": a.rule, "severity": a.severity}
                for a in self.anti_patterns()
            ],
            "style_rules": [
                {"name": r.name, "description": r.description,
                 "check": r.check, "severity": r.severity}
                for r in self.style_rules()
            ],
        }

    def review_code(self, code: str) -> dict:
        """Review code against this language's rules.

        Override for language-specific analysis. Base implementation
        checks anti-patterns and line length.
        """
        lines = code.split("\n")
        findings = []

        # Check anti-patterns (first line match)
        for ap in self.anti_patterns():
            for i, line in enumerate(lines):
                # Check first 40 chars of each anti-pattern line
                bad_first_line = ap.bad.split("\n")[0][:40].strip()
                if bad_first_line and bad_first_line in line:
                    findings.append({
                        "line": i + 1,
                        "severity": ap.severity,
                        "type": "anti_pattern",
                        "name": ap.name,
                        "message": ap.rule,
                        "bad": ap.bad[:100],
                        "good": ap.good[:200],
                    })

        # Check line length
        long_lines = [(i + 1, len(line))
                      for i, line in enumerate(lines)
                      if len(line) > self.max_line_length]
        if long_lines:
            findings.append({
                "line": None,
                "severity": "info",
                "type": "line_length",
                "name": "line_length",
                "message": f"{len(long_lines)} lines exceed {self.max_line_length} chars",
                "locations": long_lines[:5],
            })

        # Check TODO/FIXME
        todos = [(i + 1, line.strip())
                 for i, line in enumerate(lines)
                 if any(kw in line for kw in ("TODO", "FIXME", "HACK", "XXX"))]
        if todos:
            findings.append({
                "line": None,
                "severity": "info",
                "type": "todo",
                "name": "todo_comment",
                "message": f"{len(todos)} TODO/FIXME comments",
                "locations": todos[:5],
            })

        score = max(0, 100 - len(findings) * 5)
        return {
            "language": self.name,
            "score": score,
            "findings": findings,
            "summary": f"{len(findings)} issues found" if findings else "clean",
        }
