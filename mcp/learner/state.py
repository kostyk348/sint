"""Cross-session learning: error patterns, improvements, meta-memory.

Every session, the agent logs mistakes and what it learned.
Over time, patterns emerge: "you keep doing X → stop doing X."
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List, Optional

from config import (
    ERRORS_FILE, PATTERNS_FILE, SESSIONS_FILE, IMPROVEMENTS_FILE,
    PATTERN_MIN_OCCURRENCES, STALE_ERROR_DAYS,
)


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _today() -> str:
    return time.strftime("%Y-%m-%d")


def _load(path: Path, default=None) -> dict | list:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return default if default is not None else {}


def _save(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════
# ERROR LOG
# ═══════════════════════════════════════════════════════════════════

def log_error(mistake: str, context: str, fix: str,
              category: str = "reasoning",
              severity: str = "medium",
              session_id: str = "") -> dict:
    """Log an error/mistake from the current session."""
    data = _load(ERRORS_FILE, {"errors": [], "total": 0})

    eid = f"E{len(data['errors']) + 1:04d}"
    error = {
        "id": eid,
        "mistake": mistake,
        "context": context,
        "fix": fix,
        "category": category,  # reasoning | perception | action | assumption
        "severity": severity,  # low | medium | high | critical
        "session_id": session_id,
        "date": _today(),
        "timestamp": _now(),
        "times_repeated": 1,
        "verified": False,
        "superseded_by": None,
    }

    # Check if similar error exists (basic dedup)
    for existing in data["errors"]:
        if _similar(mistake, existing["mistake"]):
            existing["times_repeated"] = existing.get("times_repeated", 1) + 1
            existing["last_seen"] = _today()
            error["id"] = existing["id"]
            error["is_repeat"] = True
            _save(ERRORS_FILE, data)
            return error

    data["errors"].append(error)
    data["total"] = len(data["errors"])
    _save(ERRORS_FILE, data)
    return error


def get_errors(category: str = "", min_severity: str = "",
               limit: int = 20) -> dict:
    """Get errors, optionally filtered."""
    data = _load(ERRORS_FILE, {"errors": [], "total": 0})
    errors = data.get("errors", [])

    if category:
        errors = [e for e in errors if e.get("category") == category]

    severity_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
    if min_severity:
        min_sev = severity_order.get(min_severity, 0)
        errors = [e for e in errors
                  if severity_order.get(e.get("severity", "low"), 0) >= min_sev]

    # Sort by date descending, limit
    errors.sort(key=lambda e: e.get("date", ""), reverse=True)

    return {
        "total": data.get("total", 0),
        "showing": len(errors[:limit]),
        "errors": errors[:limit],
    }


def get_repeated_errors(min_repeats: int = 2) -> dict:
    """Get errors that keep happening (patterns)."""
    data = _load(ERRORS_FILE, {"errors": [], "total": 0})
    repeated = [
        e for e in data.get("errors", [])
        if e.get("times_repeated", 1) >= min_repeats
    ]
    repeated.sort(key=lambda e: e.get("times_repeated", 0), reverse=True)
    return {
        "total_repeated": len(repeated),
        "errors": repeated,
    }


# ═══════════════════════════════════════════════════════════════════
# PATTERNS (auto-detected from errors)
# ═══════════════════════════════════════════════════════════════════

def detect_patterns() -> dict:
    """Auto-detect patterns from error log."""
    data = _load(ERRORS_FILE, {"errors": [], "total": 0})
    errors = data.get("errors", [])

    # Group by category
    by_category = {}
    for e in errors:
        cat = e.get("category", "other")
        by_category.setdefault(cat, []).append(e)

    patterns = []
    for cat, cat_errors in by_category.items():
        if len(cat_errors) >= PATTERN_MIN_OCCURRENCES:
            # Find the most common fix
            fixes = {}
            for e in cat_errors:
                fix = e.get("fix", "")
                fixes[fix] = fixes.get(fix, 0) + 1

            best_fix = max(fixes.items(), key=lambda x: x[1]) if fixes else ("", 0)

            patterns.append({
                "category": cat,
                "count": len(cat_errors),
                "sample_mistakes": [e["mistake"][:80] for e in cat_errors[:3]],
                "recommended_fix": best_fix[0],
                "fix_confidence": round(best_fix[1] / len(cat_errors), 2),
            })

    # Sort by frequency
    patterns.sort(key=lambda p: p["count"], reverse=True)

    # Save detected patterns
    _save(PATTERNS_FILE, {
        "detected": _today(),
        "patterns": patterns,
        "total": len(patterns),
    })

    return {
        "total_patterns": len(patterns),
        "patterns": patterns,
    }


def get_patterns() -> dict:
    """Get previously detected patterns."""
    return _load(PATTERNS_FILE, {"patterns": [], "total": 0})


# ═══════════════════════════════════════════════════════════════════
# SESSION LOGGING
# ═══════════════════════════════════════════════════════════════════

def log_session(summary: str, errors_count: int = 0,
                findings_count: int = 0,
                beliefs_changed: int = 0,
                duration_min: float = 0) -> dict:
    """Log a session summary for cross-session learning."""
    data = _load(SESSIONS_FILE, {"sessions": [], "total": 0})

    sid = f"S{len(data['sessions']) + 1:04d}"
    session = {
        "id": sid,
        "date": _today(),
        "timestamp": _now(),
        "summary": summary,
        "errors_count": errors_count,
        "findings_count": findings_count,
        "beliefs_changed": beliefs_changed,
        "duration_min": round(duration_min, 1),
    }

    data["sessions"].append(session)
    data["total"] = len(data["sessions"])
    _save(SESSIONS_FILE, data)
    return session


def get_session_history(limit: int = 10) -> dict:
    """Get recent session summaries."""
    data = _load(SESSIONS_FILE, {"sessions": [], "total": 0})
    sessions = data.get("sessions", [])[-limit:]
    return {
        "total": data.get("total", 0),
        "showing": len(sessions),
        "sessions": sessions,
    }


# ═══════════════════════════════════════════════════════════════════
# IMPROVEMENTS TRACKING
# ═══════════════════════════════════════════════════════════════════

def log_improvement(what_improved: str, before: str, after: str,
                    reason: str = "") -> dict:
    """Log something the agent improved on."""
    data = _load(IMPROVEMENTS_FILE, {"improvements": [], "total": 0})

    imp = {
        "id": f"I{len(data['improvements']) + 1:04d}",
        "what": what_improved,
        "before": before,
        "after": after,
        "reason": reason,
        "date": _today(),
        "timestamp": _now(),
    }

    data["improvements"].append(imp)
    data["total"] = len(data["improvements"])
    _save(IMPROVEMENTS_FILE, data)
    return imp


def get_improvements(limit: int = 10) -> dict:
    """Get recent improvements."""
    data = _load(IMPROVEMENTS_FILE, {"improvements": [], "total": 0})
    return {
        "total": data.get("total", 0),
        "improvements": data.get("improvements", [])[-limit:],
    }


# ═══════════════════════════════════════════════════════════════════
# LEARNING SUMMARY
# ═══════════════════════════════════════════════════════════════════

def get_learning_summary() -> dict:
    """Full learning summary: what I've learned, what I keep getting wrong."""
    errors_data = _load(ERRORS_FILE, {"errors": [], "total": 0})
    patterns_data = _load(PATTERNS_FILE, {"patterns": [], "total": 0})
    sessions_data = _load(SESSIONS_FILE, {"sessions": [], "total": 0})
    improvements_data = _load(IMPROVEMENTS_FILE, {"improvements": [], "total": 0})

    errors = errors_data.get("errors", [])
    repeated = [e for e in errors if e.get("times_repeated", 1) >= 2]

    # Category breakdown
    by_category = {}
    for e in errors:
        cat = e.get("category", "other")
        by_category[cat] = by_category.get(cat, 0) + 1

    # Severity breakdown
    by_severity = {}
    for e in errors:
        sev = e.get("severity", "medium")
        by_severity[sev] = by_severity.get(sev, 0) + 1

    return {
        "total_errors_logged": len(errors),
        "repeated_errors": len(repeated),
        "patterns_detected": patterns_data.get("total", 0),
        "sessions_logged": sessions_data.get("total", 0),
        "improvements_logged": improvements_data.get("total", 0),
        "error_categories": by_category,
        "error_severity": by_severity,
        "top_repeated": [
            {"mistake": e["mistake"][:80], "times": e["times_repeated"],
             "fix": e.get("fix", "")[:80]}
            for e in sorted(repeated, key=lambda x: x.get("times_repeated", 0), reverse=True)[:5]
        ],
    }


