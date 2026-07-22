# sint-memory MCP Server

MCP server for SINT-UA v2.1 structured memory with hash-chain provenance.

## Setup

```bash
pip install mcp
```

## Run

```bash
python3 /home/lain/.opencode/mcp/sint-memory/server.py
```

Or via OpenCode (auto-started):
```json
{
  "mcp": {
    "sint-memory": {
      "type": "local",
      "command": ["python3", "/home/lain/.opencode/mcp/sint-memory/server.py"],
      "enabled": true
    }
  }
}
```

## Tools

| Tool | Args | Description |
|---|---|---|
| `memory_read_state` | — | Read current focus, pending decisions |
| `memory_read_block` | `block_id: str` | Read specific block by ID |
| `memory_read_blocks` | `register?, project?, limit?` | Read recent blocks |
| `memory_write_block` | `register, content, project?, source?, confidence?, tags?, links?` | Create new block |
| `memory_write_session` | `event, details?` | Log session event |
| `memory_update_state` | `focus?, pending_decisions?, last_session?` | Update state.json |
| `memory_verify_chain` | — | Verify hash chain integrity |
| `memory_search` | `query?, register?, project?, tags?, limit?` | Search blocks |
| `memory_get_chain_tail` | `n?` | Get last N chain entries |
| `memory_stats` | — | System statistics |

## Registers

- `SENSE` — Raw observations, tool output
- `FACT` — Verified claims with sources
- `LOGIC` — Inferences from FACT/SENSE
- `OPINION` — Subjective assessments
- `ACTION` — Execution plans

## Block Format

```json
{
  "id": "0042",
  "register": "FACT",
  "prev_hash": "a3f2c...",
  "hash": "7b1d9...",
  "timestamp": "2026-07-14T12:00:00Z",
  "project": "DSA",
  "content": "3D attenuation verified: near=0.25 far=0.0025",
  "source": "bench run",
  "confidence": 0.95,
  "tags": ["3d", "verified"],
  "links": ["0038"]
}
```
