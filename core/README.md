# SINT-UA v2.1 — Agent Memory System for OpenCode

[![GitHub](https://img.shields.io/badge/github-kostyk348%2Fsint--ua--v2.1-181717?logo=github)](https://github.com/kostyk348/sint-ua-v2.1)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)
[![OpenCode](https://img.shields.io/badge/OpenCode-compatible-purple)](https://opencode.ai)

A structured memory system with hash-chain provenance, temporal decay, drift detection, provenance archaeology, vector embeddings, and git integration for OpenCode agents.

## What This Is

This is not another prompt template. This is **infrastructure** for AI agent memory:

- **Structured JSON blocks** with semantic registers (SENSE/FACT/LOGIC/OPINION/ACTION)
- **Hash-chain provenance** — tamper-evident chain of all memory blocks
- **Temporal decay** — memory blocks "cool down" over time like human memory
- **Drift detection** — monitors when agent starts hallucinating or losing register discipline
- **Provenance archaeology** — trace any decision back to its root facts
- **Vector embeddings** — semantic search with sentence-transformers
- **Git integration** — link memory blocks to git commits for audit trail

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    sint-main (primary agent)                 │
│  Auto-reads memory → Classifies task → Delegates            │
└─────────┬──────────────────────┬────────────────────────────┘
          │                      │
          ▼                      ▼
┌─────────────────┐    ┌─────────────────┐
│ sint-critic     │    │ sint-scribe     │
│ • Verification  │    │ • Memory ops    │
│ • Fact-check    │    │ • Block I/O     │
│ • Code review   │    │ • Chain verify  │
└─────────────────┘    └─────────────────┘
          │                      │
          └──────────┬───────────┘
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  sint-memory MCP Server                     │
│  16 tools: read/write/search/verify/decay/drift/trace       │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│               Hash-Chain Memory (.opencode/memory/)         │
│  blocks/*.json — chain.jsonl — state.json — sessions/       │
└─────────────────────────────────────────────────────────────┘
```

## Components

### Agents (`.opencode/agents/`)

| Agent | Role | Mode |
|---|---|---|
| **sint-main** | Primary orchestrator, auto-reads memory, classifies, delegates | primary |
| **sint-critic** | Independent verification — register compliance, logic, sources | subagent |
| **sint-scribe** | Memory management — block I/O, chain operations | subagent |
| **sint-router** | Task classification by semantic register and domain | subagent |

### MCP Server

Python MCP server providing 20 tools for memory operations:

```
memory_read_state          memory_write_block
memory_read_block          memory_write_session
memory_read_blocks         memory_update_state
memory_search              memory_verify_chain
memory_get_chain_tail      memory_stats
memory_apply_decay         memory_heat_block
memory_relevance_tiers     memory_drift_check
memory_trace_provenance    git_link_blocks
git_trace_block            git_timeline
embeddings_index           embeddings_search
```

### CLI Tool (`sint`)

```bash
sint status          # Memory stats and current focus
sint recent [n]      # Last N chain entries
sint search <query>  # Search blocks
sint block <id>      # Block details
sint verify          # Verify hash chain
sint add <reg> <text> # Add new block
sint decay           # Apply temporal decay
sint drift           # Drift detection
sint trace <id>      # Provenance archaeology
sint git link        # Link blocks to git commits
sint git timeline    # Combined block + commit timeline
sint dashboard       # Full dashboard
```

### Vector Embeddings (`sint-embeddings`)

```bash
sint-embeddings index       # Build/update embedding index
sint-embeddings search <q>  # Semantic search
sint-embeddings similar <id> # Find similar blocks
```

### Git Integration (`sint-git`)

```bash
sint-git link         # Link blocks to git commits
sint-git trace <id>   # Trace block through git history
sint-git timeline     # Combined timeline
sint-git info         # Current commit details
```

### Plugin (`sint-hooks`)

TypeScript plugin with hooks:
- `tool.execute.after` — auto-log significant findings
- `chat.system.transform` — inject memory context
- `session.compacting` — preserve across compaction

### Commands

| Command | What it does |
|---|---|
| `/session-start` | Read memory, present context |
| `/session-end` | Write summary, update state |
| `/verify [content]` | Run sint-critic |
| `/memory [query]` | Query memory system |
| `/dashboard` | Full dashboard view |

## Memory Blocks

Each block is a JSON file with semantic register:

```json
{
  "id": "0042",
  "register": "FACT",
  "prev_hash": "a3f2c...",
  "hash": "7b1d9...",
  "timestamp": "2026-07-14T12:00:00Z",
  "project": "DSA",
  "content": "3D attenuation verified: near=0.25 far=0.0025",
  "source": "bench run 2026-07-13",
  "confidence": 0.95,
  "tags": ["3d", "attenuation", "verified"],
  "links": ["0038"]
}
```

### Registers

| Register | Use for |
|---|---|
| `SENSE` | Raw observations, tool output, logs |
| `FACT` | Verified claims with sources |
| `LOGIC` | Inferences from FACT/SENSE |
| `OPINION` | Subjective assessments (must be labeled) |
| `ACTION` | Execution plans, next steps |

### Hash-Chain

Every block references the previous block's hash:
```
block_N.prev_hash = block_{N-1}.hash
block_N.hash = sha256(id + register + content + prev_hash)[:16]
```

Tamper-evident: modifying any block breaks all subsequent hashes.

## Novel Features

### Temporal Decay

Memory blocks have relevance scores that decay over time:
- **Hot** (relevance > 0.7): Recently accessed or highly linked
- **Warm** (0.4-0.7): Still relevant
- **Cool** (0.15-0.4): Aging
- **Cold** (< 0.15): Nearly forgotten

```bash
sint decay    # Apply decay to all blocks
sint heat 0042 # Heat up block for 7 days
```

### Drift Detection

Monitors agent behavior across sessions:
- Register distribution (are opinions labeled as facts?)
- Source coverage (are claims traceable?)
- Confidence trends
- Topic consistency

```bash
sint drift    # Check for anomalies
```

### Provenance Archaeology

Trace any decision back to its root facts:
```bash
sint trace 0042  # Full reasoning chain
sint trace 0042 --tree  # Dependency tree
```

### Vector Embeddings

Semantic search using sentence-transformers with `all-MiniLM-L6-v2` (384-dim):

```bash
sint-embeddings search "3D audio attenuation"  # Returns top 10 similar blocks
sint-embeddings similar 0005  # Find blocks similar to block 0005
```

Embedding index stored at `.opencode/memory/embeddings/`.

### Git Integration

Link memory blocks to git commits for complete audit trail:

```bash
sint git link         # Link blocks to recent commits by timestamp
sint git trace 0042   # Show git commits linked to block
sint git timeline     # Combined memory + git timeline
sint git info         # Current commit details
```

## Setup

### 1. Copy to your project

```bash
cp -r .opencode/agents/ /path/to/your/project/.opencode/agents/
cp -r .opencode/mcp/ /path/to/your/project/.opencode/mcp/
cp -r .opencode/plugin/ /path/to/your/project/.opencode/plugin/
cp -r .opencode/commands/ /path/to/your/project/.opencode/commands/
cp .opencode/bin/sint /usr/local/bin/
```

### 2. Install dependencies

```bash
pip install mcp sentence-transformers faiss-cpu
```

### 3. Update opencode.json

Add to your `opencode.json`:
```json
{
  "default_agent": "sint-main",
  "agent": {
    "sint-main": { "mode": "primary" },
    "sint-critic": { "mode": "subagent" },
    "sint-scribe": { "mode": "subagent" }
  },
  "mcp": {
    "sint-memory": {
      "type": "local",
      "command": ["python3", "/path/to/.opencode/mcp/sint-memory/server.py"]
    }
  },
  "plugin": ["/path/to/.opencode/plugin/sint-hooks.ts"]
}
```

### 4. Restart OpenCode

```bash
# Changes require restart
opencode
```

## Usage

### Automatic (default)

After setup, `sint-main` runs automatically:
1. Reads memory state
2. Greets with context
3. Classifies tasks
4. Delegates to specialists
5. Plugin auto-logs findings

### Manual

```bash
# Terminal
sint status
sint drift
sint trace 0042

# In OpenCode
/session-start
/verify this claim
/memory "3D attenuation"
/dashboard
```

## How It's Different

| Typical Agent Systems | SINT-UA v2.1 |
|---|---|
| Flat context window | Structured JSON blocks |
| No provenance | Hash-chain audit trail |
| Memory = full context | Temporal decay, relevance scoring |
| No drift detection | Cross-session anomaly monitoring |
| Manual memory updates | Auto-logging via plugin hooks |
| "Trust me" | Cryptographic verification |

## File Structure

```
.opencode/
├── agents/
│   ├── sint-main.md
│   ├── sint-critic.md
│   ├── sint-scribe.md
│   └── sint-router.md
├── commands/
│   ├── session-start.md
│   ├── session-end.md
│   ├── verify.md
│   ├── memory.md
│   └── dashboard.md
├── mcp/sint-memory/
│   └── server.py
├── plugin/
│   └── sint-hooks.ts
├── memory/
│   ├── state.json
│   ├── chain.jsonl
│   ├── blocks/
│   └── sessions/
├── bin/
│   ├── sint
│   ├── sint-decay
│   ├── sint-drift
│   └── sint-archaeology
└── skills/
    └── memory-system/SKILL.md
```

## License

MIT