# ═══════════════════════════════════════════════════════════════════
# PRE-SESSION CHECK
# ═══════════════════════════════════════════════════════════════════

def pre_session_check() -> dict:
    """Check before starting: what should I remember NOT to do?

    Returns: list of anti-patterns to avoid, based on past errors.
    """
    data = _load(ERRORS_FILE, {"errors": [], "total": 0})
    errors = data.get("errors", [])

    # Get repeated errors as anti-patterns
    anti_patterns = []
    for e in errors:
        if e.get("times_repeated", 1) >= 2:
            anti_patterns.append({
                "avoid": e["mistake"],
                "instead": e.get("fix", ""),
                "times_wrong": e["times_repeated"],
                "category": e.get("category", ""),
            })

    anti_patterns.sort(key=lambda x: x["times_wrong"], reverse=True)

    # Get recent patterns
    patterns_data = _load(PATTERNS_FILE, {"patterns": []})
    patterns = patterns_data.get("patterns", [])

    return {
        "anti_patterns": anti_patterns[:10],
        "active_patterns": patterns[:5],
        "reminder": (
            f"You have {len(anti_patterns)} repeated error patterns. "
            f"Check these before proceeding."
            if anti_patterns else
            "No repeated errors detected. Keep learning."
        ),
    }


# ── Helpers ──────────────────────────────────────────────────────

def _similar(a: str, b: str, threshold: float = 0.7) -> bool:
    """Simple string similarity (word overlap)."""
    words_a = set(a.lower().split())
    words_b = set(b.lower().split())
    if not words_a or not words_b:
        return False
    overlap = len(words_a & words_b)
    union = len(words_a | words_b)
    return (overlap / union) >= threshold
