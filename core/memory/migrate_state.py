#!/usr/bin/env python3
"""
migrate_state.py — Migrate STATE.MD to structured memory system.

Reads .opencode/skills/state/SKILL.md and creates:
  - .opencode/memory/state.json (current focus)
  - .opencode/memory/chain.jsonl (genesis block)
  - .opencode/memory/blocks/ (verified patterns as FACT blocks)
  - .opencode/memory/sessions/ (session log entries)
"""

import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path

MEMORY_DIR = Path("/home/lain/.opencode/memory")
BLOCKS_DIR = MEMORY_DIR / "blocks"
SESSIONS_DIR = MEMORY_DIR / "sessions"
STATE_FILE = MEMORY_DIR / "state.json"
CHAIN_FILE = MEMORY_DIR / "chain.jsonl"
STATE_MD = Path("/home/lain/.opencode/skills/state/SKILL.md")


def compute_hash(block_id: str, register: str, content: str, prev_hash: str) -> str:
    payload = f"{block_id}:{register}:{content}:{prev_hash}"
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def parse_state_md(text: str) -> dict:
    """Extract structured data from STATE.MD."""
    data = {
        "focus": [],
        "pending_decisions": [],
        "verified_patterns": [],
        "session_log": [],
        "continuation_prompts": [],
    }

    # Parse focus items
    focus_match = re.search(r"## CURRENT FOCUS.*?\n(.*?)(?=\n##|\Z)", text, re.DOTALL)
    if focus_match:
        for line in focus_match.group(1).strip().split("\n"):
            line = line.strip()
            if line.startswith("- **") or line.startswith("1. **"):
                # Extract project and task
                m = re.match(r"[\d\.\-\*]+\s*\*\*(.+?)\*\*\s*[—–-]\s*(.+)", line)
                if m:
                    data["focus"].append({
                        "project": m.group(1).strip(),
                        "task": m.group(2).strip(),
                        "status": "in_progress"
                    })

    # Parse verified patterns
    verified_match = re.search(r"## VERIFIED THIS WEEK.*?\n(.*?)(?=\n##|\Z)", text, re.DOTALL)
    if verified_match:
        for line in verified_match.group(1).strip().split("\n"):
            line = line.strip()
            if line.startswith("- **"):
                m = re.match(r"-\s*\*\*(.+?)\*\*\s*[—–:]\s*(.+)", line)
                if m:
                    data["verified_patterns"].append({
                        "title": m.group(1).strip(),
                        "content": m.group(2).strip()
                    })

    # Parse pending decisions
    pending_match = re.search(r"## PENDING DECISIONS.*?\n(.*?)(?=\n##|\Z)", text, re.DOTALL)
    if pending_match:
        for line in pending_match.group(1).strip().split("\n"):
            line = line.strip()
            if line.startswith("- **"):
                m = re.match(r"-\s*\*\*(.+?)\*\*\s*[—–:]\s*(.+)", line)
                if m:
                    data["pending_decisions"].append({
                        "question": m.group(1).strip(),
                        "context": m.group(2).strip()
                    })

    # Parse session log
    session_match = re.search(r"## SESSION LOG.*?\n(.*?)(?=\n##|\Z)", text, re.DOTALL)
    if session_match:
        for line in session_match.group(1).strip().split("\n"):
            line = line.strip()
            if line.startswith("1. **") or line.startswith("- **"):
                m = re.match(r"[\d\.\-\*]+\s*\*\*(.+?)\*\*\s*[—–:]\s*(.+)", line)
                if m:
                    data["session_log"].append({
                        "session_id": m.group(1).strip(),
                        "summary": m.group(2).strip()
                    })

    # Parse continuation prompts
    cont_match = re.search(r"## CONTINUATION PROMPTS.*?\n(.*?)(?=\n##|\Z)", text, re.DOTALL)
    if cont_match:
        for line in cont_match.group(1).strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("100"):
                data["continuation_prompts"].append(line)

    return data


def create_genesis_block():
    """Create the first block in the chain."""
    genesis = {
        "id": "0000",
        "register": "SENSE",
        "prev_hash": "0" * 16,
        "hash": "",
        "timestamp": datetime.now().isoformat() + "Z",
        "project": "SYSTEM",
        "content": "Memory system initialized. Migration from STATE.MD.",
        "source": "migrate_state.py",
        "confidence": 1.0,
        "tags": ["system", "init"],
        "links": []
    }
    genesis["hash"] = compute_hash(
        genesis["id"], genesis["register"],
        genesis["content"], genesis["prev_hash"]
    )
    return genesis


