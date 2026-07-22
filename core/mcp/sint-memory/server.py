#!/usr/bin/env python3
"""
sint-memory-mcp — MCP server for structured memory operations.

Provides tools for reading, writing, searching, and verifying
the hash-chain memory system.

Usage: python3 sint-memory-mcp.py
"""

import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

# Memory directory
MEMORY_DIR = Path(os.environ.get("SINT_MEMORY_DIR", "/home/lain/.opencode/memory"))
BLOCKS_DIR = MEMORY_DIR / "blocks"
SESSIONS_DIR = MEMORY_DIR / "sessions"
STATE_FILE = MEMORY_DIR / "state.json"
CHAIN_FILE = MEMORY_DIR / "chain.jsonl"

mcp = FastMCP("sint-memory", dependencies=["mcp"])


def compute_hash(block_id: str, register: str, content: str, prev_hash: str) -> str:
    payload = f"{block_id}:{register}:{content}:{prev_hash}"
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def get_last_chain_entry() -> Optional[dict]:
    if not CHAIN_FILE.exists():
        return None
    lines = CHAIN_FILE.read_text().strip().split("\n")
    if not lines or not lines[0]:
        return None
    return json.loads(lines[-1])


def read_block(block_id: str) -> Optional[dict]:
    for f in BLOCKS_DIR.glob(f"{block_id}.*.json"):
        return json.loads(f.read_text())
    return None


def search_blocks(query: str = "", register: str = "", project: str = "",
                  tags: list = None, limit: int = 20) -> list:
    results = []
    for f in BLOCKS_DIR.glob("*.json"):
        block = json.loads(f.read_text())
        if register and block.get("register") != register:
            continue
        if project and block.get("project") != project:
            continue
        if tags and not all(t in block.get("tags", []) for t in tags):
            continue
        if query and query.lower() not in block.get("content", "").lower():
            continue
        results.append(block)
    results.sort(key=lambda b: b.get("id", "0000"), reverse=True)
    return results[:limit]


# --- TOOLS ---

@mcp.tool()
def memory_read_state() -> dict:
    """Read current memory state: focus, pending decisions, session count."""
    if not STATE_FILE.exists():
        return {"error": "state.json not found"}
    return json.loads(STATE_FILE.read_text())


@mcp.tool()
def memory_read_block(block_id: str) -> dict:
    """Read a specific memory block by ID (e.g. '0042')."""
    block = read_block(block_id)
    if not block:
        return {"error": f"Block {block_id} not found"}
    return block


@mcp.tool()
def memory_read_blocks(register: str = "", project: str = "",
                       limit: int = 10) -> list:
    """Read recent memory blocks, optionally filtered by register or project."""
    return search_blocks(register=register, project=project, limit=limit)


@mcp.tool()
def memory_write_block(register: str, content: str, project: str = "SYSTEM",
                       source: str = "agent", confidence: float = 0.9,
                       tags: list = None, links: list = None) -> dict:
    """
    Write a new memory block to the hash chain.
    
    register: SENSE|FACT|LOGIC|OPINION|ACTION
    content: The finding/observation/plan
    project: Project name (DSA, DataTrace, etc.)
    source: Where this came from
    confidence: 0.0-1.0
    tags: List of tags for search
    links: List of related block IDs
    """
    # Get last chain entry
    last = get_last_chain_entry()
    if last:
        prev_id = last["id"]
        prev_hash = last["hash"]
        next_id = f"{int(prev_id) + 1:04d}"
    else:
        prev_hash = "0" * 16
        next_id = "0000"

    # Create block
    block = {
        "id": next_id,
        "register": register,
        "prev_hash": prev_hash,
        "hash": "",
        "timestamp": datetime.now().isoformat() + "Z",
        "project": project,
        "content": content,
        "source": source,
        "confidence": confidence,
        "tags": tags or [],
        "links": links or []
    }
    block["hash"] = compute_hash(
        block["id"], block["register"],
        block["content"], block["prev_hash"]
    )

    # Write block file
    block_file = BLOCKS_DIR / f"{block['id']}.{register.lower()}.json"
    BLOCKS_DIR.mkdir(parents=True, exist_ok=True)
    block_file.write_text(json.dumps(block, indent=2, ensure_ascii=False))

    # Append to chain
    CHAIN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CHAIN_FILE, "a") as f:
        f.write(json.dumps(block, ensure_ascii=False) + "\n")

    return {"success": True, "id": block["id"], "hash": block["hash"]}


