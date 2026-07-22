# sint-working-mcp

Working Memory + Epistemic State MCP server for the [SINT](https://github.com/kostyk348/sint) agent ecosystem.

Structured task state, findings, beliefs, and open questions that live on **disk**, not in the context window.

## Purpose

Context windows are finite. Working memory is not. This MCP gives the agent a persistent epistemic state that survives across tool calls without polluting the context.

**1 tool call = ~200 tokens** instead of replaying full history.

## Tools

### Task State

| Tool | Description |
|---|---|
| `get_state()` | Full compact state snapshot |
| `update_task(title, status, notes)` | Update current task |

### Findings

| Tool | Description |
|---|---|
| `add_finding(claim, source, confidence)` | Record key discovery |
| `revise_finding(id, claim, confidence)` | Update a finding |

### Beliefs (Epistemic)

| Tool | Description |
|---|---|
| `add_belief(statement, confidence)` | Register belief with confidence |
| `revise_belief(id, confidence)` | Update confidence |
| `contradict(a, b)` | Flag contradictory beliefs |
| `get_weakest_beliefs()` | What I'm least sure about |
| `get_epistemic_summary()` | Beliefs overview |

### Open Questions

| Tool | Description |
|---|---|
| `add_question(question)` | Add open question |
| `answer_question(id, answer)` | Close a question |

### Housekeeping

| Tool | Description |
|---|---|
| `compression_check()` | Should I compress now? |
| `reset_session()` | Clear for new session |

## Architecture

```
Agent tool call → server.py → state.py → JSON on disk
                         ↓
              Compact state snapshot (~200 tokens)
```

## State File

All state lives in a single JSON file:

```json
{
  "task": {"title": "...", "status": "in_progress", "notes": "..."},
  "findings": [
    {"id": "f01", "claim": "...", "source": "...", "confidence": 0.8, "revised": false}
  ],
  "beliefs": [
    {"id": "b01", "statement": "...", "confidence": 0.6, "contradicts": []}
  ],
  "questions": [
    {"id": "q01", "question": "...", "answer": null}
  ],
  "message_count": 42,
  "compression_pressure": 0.3
}
```

## Usage Pattern

```python
# Start of task
update_task(title="Reverse engineer ECHONET parser", status="in_progress")

# During work
add_finding("Packet header is 4 bytes, big-endian", source="ghidra decompilation", confidence=0.95)
add_belief("This is ECHONET Lite v1.0", confidence=0.7)
add_question("What is the encryption used?")

# Check epistemic state
get_weakest_beliefs()  # → beliefs with confidence < 0.5
get_epistemic_summary()  # → overview

# End of session
compression_check()  # → "Yes, compress. 42 messages, 0.3 pressure"
```

## Setup

```bash
pip install fastmcp
```

## Run

```bash
python server.py    # stdio mode
```

## Integration

Designed for the [SINT](https://github.com/kostyk348/sint) agent. Use alongside `sint-memory` for long-term storage — working memory handles the current task's epistemic state.

## License

MIT