def create_block(block_id: str, register: str, content: str,
                 prev_hash: str, project: str = "SYSTEM",
                 source: str = "migration", confidence: float = 0.9,
                 tags: list = None, links: list = None) -> dict:
    """Create a memory block with hash."""
    block = {
        "id": block_id,
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
    return block


def main():
    # Ensure directories exist
    BLOCKS_DIR.mkdir(parents=True, exist_ok=True)
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    # Read STATE.MD
    if not STATE_MD.exists():
        print(f"ERROR: {STATE_MD} not found")
        return

    text = STATE_MD.read_text()
    data = parse_state_md(text)

    print(f"Parsed STATE.MD:")
    print(f"  Focus items: {len(data['focus'])}")
    print(f"  Verified patterns: {len(data['verified_patterns'])}")
    print(f"  Pending decisions: {len(data['pending_decisions'])}")
    print(f"  Session log entries: {len(data['session_log'])}")

    # Create genesis block
    genesis = create_genesis_block()
    chain_entries = [genesis]

    # Write genesis block file
    genesis_file = BLOCKS_DIR / f"{genesis['id']}.sense.json"
    genesis_file.write_text(json.dumps(genesis, indent=2, ensure_ascii=False))
    print(f"Created genesis block: {genesis_file}")

    # Create blocks for verified patterns
    block_id = 1
    prev_hash = genesis["hash"]

    for pattern in data["verified_patterns"]:
        block = create_block(
            block_id=f"{block_id:04d}",
            register="FACT",
            content=f"{pattern['title']}: {pattern['content']}",
            prev_hash=prev_hash,
            project="VARIOUS",
            source="STATE.MD migration",
            confidence=0.9,
            tags=["verified", "migrated"]
        )
        chain_entries.append(block)

        block_file = BLOCKS_DIR / f"{block['id']}.fact.json"
        block_file.write_text(json.dumps(block, indent=2, ensure_ascii=False))

        prev_hash = block["hash"]
        block_id += 1

    # Create blocks for session log
    for session in data["session_log"]:
        block = create_block(
            block_id=f"{block_id:04d}",
            register="SENSE",
            content=f"Session {session['session_id']}: {session['summary']}",
            prev_hash=prev_hash,
            project="SYSTEM",
            source="STATE.MD migration",
            confidence=1.0,
            tags=["session", "log", "migrated"]
        )
        chain_entries.append(block)

        block_file = BLOCKS_DIR / f"{block['id']}.sense.json"
        block_file.write_text(json.dumps(block, indent=2, ensure_ascii=False))

        prev_hash = block["hash"]
        block_id += 1

    # Create blocks for pending decisions
    for i, decision in enumerate(data["pending_decisions"]):
        block = create_block(
            block_id=f"{block_id:04d}",
            register="OPINION",
            content=f"{decision['question']} — {decision['context']}",
            prev_hash=prev_hash,
            project="SYSTEM",
            source="STATE.MD migration",
            confidence=0.7,
            tags=["decision", "pending", "migrated"]
        )
        chain_entries.append(block)

        block_file = BLOCKS_DIR / f"{block['id']}.opinion.json"
        block_file.write_text(json.dumps(block, indent=2, ensure_ascii=False))

        prev_hash = block["hash"]
        block_id += 1

    # Write chain.jsonl
    with open(CHAIN_FILE, "w") as f:
        for entry in chain_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"Wrote {len(chain_entries)} entries to chain.jsonl")

    # Update state.json
    state = {
        "version": 1,
        "last_updated": datetime.now().isoformat() + "Z",
        "focus": data["focus"][:3],  # Max 3
        "pending_decisions": [
            {
                "id": f"d{i+1}",
                "question": d["question"],
                "context": d["context"],
                "created": "2026-07-14"
            }
            for i, d in enumerate(data["pending_decisions"])
        ],
        "session_count": len(data["session_log"]),
        "last_session": data["session_log"][0]["session_id"] if data["session_log"] else "unknown",
        "migrated_from": "STATE.MD",
        "migration_date": datetime.now().isoformat() + "Z"
    }

    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))
    print(f"Updated state.json with {len(state['focus'])} focus items")

    # Create session log for migration
    session_file = SESSIONS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"
    with open(session_file, "a") as f:
        f.write(json.dumps({
            "time": datetime.now().strftime("%H:%M"),
            "event": "migration",
            "source": "STATE.MD",
            "blocks_created": len(chain_entries) - 1,
            "chain_length": len(chain_entries)
        }, ensure_ascii=False) + "\n")

    print(f"\nMigration complete!")
    print(f"  Blocks created: {len(chain_entries) - 1}")
    print(f"  Chain length: {len(chain_entries)}")
    print(f"  State focus: {[f['project'] for f in state['focus']]}")
    print(f"\nNext steps:")
    print(f"  1. Restart opencode to load new agents")
    print(f"  2. Use sint-scribe agent for memory operations")
    print(f"  3. Old STATE.MD preserved at {STATE_MD}")


if __name__ == "__main__":
    main()
