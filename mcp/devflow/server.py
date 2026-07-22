"""sint-devflow-mcp server (fastmcp, stdio).

Development workflow intelligence: pipeline planning, coding style,
commit conventions, edge case discovery, and TDD guidance.

Not a linter. A KNOWLEDGE BASE + PLANNER that helps the agent
write code like a senior developer: iterative, tested, documented.

Tools:
  plan_pipeline(title, tasks)    — break feature into verified steps
  get_next_step(pipeline_id)     — get next actionable step
  update_step(pipeline_id, step_id, status) — mark step done/failed
  get_style(language)            — coding style rules
  review_code(code, language)    — check anti-patterns + style
  get_commit_conventions()       — commit message rules
  suggest_commit(type, scope, desc) — generate conventional commit
  edge_cases(description)        — systematic edge case discovery
  tdd_guide(task)                — TDD workflow for a task

Run: python server.py (stdio)
"""
from __future__ import annotations

import json
from pathlib import Path

from fastmcp import FastMCP

from config import NAME
from pipeline import (
    plan_pipeline, pipeline_to_dict, get_next_step,
    Pipeline, StepStatus,
)
from style.registry import registry
from style.base import LanguageStyle
from commit import get_commit_conventions, suggest_commit_message

mcp = FastMCP(NAME)

# ── Active pipelines store ──────────────────────────────────────────
_pipelines: dict[str, Pipeline] = {}


# ═══════════════════════════════════════════════════════════════════
# PIPELINE PLANNING
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def plan_feature(title: str, tasks: list[str], description: str = "") -> str:
    """Plan a feature as an iterative pipeline with verification.

    Each task becomes a step with:
    - Verification criteria
    - TDD recommendation (test-first or test-after)
    - Suggested commit message (conventional commits)
    - Edge cases to consider
    - Dependencies on previous steps

    Args:
        title: feature name (e.g. "ECHONET Lite parser")
        tasks: ordered list of implementation tasks
        description: optional context
    Returns: JSON pipeline with all steps planned.
    """
    pipe = plan_pipeline(title, description or title, tasks)
    _pipelines[pipe.id] = pipe
    result = pipeline_to_dict(pipe)

    # Add next-step recommendation
    nxt = get_next_step(pipe)
    result["next_step"] = nxt
    result["tip"] = "Start with the test file. Write failing tests first (TDD)."

    return json.dumps(result, ensure_ascii=False, indent=1)


@mcp.tool()
def get_next_action(pipeline_id: str) -> str:
    """Get the next actionable step in a pipeline.

    Returns the first pending step whose dependencies are all done,
    with its verification criteria, edge cases, and commit suggestion.
    """
    pipe = _pipelines.get(pipeline_id)
    if not pipe:
        return json.dumps({"error": f"pipeline '{pipeline_id}' not found"})

    nxt = get_next_step(pipe)
    if not nxt:
        return json.dumps({"status": "all_done", "pipeline": pipe.title,
                           "completed": sum(1 for s in pipe.steps
                                          if s.status == StepStatus.DONE)})
    return json.dumps(nxt, ensure_ascii=False, indent=1)


@mcp.tool()
def update_step(pipeline_id: str, step_id: str, status: str,
                notes: str = "") -> str:
    """Update a step's status (pending|in_progress|done|failed|blocked).

    Args:
        pipeline_id: pipeline ID
        step_id: step ID (e.g. "s01")
        status: new status
        notes: optional notes about what was done
    """
    pipe = _pipelines.get(pipeline_id)
    if not pipe:
        return json.dumps({"error": f"pipeline '{pipeline_id}' not found"})

    for s in pipe.steps:
        if s.id == step_id:
            try:
                s.status = StepStatus(status)
            except ValueError:
                return json.dumps({"error": f"invalid status '{status}'"})
            if notes:
                s.notes = notes
            nxt = get_next_step(pipe)
            return json.dumps({
                "updated": step_id, "status": status,
                "next_step": nxt,
                "progress": f"{sum(1 for s in pipe.steps if s.status == StepStatus.DONE)}/{len(pipe.steps)}",
            }, ensure_ascii=False, indent=1)

    return json.dumps({"error": f"step '{step_id}' not found"})


# ═══════════════════════════════════════════════════════════════════
# CODING STYLE
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def get_style_rules(language: str) -> str:
    """Get coding style rules for a language.

    Includes: naming conventions, indentation, line length,
    anti-patterns, and project-specific rules.
    """
    style = registry.get(language)
    if not style:
        available = registry.list_languages()
        return json.dumps({"error": f"no style for '{language}'",
                           "available": available})
    return json.dumps(style.get_config(), ensure_ascii=False, indent=1)


