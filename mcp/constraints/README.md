# constraints (Planned)

Hard/soft limit tracker with conflict detection for the SINT agent.

## Purpose

The Constraint Tracker manages the agent's operational boundaries:
- **Hard constraints**: Cannot violate (safety, security, ethics)
- **Soft constraints**: Should respect (preferences, conventions, style)
- **Conflicts**: Detect when constraints contradict each other

## Planned Tools

| Tool | Description |
|---|---|
| `add_constraint(type, rule, source)` | Register a constraint |
| `check_constraints(action)` | Verify action against all constraints |
| `detect_conflicts()` | Find contradictory constraints |
| `list_constraints(type)` | List all constraints by type |
| `relax_constraint(id, reason)` | Temporarily relax a soft constraint |

## Constraint Types

```json
{
  "id": "c01",
  "type": "hard|soft",
  "rule": "Never execute destructive commands without confirmation",
  "source": "AGENTS.MD §1.1",
  "domains": ["bash", "action"],
  "active": true
}
```

## Status

🔲 Planned — requires integration with AGENTS.MD and agent configs