@mcp.tool()
def memory_write_session(event: str, details: dict = None) -> dict:
    """Log a session event to today's session log."""
    today = datetime.now().strftime("%Y-%m-%d")
    session_file = SESSIONS_DIR / f"{today}.jsonl"
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    entry = {
        "time": datetime.now().strftime("%H:%M"),
        "event": event
    }
    if details:
        entry.update(details)

    with open(session_file, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return {"success": True, "file": str(session_file)}


@mcp.tool()
def memory_update_state(focus: list = None, pending_decisions: list = None,
                        last_session: str = None) -> dict:
    """Update memory state: focus items, pending decisions, last session."""
    if not STATE_FILE.exists():
        return {"error": "state.json not found — run migration first"}

    state = json.loads(STATE_FILE.read_text())

    if focus is not None:
        state["focus"] = focus[:3]  # Max 3
    if pending_decisions is not None:
        state["pending_decisions"] = pending_decisions
    if last_session is not None:
        state["last_session"] = last_session

    state["last_updated"] = datetime.now().isoformat() + "Z"

    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))
    return {"success": True, "focus_count": len(state["focus"])}


@mcp.tool()
def memory_verify_chain() -> dict:
    """Verify hash chain integrity. Returns any broken links."""
    if not CHAIN_FILE.exists():
        return {"error": "chain.jsonl not found"}

    lines = CHAIN_FILE.read_text().strip().split("\n")
    if not lines or not lines[0]:
        return {"chain_length": 0, "valid": True}

    broken = []
    prev_hash = "0" * 16

    for i, line in enumerate(lines):
        if not line.strip():
            continue
        entry = json.loads(line)

        # Check prev_hash links
        if entry.get("prev_hash") != prev_hash:
            broken.append({
                "entry_index": i,
                "id": entry.get("id"),
                "expected_prev": prev_hash,
                "actual_prev": entry.get("prev_hash")
            })

        # Verify content hash
        block = read_block(entry["id"])
        if block:
            expected_hash = compute_hash(
                block["id"], block["register"],
                block["content"], block["prev_hash"]
            )
            if block.get("hash") != expected_hash:
                broken.append({
                    "entry_index": i,
                    "id": entry["id"],
                    "type": "hash_mismatch",
                    "expected": expected_hash,
                    "actual": block.get("hash")
                })

        prev_hash = entry.get("hash", prev_hash)

    return {
        "chain_length": len(lines),
        "valid": len(broken) == 0,
        "broken_links": broken
    }


@mcp.tool()
def memory_search(query: str = "", register: str = "",
                  project: str = "", tags: list = None,
                  limit: int = 20) -> list:
    """Search memory blocks by content, register, project, or tags."""
    return search_blocks(query=query, register=register,
                        project=project, tags=tags, limit=limit)


@mcp.tool()
def memory_get_chain_tail(n: int = 10) -> list:
    """Get the last N entries from the hash chain."""
    if not CHAIN_FILE.exists():
        return []

    lines = CHAIN_FILE.read_text().strip().split("\n")
    entries = []
    for line in lines[-n:]:
        if line.strip():
            entries.append(json.loads(line))
    return entries


@mcp.tool()
def memory_stats() -> dict:
    """Get memory system statistics."""
    blocks = list(BLOCKS_DIR.glob("*.json")) if BLOCKS_DIR.exists() else []
    sessions = list(SESSIONS_DIR.glob("*.jsonl")) if SESSIONS_DIR.exists() else []
    
    chain_length = 0
    if CHAIN_FILE.exists():
        lines = CHAIN_FILE.read_text().strip().split("\n")
        chain_length = len([l for l in lines if l.strip()])

    registers = {}
    for f in blocks:
        block = json.loads(f.read_text())
        reg = block.get("register", "unknown")
        registers[reg] = registers.get(reg, 0) + 1

    return {
        "total_blocks": len(blocks),
        "chain_length": chain_length,
        "total_sessions": len(sessions),
        "blocks_by_register": registers
    }


# --- TEMPORAL DECAY ---

