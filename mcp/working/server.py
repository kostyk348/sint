"""sint-working-mcp server (fastmcp, stdio).

Working Memory + Epistemic State for the sint agent.

Structured task state, findings, beliefs, and open questions
that live on DISK, not in the context window.

Agent reads them on demand (1 tool call = ~200 tokens)
instead of keeping full history in context.

Tools:
  get_state()                     — full compact state snapshot
  update_task(...)                — update current task
  add_finding(claim, source)      — record key discovery
  revise_finding(id, ...)         — update a finding
  add_belief(statement, confidence) — register belief with confidence
  revise_belief(id, confidence)   — belief revision
  contradict(a, b)                — flag contradictory beliefs
  add_question(question)          — add open question
  answer_question(id, answer)     — close a question
  get_epistemic_summary()         — beliefs overview
  get_weakest_beliefs()           — what I'm least sure about
  compression_check()             — should I compress now?
  reset_session()                 — clear for new session

Run: python server.py (stdio)
"""
from __future__ import annotations

import json

from fastmcp import FastMCP

from config import NAME
from state import (
    get_task, update_task, increment_messages, get_compression_pressure,
    get_findings, add_finding, revise_finding,
    get_beliefs, add_belief, revise_belief, contradict,
    get_weakest_beliefs, get_epistemic_summary,
    get_open_questions, add_question, answer_question,
    get_full_state, reset_session,
)

mcp = FastMCP(NAME)


# ═══════════════════════════════════════════════════════════════════
# FULL STATE
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def get_state() -> str:
    """Get full working memory state (compact, ~400 tokens).

    Returns: task status, top findings, beliefs by tier,
    open questions, and compression pressure.
    Use this to restore context after a long conversation.
    """
    state = get_full_state()
    return json.dumps(state, ensure_ascii=False, indent=1)


# ═══════════════════════════════════════════════════════════════════
# TASK STATE
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def update_task(objective: str = "", status: str = "",
                next_step: str = "", blocked_on: list = None,
                add_checked: str = "") -> str:
    """Update current task state.

    Args:
        objective: what we're trying to do
        status: idle|in_progress|blocked|done
        next_step: what to do next
        blocked_on: list of blockers
        add_checked: add an item to "already checked" list
    """
    task = update_task(
        objective=objective, status=status, next_step=next_step,
        blocked_on=blocked_on, add_checked=add_checked,
    )
    return json.dumps(task, ensure_ascii=False, indent=1)


@mcp.tool()
def task_checkin(what_checked: str, what_found: str,
                 next_step: str = "") -> str:
    """Quick task checkin: what I just checked and what I found.

    Convenience method that updates task + adds finding in one call.
    Use this every few messages to keep state fresh.
    """
    # Update task
    update_task(add_checked=what_checked, next_step=next_step)

    # Add finding
    finding = None
    if what_found:
        finding = add_finding(claim=what_found, source=what_checked)

    task = get_task()
    result = {
        "task_status": task.get("status", ""),
        "checked_count": len(task.get("checked", [])),
        "next_step": task.get("next_step", ""),
    }
    if finding:
        result["new_finding"] = finding["id"]

    return json.dumps(result, ensure_ascii=False, indent=1)


# ═══════════════════════════════════════════════════════════════════
# FINDINGS
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def add_finding_tool(claim: str, source: str, confidence: float = 0.8,
                     tags: list = None) -> str:
    """Record a key finding (discovery).

    Args:
        claim: what was found (statement)
        source: where it came from (tool, search, spec, etc.)
        confidence: 0.0-1.0
        tags: optional categorization tags
    Returns: finding with ID.
    """
    f = add_finding(claim=claim, source=source,
                    confidence=confidence, tags=tags or [])
    return json.dumps(f, ensure_ascii=False, indent=1)


@mcp.tool()
def revise_finding_tool(finding_id: str, new_claim: str = "",
                        new_confidence: float = None,
                        new_status: str = "") -> str:
    """Revise a finding with new information."""
    result = revise_finding(finding_id, new_claim=new_claim,
                           new_confidence=new_confidence,
                           new_status=new_status)
    return json.dumps(result, ensure_ascii=False, indent=1)


