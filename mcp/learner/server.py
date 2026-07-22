"""sint-learner-mcp server (fastmcp, stdio).

Cross-session learning: error patterns, improvements, meta-memory.

The agent logs mistakes, detects patterns over time,
and checks before sessions what NOT to repeat.

Tools:
  log_error(mistake, context, fix)     — record a mistake
  get_errors(category, severity)       — list errors
  get_repeated()                       — errors that keep happening
  detect_patterns()                    — auto-detect patterns from errors
  log_session(summary, ...)            — log session summary
  log_improvement(what, before, after) — record improvement
  pre_session_check()                  — what NOT to do (anti-patterns)
  get_learning_summary()               — full learning overview

Run: python server.py (stdio)
"""
from __future__ import annotations

import json

from fastmcp import FastMCP

from config import NAME
from state import (
    log_error, get_errors, get_repeated_errors,
    detect_patterns, get_patterns,
    log_session, get_session_history,
    log_improvement, get_improvements,
    get_learning_summary, pre_session_check,
)

mcp = FastMCP(NAME)


# ═══════════════════════════════════════════════════════════════════
# ERROR LOGGING
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def log_error_tool(mistake: str, context: str, fix: str,
                   category: str = "reasoning",
                   severity: str = "medium") -> str:
    """Log a mistake from the current session.

    Args:
        mistake: what went wrong (description)
        context: where it happened (task, project, situation)
        fix: what to do instead next time
        category: reasoning|perception|action|assumption
        severity: low|medium|high|critical
    Returns: error entry with ID and repeat detection.
    """
    result = log_error(mistake=mistake, context=context, fix=fix,
                      category=category, severity=severity)
    repeat_notice = ""
    if result.get("is_repeat"):
        repeat_notice = f" (REPEAT #{result.get('times_repeated', 2)} — this is a pattern!)"

    return json.dumps({
        "logged": result["id"],
        "repeat": result.get("is_repeat", False),
        "times_repeated": result.get("times_repeated", 1),
        "notice": repeat_notice,
    }, ensure_ascii=False, indent=1)


@mcp.tool()
def get_errors_tool(category: str = "", severity: str = "",
                    limit: int = 10) -> str:
    """Get logged errors, optionally filtered."""
    result = get_errors(category=category, min_severity=severity, limit=limit)
    return json.dumps(result, ensure_ascii=False, indent=1)


@mcp.tool()
def get_repeated() -> str:
    """Get errors that keep happening (patterns).

    These are the most important: they show what the agent
    keeps getting wrong across sessions.
    """
    result = get_repeated_errors(min_repeats=2)
    return json.dumps(result, ensure_ascii=False, indent=1)


# ═══════════════════════════════════════════════════════════════════
# PATTERN DETECTION
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def detect_error_patterns() -> str:
    """Auto-detect patterns from error log.

    Groups errors by category, finds the most common fixes,
    and generates actionable anti-patterns.
    """
    result = detect_patterns()
    return json.dumps(result, ensure_ascii=False, indent=1)


@mcp.tool()
def get_patterns_tool() -> str:
    """Get previously detected error patterns."""
    return json.dumps(get_patterns(), ensure_ascii=False, indent=1)


# ═══════════════════════════════════════════════════════════════════
# SESSION LOGGING
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def log_session_tool(summary: str, errors_count: int = 0,
                     findings_count: int = 0,
                     beliefs_changed: int = 0,
                     duration_min: float = 0) -> str:
    """Log session summary for cross-session learning.

    Call at end of session to record what happened.
    """
    result = log_session(summary=summary, errors_count=errors_count,
                        findings_count=findings_count,
                        beliefs_changed=beliefs_changed,
                        duration_min=duration_min)
    return json.dumps(result, ensure_ascii=False, indent=1)


@mcp.tool()
def get_session_history_tool(limit: int = 5) -> str:
    """Get recent session summaries."""
    return json.dumps(get_session_history(limit=limit), ensure_ascii=False, indent=1)


# ═══════════════════════════════════════════════════════════════════
# IMPROVEMENTS
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def log_improvement_tool(what_improved: str, before: str, after: str,
                         reason: str = "") -> str:
    """Record something the agent improved on.

    Use when you notice you're doing better than before.
    """
    result = log_improvement(what_improved=what_improved, before=before,
                            after=after, reason=reason)
    return json.dumps(result, ensure_ascii=False, indent=1)


@mcp.tool()
def get_improvements_tool(limit: int = 10) -> str:
    """Get recent improvements."""
    return json.dumps(get_improvements(limit=limit), ensure_ascii=False, indent=1)


# ═══════════════════════════════════════════════════════════════════
# LEARNING SUMMARY
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def get_learning_summary_tool() -> str:
    """Full learning summary: what I've learned, what I keep getting wrong.

    Shows: error counts, repeated patterns, improvements,
    session history overview.
    """
    return json.dumps(get_learning_summary(), ensure_ascii=False, indent=1)


@mcp.tool()
def pre_session_check_tool() -> str:
    """Check before starting: what should I remember NOT to do?

    Returns anti-patterns from past errors.
    Call this at the start of each session.
    """
    return json.dumps(pre_session_check(), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    mcp.run(transport="stdio")