def _compute_final_relevance(block_file: Path) -> float:
    """Compute final relevance score for a block (decay engine)."""
    import math
    block = json.loads(block_file.read_text())
    
    DECAY_HALF_LIFE_DAYS = 30
    MIN_RELEVANCE = 0.01
    
    # Base from confidence + register
    confidence = block.get("confidence", 0.5)
    register_weights = {"FACT": 1.0, "ACTION": 0.95, "LOGIC": 0.9, "SENSE": 0.7, "OPINION": 0.6}
    base = confidence * register_weights.get(block.get("register", "SENSE"), 0.7)
    
    # Time decay
    ts = block.get("timestamp", "")
    if ts:
        try:
            mtime = datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None)
            age_days = (datetime.now() - mtime).total_seconds() / 86400
            decay = math.exp(-0.693 * age_days / DECAY_HALF_LIFE_DAYS)
        except:
            decay = 1.0
    else:
        decay = 1.0
    
    # Link boost
    links = block.get("links", [])
    inbound = 0
    for f in BLOCKS_DIR.glob("*.json"):
        other = json.loads(f.read_text())
        if block["id"] in other.get("links", []):
            inbound += 1
    link_factor = 1.0 + ((len(links) + inbound) * 0.15)
    
    # Heated?
    heated_until = block.get("_heated_until")
    if heated_until:
        try:
            if datetime.now() < datetime.fromisoformat(heated_until.replace("Z", "")):
                return min(1.0, base * 1.3 * link_factor)
        except:
            pass
    
    score = base * decay * link_factor
    return max(min(score, 1.0), MIN_RELEVANCE)


@mcp.tool()
def memory_apply_decay() -> dict:
    """Apply temporal decay to all blocks. Returns relevance scores."""
    if not BLOCKS_DIR.exists():
        return {"error": "No blocks directory"}
    
    results = []
    for f in sorted(BLOCKS_DIR.glob("*.json")):
        block = json.loads(f.read_text())
        relevance = _compute_final_relevance(f)
        block["_relevance"] = round(relevance, 4)
        block["_relevance_updated"] = datetime.now().isoformat() + "Z"
        f.write_text(json.dumps(block, indent=2, ensure_ascii=False))
        results.append({"id": block["id"], "register": block.get("register"), "relevance": relevance})
    
    return {"applied": len(results), "blocks": results}


@mcp.tool()
def memory_heat_block(block_id: str) -> dict:
    """Heat up a block — mark as recently accessed for 7 days."""
    for f in BLOCKS_DIR.glob(f"{block_id}.*.json"):
        block = json.loads(f.read_text())
        from datetime import timedelta
        block["_heated_until"] = (datetime.now() + timedelta(days=7)).isoformat() + "Z"
        block["_last_heated"] = datetime.now().isoformat() + "Z"
        f.write_text(json.dumps(block, indent=2, ensure_ascii=False))
        return {"success": True, "heated_until": block["_heated_until"]}
    return {"error": f"Block {block_id} not found"}


@mcp.tool()
def memory_relevance_tiers() -> dict:
    """Get blocks grouped by relevance tier (hot/warm/cool/cold)."""
    if not BLOCKS_DIR.exists():
        return {"error": "No blocks"}
    
    tiers = {"hot": [], "warm": [], "cool": [], "cold": []}
    for f in sorted(BLOCKS_DIR.glob("*.json")):
        block = json.loads(f.read_text())
        rel = block.get("_relevance") or _compute_final_relevance(f)
        
        if rel >= 0.7: tier = "hot"
        elif rel >= 0.4: tier = "warm"
        elif rel >= 0.15: tier = "cool"
        else: tier = "cold"
        
        tiers[tier].append({"id": block["id"], "register": block.get("register"), "relevance": rel})
    
    return {k: len(v) for k, v in tiers.items()} | {"details": tiers}


# --- DRIFT DETECTION ---

