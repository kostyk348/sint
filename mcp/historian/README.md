# sint-historian-mcp

Cross-session work analyst for the [SINT](https://github.com/kostyk348/sint-ua-v2.1) agent ecosystem.

Provides session statistics, project timelines, pattern search, drift detection, and work reports. Integrates with [sint-memory](https://github.com/kostyk348/sint-ua-v2.1) for structured memory analysis.

## Purpose

The agent works across many sessions. Historian answers: **What did I work on? How productive was I? Where are the patterns?**

## Tools

### Session Analytics

| Tool | Description |
|---|---|
| `session_stats(project)` | Stats: session count, duration, blocks written |
| `work_report(period)` | Human-readable work summary |
| `productivity_trend()` | Activity over time (blocks/day, commits/day) |

### Pattern Detection

| Tool | Description |
|---|---|
| `find_patterns(query)` | Search for recurring themes across sessions |
| `project_timeline(project)` | Chronological project activity |
| `drift_analysis()` | Check if focus is drifting from core projects |

### Cross-Session Queries

| Tool | Description |
|---|---|
| `search_history(query)` | Full-text search across all session logs |
| `compare_periods(a, b)` | Compare two time periods |
| `idle_detection()` | Find gaps and inactive periods |

## Architecture

```
sint-memory blocks + session logs → Historian analyzers → Reports
                                            ↓
                               reporters/ (markdown, JSON, terminal)
```

## Setup

```bash
pip install fastmcp
```

## Run

```bash
python server.py    # stdio mode
```

## Example

```python
# What did I work on this week?
work_report(period="this_week")

# Show project timeline
project_timeline(project="sint-devflow-mcp")

# Find patterns
find_patterns(query="crypto implementation")

# Am I drifting?
drift_analysis()
# → "80% of recent sessions on sint-*, only 20% on DSO core"
```

## Integration

Works with [sint-memory](https://github.com/kostyk348/sint-ua-v2.1) hash-chain blocks and session logs. Call at session boundaries for analytics.

## License

MIT
