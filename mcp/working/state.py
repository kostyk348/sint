"""Working memory state management.

Maintains structured JSON state files that live on disk,
not in the context window. Agent reads them on demand.
"""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import (
    TASK_FILE, FINDINGS_FILE, BELIEFS_FILE, OPEN_FILE, SESSION_LOG,
    CONFIDENCE_HIGH, CONFIDENCE_MEDIUM, CONFIDENCE_LOW,
)


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _load(path: Path, default: Any = None) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return default if default is not None else {}


def _save(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _new_id(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"


# ═══════════════════════════════════════════════════════════════════
# TASK STATE
# ═══════════════════════════════════════════════════════════════════

def get_task() -> dict:
    """Get current task state."""
    return _load(TASK_FILE, {
        "objective": "",
        "status": "idle",
        "checked": [],
        "findings_summary": "",
        "next_step": "",
        "blocked_on": [],
        "started": "",
        "messages_since_update": 0,
    })


def update_task(objective: str = "", status: str = "", next_step: str = "",
                blocked_on: List[str] = None, add_checked: str = "") -> dict:
    """Update task state. Only non-empty fields are updated."""
    task = get_task()

    if objective:
        task["objective"] = objective
        task["started"] = task.get("started") or _now()
    if status:
        task["status"] = status
    if next_step:
        task["next_step"] = next_step
    if blocked_on is not None:
        task["blocked_on"] = blocked_on
    if add_checked:
        if add_checked not in task["checked"]:
            task["checked"].append(add_checked)

    task["messages_since_update"] = 0
    task["last_updated"] = _now()
    _save(TASK_FILE, task)
    return task


def increment_messages():
    """Increment message counter (called on each agent response)."""
    task = get_task()
    task["messages_since_update"] = task.get("messages_since_update", 0) + 1
    _save(TASK_FILE, task)
    return task["messages_since_update"]


def get_compression_pressure() -> dict:
    """Check if compression is needed."""
    task = get_task()
    count = task.get("messages_since_update", 0)
    return {
        "messages_since_update": count,
        "needs_compression": count >= 15,
        "recommendation": (
            "Time to compress: update task.json, findings.json, beliefs.json"
            if count >= 15
            else f"{15 - count} messages until compression recommended"
        ),
    }


# ═══════════════════════════════════════════════════════════════════
# FINDINGS
# ═══════════════════════════════════════════════════════════════════

def get_findings() -> dict:
    """Get all findings."""
    return _load(FINDINGS_FILE, {"items": [], "total": 0})


def add_finding(claim: str, source: str, confidence: float = 0.8,
                tags: List[str] = None) -> dict:
    """Add a finding (key discovery)."""
    data = get_findings()
    fid = f"F{len(data['items']) + 1:03d}"

    finding = {
        "id": fid,
        "claim": claim,
        "source": source,
        "confidence": round(confidence, 2),
        "tags": tags or [],
        "timestamp": _now(),
        "status": "active",
    }

    data["items"].append(finding)
    data["total"] = len(data["items"])
    _save(FINDINGS_FILE, data)
    return finding


def revise_finding(finding_id: str, new_claim: str = "",
                   new_confidence: float = None,
                   new_status: str = "") -> dict:
    """Revise a finding."""
    data = get_findings()
    for item in data["items"]:
        if item["id"] == finding_id:
            if new_claim:
                item["claim"] = new_claim
            if new_confidence is not None:
                item["confidence"] = round(new_confidence, 2)
            if new_status:
                item["status"] = new_status
            item["revised"] = _now()
            item["revision_history"] = item.get("revision_history", [])
            item["revision_history"].append({
                "timestamp": _now(),
                "old_claim": item.get("claim", ""),
                "old_confidence": item.get("confidence", 0),
            })
            _save(FINDINGS_FILE, data)
            return item
    return {"error": f"finding '{finding_id}' not found"}


# ═══════════════════════════════════════════════════════════════════
# BELIEFS (Epistemic)
# ═══════════════════════════════════════════════════════════════════

def get_beliefs() -> dict:
    """Get all beliefs."""
    return _load(BELIEFS_FILE, {"beliefs": [], "total": 0})


def add_belief(statement: str, confidence: float, evidence_ids: List[str] = None,
               reasoning: str = "") -> dict:
    """Add a belief with confidence level."""
    data = get_beliefs()
    bid = f"B{len(data['beliefs']) + 1:03d}"

    # Classify confidence
    if confidence >= CONFIDENCE_HIGH:
        tier = "high"
    elif confidence >= CONFIDENCE_MEDIUM:
        tier = "medium"
    elif confidence >= CONFIDENCE_LOW:
        tier = "low"
    else:
        tier = "speculative"

    belief = {
        "id": bid,
        "statement": statement,
        "confidence": round(confidence, 2),
        "confidence_tier": tier,
        "evidence": evidence_ids or [],
        "reasoning": reasoning,
        "status": "active",
        "created": _now(),
        "last_verified": _now(),
        "contradictions": [],
        "revisions": [],
    }

    data["beliefs"].append(belief)
    data["total"] = len(data["beliefs"])
    _save(BELIEFS_FILE, data)
    return belief


def revise_belief(belief_id: str, new_confidence: float = None,
                  reason: str = "") -> dict:
    """Revise belief confidence (belief revision)."""
    data = get_beliefs()
    for b in data["beliefs"]:
        if b["id"] == belief_id:
            old_conf = b["confidence"]
            if new_confidence is not None:
                b["confidence"] = round(new_confidence, 2)
                # Update tier
                if new_confidence >= CONFIDENCE_HIGH:
                    b["confidence_tier"] = "high"
                elif new_confidence >= CONFIDENCE_MEDIUM:
                    b["confidence_tier"] = "medium"
                elif new_confidence >= CONFIDENCE_LOW:
                    b["confidence_tier"] = "low"
                else:
                    b["confidence_tier"] = "speculative"

            b["revisions"].append({
                "timestamp": _now(),
                "old_confidence": old_conf,
                "new_confidence": b["confidence"],
                "reason": reason,
            })
            b["last_verified"] = _now()
            _save(BELIEFS_FILE, data)
            return b
    return {"error": f"belief '{belief_id}' not found"}


def contradict(belief_id_a: str, belief_id_b: str, reason: str = "") -> dict:
    """Flag two beliefs as contradictory."""
    data = get_beliefs()
    a, b = None, None
    for belief in data["beliefs"]:
        if belief["id"] == belief_id_a:
            a = belief
        if belief["id"] == belief_id_b:
            b = belief

    if not a or not b:
        return {"error": "one or both beliefs not found"}

    contradiction = {
        "timestamp": _now(),
        "reason": reason,
        "belief_a": belief_id_a,
        "belief_b": belief_id_b,
    }

    a.setdefault("contradictions", []).append(contradiction)
    b.setdefault("contradictions", []).append(contradiction)

    # Lower confidence on both (contradiction = uncertainty)
    a["confidence"] = round(max(a["confidence"] - 0.2, 0.0), 2)
    b["confidence"] = round(max(b["confidence"] - 0.2, 0.0), 2)

    _save(BELIEFS_FILE, data)
    return {
        "contradiction_flagged": True,
        "belief_a": {"id": a["id"], "new_confidence": a["confidence"]},
        "belief_b": {"id": b["id"], "new_confidence": b["confidence"]},
        "reason": reason,
    }


def get_weakest_beliefs(n: int = 5) -> List[dict]:
    """Get the N weakest beliefs (lowest confidence)."""
    data = get_beliefs()
    sorted_beliefs = sorted(data["beliefs"], key=lambda b: b["confidence"])
    return sorted_beliefs[:n]


def get_epistemic_summary() -> dict:
    """Summary of epistemic state."""
    data = get_beliefs()
    beliefs = data.get("beliefs", [])

    by_tier = {"high": 0, "medium": 0, "low": 0, "speculative": 0}
    for b in beliefs:
        tier = b.get("confidence_tier", "speculative")
        by_tier[tier] = by_tier.get(tier, 0) + 1

    total_contradictions = sum(
        len(b.get("contradictions", [])) for b in beliefs
    )

    return {
        "total_beliefs": len(beliefs),
        "by_tier": by_tier,
        "total_contradictions": total_contradictions,
        "needs_review": [
            b for b in beliefs
            if b.get("contradictions") or b["confidence"] < CONFIDENCE_LOW
        ],
    }


# ═══════════════════════════════════════════════════════════════════
# OPEN QUESTIONS
# ═══════════════════════════════════════════════════════════════════

def get_open_questions() -> dict:
    """Get all open questions."""
    return _load(OPEN_FILE, {"questions": [], "total": 0})


def add_question(question: str, priority: str = "medium",
                 context: str = "") -> dict:
    """Add an open question."""
    data = get_open_questions()
    qid = f"Q{len(data['questions']) + 1:03d}"

    q = {
        "id": qid,
        "question": question,
        "priority": priority,
        "context": context,
        "status": "unanswered",
        "created": _now(),
        "answered": None,
        "answer": "",
    }

    data["questions"].append(q)
    data["total"] = len(data["questions"])
    _save(OPEN_FILE, data)
    return q


def answer_question(question_id: str, answer: str,
                    source: str = "") -> dict:
    """Mark a question as answered."""
    data = get_open_questions()
    for q in data["questions"]:
        if q["id"] == question_id:
            q["status"] = "answered"
            q["answer"] = answer
            q["answer_source"] = source
            q["answered"] = _now()
            _save(OPEN_FILE, data)
            return q
    return {"error": f"question '{question_id}' not found"}


# ═══════════════════════════════════════════════════════════════════
# FULL STATE
# ═══════════════════════════════════════════════════════════════════

def get_full_state() -> dict:
    """Get complete working memory state (compact)."""
    task = get_task()
    findings = get_findings()
    beliefs = get_beliefs()
    questions = get_open_questions()
    epistemic = get_epistemic_summary()

    return {
        "task": {
            "objective": task.get("objective", ""),
            "status": task.get("status", "idle"),
            "checked_count": len(task.get("checked", [])),
            "next_step": task.get("next_step", ""),
            "blocked_on": task.get("blocked_on", []),
        },
        "findings": {
            "total": findings.get("total", 0),
            "top_3": [
                {"claim": f["claim"][:100], "confidence": f["confidence"]}
                for f in findings.get("items", [])[-3:]
            ],
        },
        "beliefs": {
            "total": beliefs.get("total", 0),
            "by_tier": epistemic.get("by_tier", {}),
            "weakest": [
                {"statement": b["statement"][:80], "confidence": b["confidence"]}
                for b in get_weakest_beliefs(3)
            ],
        },
        "open_questions": {
            "total": questions.get("total", 0),
            "unanswered": [
                {"question": q["question"][:100], "priority": q["priority"]}
                for q in questions.get("questions", [])
                if q["status"] == "unanswered"
            ][:5],
        },
        "compression_pressure": get_compression_pressure(),
        "token_estimate": _estimate_tokens(task, findings, beliefs, questions),
    }


def _estimate_tokens(task, findings, beliefs, questions) -> int:
    """Rough token estimate of full state."""
    # ~4 chars per token for JSON
    total_chars = 0
    for data in [task, findings, beliefs, questions]:
        total_chars += len(json.dumps(data, ensure_ascii=False))
    return total_chars // 4


def reset_session():
    """Reset all working memory for a new session."""
    for f in [TASK_FILE, FINDINGS_FILE, BELIEFS_FILE, OPEN_FILE]:
        if f.exists():
            f.unlink()
    return {"status": "reset", "files_cleared": 4}
