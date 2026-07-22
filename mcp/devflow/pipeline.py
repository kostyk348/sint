"""Pipeline planner — break tasks into verified steps.

Inspired by TDD and iterative development:
- Every step has a clear input, output, and verification
- Steps are atomic enough to be done in one commit
- Tests come before (or with) implementation
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional


class StepStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class Step:
    id: str
    title: str
    description: str
    status: StepStatus = StepStatus.PENDING
    depends_on: List[str] = field(default_factory=list)
    verification: str = ""  # how to verify this step is done
    test_first: bool = False  # write test before implementation?
    commit_message: str = ""  # suggested commit message
    edge_cases: List[str] = field(default_factory=list)
    files_affected: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class Pipeline:
    id: str
    title: str
    description: str
    steps: List[Step] = field(default_factory=list)
    created: str = ""
    status: str = "active"


def plan_pipeline(title: str, description: str, tasks: List[str]) -> Pipeline:
    """Break a feature/task description into an iterative pipeline.

    Each task becomes a step with:
    - Verification criteria
    - TDD recommendation
    - Suggested commit message
    - Edge cases to consider
    """
    pipeline = Pipeline(
        id=f"pipe_{int(time.time())}",
        title=title,
        description=description,
        created=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )

    for i, task in enumerate(tasks):
        step = Step(
            id=f"s{i+1:02d}",
            title=task,
            description=f"Implement: {task}",
            verification=_suggest_verification(task),
            test_first=_should_test_first(task),
            commit_message=_suggest_commit(task, i + 1),
            edge_cases=_suggest_edge_cases(task),
        )
        # Dependency: each step depends on previous
        if i > 0:
            step.depends_on = [f"s{i:02d}"]
        pipeline.steps.append(step)

    return pipeline


def pipeline_to_dict(pipe: Pipeline) -> dict:
    return {
        "id": pipe.id,
        "title": pipe.title,
        "description": pipe.description,
        "created": pipe.created,
        "status": pipe.status,
        "total_steps": len(pipe.steps),
        "steps": [
            {
                "id": s.id,
                "title": s.title,
                "status": s.status.value,
                "depends_on": s.depends_on,
                "verification": s.verification,
                "test_first": s.test_first,
                "commit_message": s.commit_message,
                "edge_cases": s.edge_cases,
                "files_affected": s.files_affected,
                "notes": s.notes,
            }
            for s in pipe.steps
        ],
    }


def get_next_step(pipe: Pipeline) -> Optional[dict]:
    """Get the next actionable step (first pending without unmet dependencies)."""
    done_ids = {s.id for s in pipe.steps if s.status == StepStatus.DONE}
    for s in pipe.steps:
        if s.status != StepStatus.PENDING:
            continue
        if all(dep in done_ids for dep in s.depends_on):
            return {
                "id": s.id,
                "title": s.title,
                "description": s.description,
                "verification": s.verification,
                "test_first": s.test_first,
                "commit_message": s.commit_message,
                "edge_cases": s.edge_cases,
            }
    return None


# ── Suggestion heuristics ──────────────────────────────────────────

def _suggest_verification(task: str) -> str:
    """Suggest verification criteria based on task type."""
    t = task.lower()
    if "test" in t or "spec" in t:
        return "Run test suite, all green"
    if "config" in t or "setup" in t:
        return "Load config, verify all fields parsed correctly"
    if "api" in t or "endpoint" in t:
        return "Call endpoint, verify response schema + status code"
    if "parser" in t or "extract" in t:
        return "Parse sample input, compare output to expected"
    if "graph" in t or "node" in t:
        return "Build graph from test data, verify node/edge counts"
    if "embed" in t or "vector" in t:
        return "Embed test strings, verify dimension + cosine similarity"
    if "cache" in t or "persist" in t:
        return "Save → load → compare, verify roundtrip integrity"
    if "detect" in t or "pattern" in t:
        return "Run against known samples, verify detection rate > 90%"
    return "Manual review + integration test"


def _should_test_first(task: str) -> bool:
    """Decide if TDD is recommended for this task."""
    t = task.lower()
    # Core logic should be test-first
    if any(kw in t for kw in ["core", "engine", "parser", "algorithm",
                               "detect", "trace", "taint", "encrypt"]):
        return True
    # Infrastructure can be test-after
    if any(kw in t for kw in ["config", "setup", "readme", "doc"]):
        return False
    return True  # default: test-first


def _suggest_commit(task: str, step_num: int) -> str:
    """Suggest a conventional commit message."""
    t = task.lower()
    if "test" in t:
        return f"test: {task.lower()}"
    if "config" in t or "setup" in t:
        return f"chore: {task.lower()}"
    if "doc" in t or "readme" in t:
        return f"docs: {task.lower()}"
    if "fix" in t or "bug" in t:
        return f"fix: {task.lower()}"
    if "refactor" in t:
        return f"refactor: {task.lower()}"
    return f"feat: {task.lower()}"


def _suggest_edge_cases(task: str) -> List[str]:
    """Suggest edge cases to consider."""
    cases = ["empty input", "null/nil values", "very large input"]
    t = task.lower()
    if "parse" in t or "extract" in t:
        cases.extend(["malformed input", "partial data", "encoding issues"])
    if "graph" in t or "node" in t:
        cases.extend(["single node graph", "circular references", "orphan nodes"])
    if "network" in t or "socket" in t:
        cases.extend(["connection refused", "timeout", "partial read"])
    if "file" in t or "io" in t:
        cases.extend(["file not found", "permission denied", "disk full"])
    if "crypto" in t or "encrypt" in t:
        cases.extend(["wrong key", "truncated ciphertext", "replay attack"])
    return cases
