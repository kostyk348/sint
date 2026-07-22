# replay (Planned)

Session replay and failure analysis for the SINT agent.

## Purpose

When something goes wrong, the agent needs to replay the session to understand:
- Where did the failure occur?
- What decisions led to it?
- What alternatives existed?
- What should be done differently?

## Planned Tools

| Tool | Description |
|---|---|
| `replay_session(session_id)` | Step-by-step session replay |
| `find_failure_point(session_id)` | Identify where things went wrong |
| `analyze_decisions(session_id)` | Review decision points |
| `suggest_alternatives(failure_point)` | What else could have been done |
| `generate_postmortem(session_id)` | Structured failure analysis |

## Data Sources

- `core/memory/sessions/` — session logs
- `mcp/working` — task state snapshots
- `mcp/learner` — error logs and patterns
- `mcp/historian` — cross-session analytics

## Status

🔲 Planned — requires session logging infrastructure
