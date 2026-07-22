"""Commit conventions — conventional commits knowledge base."""
from __future__ import annotations


COMMIT_CONVENTIONS = {
    "type_prefix": True,
    "types": {
        "feat": "new feature",
        "fix": "bug fix",
        "docs": "documentation only",
        "style": "formatting, no code change",
        "refactor": "code restructuring, no behavior change",
        "test": "adding/updating tests",
        "chore": "build, CI, tooling",
        "perf": "performance improvement",
        "revert": "reverting a previous commit",
    },
    "rules": [
        "subject line: imperative mood, lowercase, no period, max 72 chars",
        "body: explain WHY, not WHAT (git diff shows what)",
        "reference issues: Closes #123, Fixes #456",
        "breaking changes: start subject with BREAKING CHANGE: or use ! after type",
    ],
    "examples": {
        "good": [
            "feat: add ECHONET Lite packet parser",
            "fix: handle partial recv in taint tracker",
            "docs: add architecture diagram for re-graph",
            "test: add edge cases for CRC-32 pattern detector",
            "refactor: extract pattern matching into separate module",
            "perf: cache embeddings in SQLite instead of recomputing",
        ],
        "bad": [
            "Fixed stuff",
            "update code",
            "feat: added parser",
            "WIP",
        ],
    },
}


def get_commit_conventions() -> dict:
    """Get commit message conventions."""
    return COMMIT_CONVENTIONS


def suggest_commit_message(change_type: str, scope: str, description: str) -> str:
    """Generate a conventional commit message."""
    types = COMMIT_CONVENTIONS["types"]
    if change_type not in types:
        change_type = "feat"

    if scope:
        msg = f"{change_type}({scope}): {description.lower()}"
    else:
        msg = f"{change_type}: {description.lower()}"

    if len(msg) > 72:
        msg = msg[:69] + "..."

    return msg