@mcp.tool()
def memory_drift_check() -> dict:
    """Check for register distribution drift and other anomalies."""
    from collections import Counter
    
    if not BLOCKS_DIR.exists():
        return {"error": "No blocks"}
    
    blocks = []
    for f in BLOCKS_DIR.glob("*.json"):
        try:
            blocks.append(json.loads(f.read_text()))
        except:
            pass
    
    if not blocks:
        return {"error": "No blocks"}
    
    # Register distribution
    counts = Counter(b.get("register", "UNKNOWN") for b in blocks)
    total = sum(counts.values())
    distribution = {reg: count / total for reg, count in counts.items()}
    
    # Expected
    expected = {"FACT": 0.35, "SENSE": 0.25, "LOGIC": 0.20, "ACTION": 0.15, "OPINION": 0.05}
    
    # Alerts
    alerts = []
    for reg, exp in expected.items():
        actual = distribution.get(reg, 0)
        deviation = abs(actual - exp)
        if deviation > 0.3:
            direction = "more" if actual > exp else "fewer"
            alerts.append(f"CRITICAL: {direction} {reg} blocks ({actual:.0%} vs expected {exp:.0%})")
    
    # Source coverage for FACT blocks
    fact_blocks = [b for b in blocks if b.get("register") == "FACT"]
    if fact_blocks:
        with_source = sum(1 for b in fact_blocks if b.get("source", "") not in ["agent", "migration", "CLI", ""])
        coverage = with_source / len(fact_blocks)
        if coverage < 0.4:
            alerts.append(f"WARNING: Only {coverage:.0%} of FACT blocks have proper sources")
    
    # Low confidence
    low_conf = [b for b in blocks if b.get("confidence", 1) < 0.5]
    if low_conf and len(low_conf) / len(blocks) > 0.3:
        alerts.append(f"WARNING: {len(low_conf)} blocks ({len(low_conf)/len(blocks):.0%}) have low confidence")
    
    return {
        "block_count": len(blocks),
        "distribution": distribution,
        "alerts": alerts,
        "healthy": len(alerts) == 0
    }


# --- PROVENANCE ARCHAEOLOGY ---

@mcp.tool()
def memory_trace_provenance(block_id: str) -> dict:
    """Trace the full reasoning chain from a block back to genesis."""
    if not BLOCKS_DIR.exists():
        return {"error": "No blocks"}
    
    all_blocks = {}
    for f in BLOCKS_DIR.glob("*.json"):
        try:
            block = json.loads(f.read_text())
            all_blocks[block["id"]] = block
        except:
            pass
    
    if block_id not in all_blocks:
        return {"error": f"Block {block_id} not found"}
    
    chain_path = []
    visited = set()
    current_id = block_id
    
    while current_id and current_id not in visited:
        if current_id not in all_blocks:
            break
        
        block = all_blocks[current_id]
        visited.add(current_id)
        
        chain_path.append({
            "id": block["id"],
            "register": block.get("register", "?"),
            "project": block.get("project", "?"),
            "content": block.get("content", "")[:100],
            "confidence": block.get("confidence", 0)
        })
        
        # Follow links or prev_hash
        links = block.get("links", [])
        if links:
            current_id = links[0]
        else:
            prev_hash = block.get("prev_hash", "")
            if prev_hash:
                # Find in chain
                if CHAIN_FILE.exists():
                    chain_lines = CHAIN_FILE.read_text().strip().split("\n")
                    found = False
                    for line in chain_lines:
                        entry = json.loads(line)
                        if entry.get("hash") == prev_hash:
                            current_id = entry.get("id")
                            found = True
                            break
                    if not found:
                        current_id = None
                else:
                    current_id = None
            else:
                current_id = None
    
    chain_path.reverse()
    
    return {
        "block_id": block_id,
        "chain_length": len(chain_path),
        "chain": chain_path,
        "genesis": [p for p in chain_path if p["register"] in ("SENSE", "FACT")]
    }


# --- Git Integration Tools ---

GIT_LINKS_FILE = MEMORY_DIR / "git_links.jsonl"


def _run_git(args: list, cwd: str = None) -> str:
    """Run git command and return output."""
    import subprocess
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            cwd=cwd or os.getcwd()
        )
        return result.stdout.strip()
    except Exception as e:
        return ""