@mcp.tool()
def list_findings(limit: int = 10) -> str:
    """List recent findings."""
    data = get_findings()
    items = data.get("items", [])[-limit:]
    return json.dumps({
        "total": data.get("total", 0),
        "showing": len(items),
        "findings": items,
    }, ensure_ascii=False, indent=1)


# ═══════════════════════════════════════════════════════════════════
# BELIEFS (Epistemic)
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def add_belief_tool(statement: str, confidence: float,
                    evidence_ids: list = None,
                    reasoning: str = "") -> str:
    """Register a belief with confidence level.

    Args:
        statement: what I believe
        confidence: 0.0-1.0 (0.85+ = high, 0.6+ = medium, below = low/speculative)
        evidence_ids: list of finding IDs that support this
        reasoning: why I believe this
    Returns: belief with ID and confidence tier.
    """
    b = add_belief(statement=statement, confidence=confidence,
                   evidence_ids=evidence_ids or [], reasoning=reasoning)
    return json.dumps(b, ensure_ascii=False, indent=1)


@mcp.tool()
def revise_belief_tool(belief_id: str, new_confidence: float,
                       reason: str = "") -> str:
    """Revise belief confidence (belief revision).

    Use when new evidence changes how confident you are.
    """
    result = revise_belief(belief_id, new_confidence=new_confidence,
                          reason=reason)
    return json.dumps(result, ensure_ascii=False, indent=1)


@mcp.tool()
def contradict_beliefs(belief_id_a: str, belief_id_b: str,
                       reason: str = "") -> str:
    """Flag two beliefs as contradictory.

    Both beliefs will have confidence reduced by 0.2.
    Use when you find evidence that conflicts with an existing belief.
    """
    result = contradict(belief_id_a, belief_id_b, reason=reason)
    return json.dumps(result, ensure_ascii=False, indent=1)


@mcp.tool()
def get_epistemic() -> str:
    """Get epistemic summary: beliefs by tier, contradictions, needs review."""
    return json.dumps(get_epistemic_summary(), ensure_ascii=False, indent=1)


@mcp.tool()
def get_uncertain() -> str:
    """Get weakest beliefs — what I'm least sure about.

    Use this to identify areas needing more evidence.
    """
    weakest = get_weakest_beliefs(5)
    return json.dumps({
        "weakest_beliefs": [
            {"id": b["id"], "statement": b["statement"][:100],
             "confidence": b["confidence"], "tier": b["confidence_tier"]}
            for b in weakest
        ],
    }, ensure_ascii=False, indent=1)


# ═══════════════════════════════════════════════════════════════════
# OPEN QUESTIONS
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def add_question_tool(question: str, priority: str = "medium",
                      context: str = "") -> str:
    """Add an open question to track what we don't know yet.

    Args:
        question: what we need to find out
        priority: high|medium|low
        context: why this matters
    """
    q = add_question(question=question, priority=priority, context=context)
    return json.dumps(q, ensure_ascii=False, indent=1)


@mcp.tool()
def answer_question_tool(question_id: str, answer: str,
                         source: str = "") -> str:
    """Close a question with its answer."""
    result = answer_question(question_id, answer=answer, source=source)
    return json.dumps(result, ensure_ascii=False, indent=1)


@mcp.tool()
def list_open_questions() -> str:
    """List all open questions."""
    data = get_open_questions()
    unanswered = [q for q in data.get("questions", []) if q["status"] == "unanswered"]
    answered = [q for q in data.get("questions", []) if q["status"] == "answered"]
    return json.dumps({
        "total": data.get("total", 0),
        "unanswered": len(unanswered),
        "answered": len(answered),
        "questions": unanswered[:10],
    }, ensure_ascii=False, indent=1)


# ═══════════════════════════════════════════════════════════════════
# COMPRESSION
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def compression_check() -> str:
    """Check if working memory needs compression.

    Returns compression pressure and recommendation.
    Call this periodically to know when to update state files.
    """
    return json.dumps(get_compression_pressure(), ensure_ascii=False, indent=1)


@mcp.tool()
def reset() -> str:
    """Reset all working memory for a new session."""
    return json.dumps(reset_session(), ensure_ascii=False)


if __name__ == "__main__":
    mcp.run(transport="stdio")
