"""sint-historian-mcp — cross-session analyst (fastmcp, stdio).

Analyzes memory blocks and session logs to find patterns,
track progress, and surface insights across sessions.

Integrates with sint-memory and git for full provenance.

Tools:
  session_stats()              — summary of all logged sessions
  recent_sessions(n)           — last N session summaries
  pattern_search(query)        — find recurring patterns in work
  project_timeline(project)    — timeline of a project's blocks
  git_integration_status()     — show memory<->git link health
  work_report(days)            — what was accomplished in N days
  drift_analysis()             — detect topic drift across sessions
  historian_help()             — usage guide

Run: python server.py (stdio)
"""
from __future__ import annotations

import json
import datetime
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

from config import NAME, VERSION, MEMORY_BLOCKS_LIMIT

mcp = FastMCP(NAME)

# ── Memory system integration (via file-based fallback) ──────────────
MEMORY_DIR = Path.home() / ".opencode" / "memory"
STATE_FILE = MEMORY_DIR / "state.json"
BLOCKS_DIR = MEMORY_DIR / "blocks"

# ── Helpers ──────────────────────────────────────────────────────────

def _read_state() -> dict:
    """Read current memory state.json."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {}

def _read_blocks(limit: int = 50) -> list[dict]:
    """Read recent memory blocks from the chain."""
    blocks = []
    if BLOCKS_DIR.exists():
        for f in sorted(BLOCKS_DIR.iterdir(), reverse=True)[:limit]:
            if f.suffix == ".json":
                try:
                    blocks.append(json.loads(f.read_text()))
                except (json.JSONDecodeError, OSError):
                    pass
    return blocks

def _read_sessions() -> list[dict]:
    """Read session log entries."""
    sessions = []
    for f in sorted(MEMORY_DIR.glob("session_*.jsonl"), reverse=True)[:20]:
        try:
            for line in f.read_text().strip().split("\n"):
                if line:
                    sessions.append(json.loads(line))
        except (json.JSONDecodeError, OSError):
            pass
    return sessions


# ═══════════════════════════════════════════════════════════════════
# SESSION ANALYSIS
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def session_stats() -> str:
    """Get summary statistics of all recorded sessions.

    Returns: total sessions, blocks, projects, activity timeline.
    """
    blocks = _read_blocks(200)
    state = _read_state()

    projects = set()
    registers = {}
    for b in blocks:
        p = b.get("project", "UNKNOWN")
        if p != "UNKNOWN":
            projects.add(p)
        r = b.get("register", "SENSE")
        registers[r] = registers.get(r, 0) + 1

    return json.dumps({
        "total_blocks": len(blocks),
        "total_projects": len(projects),
        "projects": sorted(projects),
        "register_distribution": registers,
        "last_session": state.get("last_session", "N/A"),
        "pending_decisions": state.get("pending_decisions", []),
    }, ensure_ascii=False, indent=1)


@mcp.tool()
def recent_sessions(n: int = 5) -> str:
    """Get summaries of the most recent sessions.

    Args:
        n: number of recent sessions to show
    Returns: JSON array of session entries.
    """
    blocks = _read_blocks(100)
    sessions = _read_sessions()

    # Group by date
    by_day = {}
    for b in blocks:
        ts = b.get("timestamp", "")[:10]
        if ts:
            if ts not in by_day:
                by_day[ts] = {"date": ts, "blocks": 0, "projects": set(), "registers": set()}
            by_day[ts]["blocks"] += 1
            by_day[ts]["projects"].add(b.get("project", "?"))
            by_day[ts]["registers"].add(b.get("register", "?"))

    # Sort by date descending
    sorted_days = sorted(by_day.items(), reverse=True)[:n]
    results = []
    for date, info in sorted_days:
        results.append({
            "date": date,
            "blocks": info["blocks"],
            "projects": sorted(info["projects"]),
            "registers": sorted(info["registers"]),
        })

    return json.dumps({
        "recent_sessions": results,
        "raw_session_events": len(sessions),
    }, ensure_ascii=False, indent=1)


@mcp.tool()
def project_timeline(project: str) -> str:
    """Show the timeline of blocks for a specific project.

    Args:
        project: project name (e.g. 'CLEFIA', 'Camellia', 'DSA')
    Returns: JSON timeline of activity.
    """
    blocks = _read_blocks(200)
    timeline = []
    for b in blocks:
        if b.get("project", "").upper() == project.upper():
            timeline.append({
                "id": b.get("id", "?"),
                "register": b.get("register", "?"),
                "timestamp": b.get("timestamp", "?"),
                "summary": b.get("content", "")[:120],
                "tags": b.get("tags", []),
            })

    return json.dumps({
        "project": project,
        "total_blocks": len(timeline),
        "timeline": timeline,
    }, ensure_ascii=False, indent=1)


@mcp.tool()
def pattern_search(query: str) -> str:
    """Search for recurring patterns across sessions.

    Looks for repeated project names, tags, and register usage.

    Args:
        query: keyword to search for in blocks
    Returns: JSON with pattern analysis.
    """
    blocks = _read_blocks(200)
    matches = []
    for b in blocks:
        content = b.get("content", "").lower()
        tags = [t.lower() for t in b.get("tags", [])]
        if query.lower() in content or query.lower() in tags:
            matches.append({
                "id": b.get("id", "?"),
                "register": b.get("register", "?"),
                "project": b.get("project", "?"),
                "timestamp": b.get("timestamp", "?"),
                "snippet": content[:100],
            })

    # Frequency analysis
    projects = {}
    registers = {}
    for m in matches:
        p = m["project"]
        projects[p] = projects.get(p, 0) + 1
        r = m["register"]
        registers[r] = registers.get(r, 0) + 1

    return json.dumps({
        "query": query,
        "total_matches": len(matches),
        "by_project": projects,
        "by_register": registers,
        "matches": matches[:20],  # limit output
    }, ensure_ascii=False, indent=1)


@mcp.tool()
def work_report(days: int = 7) -> str:
    """Generate a work report for the last N days.

    Args:
        days: number of days to look back
    Returns: JSON summary of what was accomplished.
    """
    blocks = _read_blocks(200)
    cutoff = (datetime.datetime.utcnow() -
              datetime.timedelta(days=days)).isoformat()

    recent = [b for b in blocks
              if b.get("timestamp", "") >= cutoff[:19]]

    # Projects touched
    projects = {}
    for b in recent:
        p = b.get("project", "UNKNOWN")
        r = b.get("register", "SENSE")
        if p not in projects:
            projects[p] = {"blocks": 0, "registers": set()}
        projects[p]["blocks"] += 1
        projects[p]["registers"].add(r)

    # Key actions (ACTION register blocks)
    actions = [b for b in recent if b.get("register") == "ACTION"]

    return json.dumps({
        "period_days": days,
        "total_blocks": len(recent),
        "projects_touched": len(projects),
        "per_project": {
            p: {"blocks": v["blocks"],
                "registers": sorted(v["registers"])}
            for p, v in sorted(projects.items(), key=lambda x: -x[1]["blocks"])
        },
        "key_actions": [
            {"id": a.get("id"), "summary": a.get("content", "")[:150],
             "project": a.get("project")}
            for a in actions[-10:]
        ],
    }, ensure_ascii=False, indent=1)


@mcp.tool()
def drift_analysis() -> str:
    """Detect topic drift: how focus shifted across sessions.

    Analyzes project distribution over time to identify
    when and how the work focus changed.
    """
    blocks = _read_blocks(200)

    # Chronological project transitions
    transitions = []
    last_project = None
    for b in reversed(blocks):
        p = b.get("project", "?")
        if p != last_project:
            transitions.append({
                "timestamp": b.get("timestamp", "?"),
                "project": p,
                "register": b.get("register", "?"),
            })
            last_project = p

    # Count shifts
    project_changes = {}
    for t in transitions[1:]:
        prev = transitions[transitions.index(t) - 1]["project"]
        change = f"{prev} → {t['project']}"
        project_changes[change] = project_changes.get(change, 0) + 1

    return json.dumps({
        "total_transitions": len(transitions),
        "project_flow": transitions[:30],  # show recent flow
        "common_shifts": dict(sorted(
            project_changes.items(), key=lambda x: -x[1]
        )[:10]),
        "current_focus": transitions[-1]["project"] if transitions else "N/A",
    }, ensure_ascii=False, indent=1)


@mcp.tool()
def historian_help() -> str:
    """Get usage guide for sint-historian-mcp."""
    return json.dumps({
        "description": "sint-historian-mcp — Cross-session work analyst",
        "tools": {
            "session_stats": "session_stats() — overall stats",
            "recent_sessions": "recent_sessions(5) — last 5 sessions",
            "project_timeline": "project_timeline('CLEFIA') — project history",
            "pattern_search": "pattern_search('crypto') — search blocks",
            "work_report": "work_report(7) — weekly report",
            "drift_analysis": "drift_analysis() — topic drift",
        },
        "examples": [
            "See what we did this week: work_report(7)",
            "Check CLEFIA timeline: project_timeline('CLEFIA')",
            "Detect drift: drift_analysis()",
        ],
    }, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    mcp.run(transport="stdio")