@mcp.tool()
def git_link_blocks() -> str:
    """Link memory blocks to git commits based on timestamps.
    
    Scans recent commits and links blocks created around the same time.
    Returns the number of new links created.
    """
    commits = []
    output = _run_git(["log", "-50", "--format=%H|%s|%ai|%an"])
    if output:
        for line in output.split("\n"):
            if "|" in line:
                parts = line.split("|", 3)
                if len(parts) >= 3:
                    commits.append({
                        "hash": parts[0],
                        "message": parts[1],
                        "date": parts[2],
                        "author": parts[3] if len(parts) > 3 else "unknown"
                    })
    
    if not commits:
        return "No git commits found."
    
    existing_links = {}
    if GIT_LINKS_FILE.exists():
        for line in GIT_LINKS_FILE.read_text().strip().split("\n"):
            if line.strip():
                link = json.loads(line)
                existing_links[link["block_id"]] = link
    
    blocks = {}
    for f in BLOCKS_DIR.glob("*.json"):
        try:
            block = json.loads(f.read_text())
            blocks[block["id"]] = block
        except:
            pass
    
    new_links = 0
    for bid, block in blocks.items():
        if bid in existing_links:
            continue
        
        block_ts = block.get("timestamp", "")
        if not block_ts:
            continue
        
        try:
            block_time = datetime.fromisoformat(block_ts.replace("Z", "+00:00")).replace(tzinfo=None)
        except:
            continue
        
        for commit in commits:
            try:
                commit_time = datetime.strptime(commit["date"][:19], "%Y-%m-%d %H:%M:%S")
                diff = (block_time - commit_time).total_seconds()
                if -3600 <= diff <= 7200:
                    link = {
                        "block_id": bid,
                        "commit_hash": commit["hash"],
                        "commit_message": commit["message"],
                        "commit_date": commit["date"],
                        "block_timestamp": block_ts,
                        "time_diff_seconds": diff,
                        "linked_at": datetime.now().isoformat()
                    }
                    
                    with open(GIT_LINKS_FILE, "a") as f:
                        f.write(json.dumps(link, ensure_ascii=False) + "\n")
                    
                    existing_links[bid] = link
                    new_links += 1
                    break
            except:
                continue
    
    return f"Linked {new_links} new blocks. Total links: {len(existing_links)}"


@mcp.tool()
def git_trace_block(block_id: str) -> str:
    """Trace a memory block through git history.
    
    Shows git commits linked to the block and nearby commits.
    """
    links = []
    if GIT_LINKS_FILE.exists():
        for line in GIT_LINKS_FILE.read_text().strip().split("\n"):
            if line.strip():
                link = json.loads(line)
                if link["block_id"] == block_id:
                    links.append(link)
    
    if not links:
        return f"No git links found for block {block_id}."
    
    result = [f"Git Links for {block_id}:"]
    for link in links:
        result.append(f"  {link.get('commit_hash', '?')[:8]}")
        result.append(f"    {link.get('commit_message', '?')}")
        result.append(f"    {link.get('commit_date', '?')}")
        if "time_diff_seconds" in link:
            diff = link["time_diff_seconds"]
            result.append(f"    Time diff: {diff:.0f}s")
    
    return "\n".join(result)


@mcp.tool()
def git_timeline(project: Optional[str] = None, limit: int = 20) -> str:
    """Get combined timeline of memory blocks and git commits.
    
    Returns interleaved events sorted by time.
    """
    events = []
    
    # Memory blocks
    for f in BLOCKS_DIR.glob("*.json"):
        try:
            block = json.loads(f.read_text())
            if project and block.get("project") != project:
                continue
            events.append({
                "type": "block",
                "id": block["id"],
                "timestamp": block.get("timestamp", ""),
                "register": block.get("register", ""),
                "content": block.get("content", "")[:60]
            })
        except:
            pass
    
    # Git commits
    output = _run_git(["log", f"-{limit}", "--format=%H|%s|%ai|%an"])
    if output:
        for line in output.split("\n"):
            if "|" in line:
                parts = line.split("|", 3)
                if len(parts) >= 3:
                    events.append({
                        "type": "commit",
                        "hash": parts[0][:8],
                        "timestamp": parts[2],
                        "message": parts[1][:60]
                    })
    
    events.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
    
    result = ["Combined Timeline:"]
    for event in events[:limit]:
        if event["type"] == "block":
            result.append(f"  {event.get('timestamp', '?')[:19]}  BLOCK {event['id']} {event.get('register', '?')}")
            result.append(f"    {event.get('content', '')}")
        else:
            result.append(f"  {event.get('timestamp', '?')[:19]}  COMMIT {event.get('hash', '?')}")
            result.append(f"    {event.get('message', '')}")
    
    return "\n".join(result)


@mcp.tool()
def git_commit_info() -> str:
    """Show information about the current git commit."""
    output = _run_git(["log", "-1", "--format=%H%n%s%n%ai%n%an"])
    if not output:
        return "No git commits found."
    
    lines = output.split("\n")
    return f"Commit: {lines[0][:8]}\nMessage: {lines[1]}\nDate: {lines[2]}\nAuthor: {lines[3]}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