@mcp.tool()
def code_review(code: str, language: str = "python") -> str:
    """Review code for style violations and anti-patterns.

    Checks: naming conventions, line length, known anti-patterns,
    TODO/FIXME comments, and provides a quality score.
    """
    style = registry.get(language)
    if not style:
        available = registry.list_languages()
        return json.dumps({"error": f"no style for '{language}'",
                           "available": available})
    result = style.review_code(code)
    return json.dumps(result, ensure_ascii=False, indent=1)


@mcp.tool()
def list_languages() -> str:
    """List all registered language style plugins."""
    langs = registry.list_all()
    return json.dumps({"languages": langs, "total": len(langs)},
                      ensure_ascii=False, indent=1)


# ═══════════════════════════════════════════════════════════════════
# COMMIT CONVENTIONS
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def commit_conventions() -> str:
    """Get commit message conventions (Conventional Commits)."""
    return json.dumps(get_commit_conventions(), ensure_ascii=False, indent=1)


@mcp.tool()
def make_commit_message(change_type: str, scope: str, description: str) -> str:
    """Generate a conventional commit message.

    Args:
        change_type: feat|fix|docs|style|refactor|test|chore|perf|revert
        scope: module or component name (optional)
        description: what changed, imperative mood, lowercase
    Returns: formatted commit message.
    """
    msg = suggest_commit_message(change_type, scope, description)
    return json.dumps({"message": msg, "type": change_type,
                       "scope": scope}, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════════
# EDGE CASES
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def discover_edge_cases(description: str) -> str:
    """Systematically discover edge cases for a feature/function.

    Analyzes the description and suggests edge cases across categories:
    - Input boundaries (empty, null, oversized)
    - State transitions (concurrent, interrupted, partial)
    - Error conditions (network, file, permission)
    - Security (injection, overflow, replay)
    - Performance (large data, rapid calls, memory pressure)
    """
    cases = _systematic_edge_cases(description)
    return json.dumps({"feature": description, "edge_cases": cases,
                       "total": len(cases)}, ensure_ascii=False, indent=1)


def _systematic_edge_cases(description: str) -> list:
    """Generate systematic edge cases based on feature analysis."""
    d = description.lower()
    cases = []

    # Universal cases
    cases.extend([
        {"category": "input", "case": "empty input", "test": "pass empty string/bytes/null"},
        {"category": "input", "case": "null/None values", "test": "pass None where object expected"},
        {"category": "input", "case": "very large input (>1MB)", "test": "pass 10MB buffer"},
        {"category": "input", "case": "unicode/binary混合", "test": "pass mixed encoding"},
    ])

    # Domain-specific
    if any(kw in d for kw in ["parse", "extract", "decode"]):
        cases.extend([
            {"category": "malformed", "case": "truncated data", "test": "cut input at 50%"},
            {"category": "malformed", "case": "wrong magic bytes", "test": "corrupt header"},
            {"category": "malformed", "case": "valid but unexpected structure", "test": "valid JSON in binary format"},
        ])

    if any(kw in d for kw in ["network", "socket", "http", "recv", "send"]):
        cases.extend([
            {"category": "network", "case": "connection refused", "test": "target port closed"},
            {"category": "network", "case": "timeout", "test": "no response for 30s"},
            {"category": "network", "case": "partial recv", "test": "receive half the expected data"},
            {"category": "network", "case": "connection reset mid-transfer", "test": "kill connection after 50% data"},
        ])

    if any(kw in d for kw in ["file", "read", "write", "io", "open"]):
        cases.extend([
            {"category": "filesystem", "case": "file not found", "test": "delete file before read"},
            {"category": "filesystem", "case": "permission denied", "test": "chmod 000 the file"},
            {"category": "filesystem", "case": "disk full", "test": "fill disk, then write"},
            {"category": "filesystem", "case": "symlink loop", "test": "create A→B→A"},
        ])

    if any(kw in d for kw in ["graph", "node", "edge", "link"]):
        cases.extend([
            {"category": "graph", "case": "single node", "test": "graph with one node, no edges"},
            {"category": "graph", "case": "cyclic references", "test": "A→B→C→A"},
            {"category": "graph", "case": "orphan nodes", "test": "node with no edges"},
            {"category": "graph", "case": "self-loop", "test": "node→node"},
        ])

    if any(kw in d for kw in ["crypto", "encrypt", "decrypt", "hash", "key"]):
        cases.extend([
            {"category": "security", "case": "wrong key", "test": "decrypt with different key"},
            {"category": "security", "case": "truncated ciphertext", "test": "cut ciphertext at 75%"},
            {"category": "security", "case": "replay attack", "test": "resend captured packet"},
            {"category": "security", "case": "timing side-channel", "test": "measure response time variations"},
        ])

    if any(kw in d for kw in ["embed", "vector", "similarity"]):
        cases.extend([
            {"category": "semantic", "case": "empty embedding", "test": "embed empty string"},
            {"category": "semantic", "case": "near-identical queries", "test": "embed 'abc' and 'abd'"},
            {"category": "semantic", "case": "cross-language equivalence", "test": "embed same meaning in EN vs RU"},
        ])

    if any(kw in d for kw in ["concurrent", "thread", "lock", "async"]):
        cases.extend([
            {"category": "concurrency", "case": "race condition", "test": "100 threads, same resource"},
            {"category": "concurrency", "case": "deadlock", "test": "two locks, opposite order"},
            {"category": "concurrency", "case": "resource exhaustion", "test": "10000 open connections"},
        ])

    return cases


# ═══════════════════════════════════════════════════════════════════
# TDD GUIDE
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def tdd_guide(task: str) -> str:
    """Generate a TDD workflow guide for a specific task.

    Returns: test file structure, first failing test, and
    implementation steps following Red→Green→Refactor.
    """
    d = task.lower()

    # Choose test framework
    if any(kw in d for kw in ["c", "embedded", "mcu", "rtos"]):
        framework = "CUnit / Unity / custom assert"
        ext = ".c"
        runner = "gcc -o test_x test_x.c && ./test_x"
    else:
        framework = "pytest"
        ext = ".py"
        runner = "pytest test_x.py -v"

    guide = {
        "task": task,
        "framework": framework,
        "runner": runner,
        "workflow": [
            "1. RED: Write a failing test that defines expected behavior",
            "2. GREEN: Write minimal code to make the test pass",
            "3. REFACTOR: Clean up without changing behavior",
            "4. REPEAT: Add next test case",
        ],
        "first_test_template": _first_test_template(task, ext),
        "test_cases_to_write": _suggest_test_cases(task),
    }

    return json.dumps(guide, ensure_ascii=False, indent=1)


def _first_test_template(task: str, ext: str) -> str:
    d = task.lower()
    if ext == ".py":
        return f'''import pytest

def test_{task.replace(" ", "_").lower().replace("-", "_")}():
    """Test that {task} works correctly."""
    # Arrange
    input_data = b"test input"
    
    # Act
    result = process(input_data)
    
    # Assert
    assert result is not None
    assert len(result) > 0


def test_{task.replace(" ", "_").lower().replace("-", "_")}_empty_input():
    """Test {task} with empty input."""
    result = process(b"")
    assert result is not None  # or assert raises
'''
    else:
        return f'''#include <assert.h>

void test_{task.replace(" ", "_").lower().replace("-", "_")}(void) {{
    /* Test that {task} works correctly */
    const uint8_t input[] = {{0x01, 0x02, 0x03}};
    uint8_t output[64];
    
    int ret = process(input, sizeof(input), output, sizeof(output));
    assert(ret > 0);
}}

void test_{task.replace(" ", "_").lower().replace("-", "_")}_edge(void) {{
    /* Edge case: empty input */
    int ret = process(NULL, 0, NULL, 0);
    assert(ret < 0);  /* should fail gracefully */
}}
'''


def _suggest_test_cases(task: str) -> list:
    d = task.lower()
    cases = [
        "happy path — normal input, expected output",
        "empty input — should handle gracefully",
        "boundary — minimum/maximum size",
        "error condition — invalid input, check error return",
    ]

    if "parse" in d:
        cases.extend([
            "truncated input — partial data",
            "malformed input — corrupted structure",
        ])
    if "crypto" in d or "encrypt" in d:
        cases.extend([
            "known test vector — RFC NIST reference",
            "wrong key — should fail or produce different output",
        ])
    if "graph" in d:
        cases.extend([
            "single node — no edges",
            "circular — cycle detection",
        ])
    if "embed" in d or "vector" in d:
        cases.extend([
            "identical inputs — same embedding",
            "different inputs — different embeddings",
        ])

    return cases


if __name__ == "__main__":
    mcp.run(transport="stdio")
