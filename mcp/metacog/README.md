# metacog (Planned)

Metacognitive monitor for the SINT agent — error pattern analysis, drift alerts, self-assessment.

## Purpose

The Metacognitive Monitor watches the agent's own behavior patterns and alerts when:
- Error rates increase
- Register distribution drifts
- Confidence calibration degrades
- Same mistakes repeat

## Planned Tools

| Tool | Description |
|---|---|
| `monitor_session()` | Analyze current session for issues |
| `get_error_trend()` | Error rate over time |
| `calibration_check()` | "Was my confidence accurate?" |
| `drift_alert()` | Register distribution anomalies |
| `self_assessment()` | Overall metacognitive health |

## Integration Points

- `mcp/learner` — error patterns and improvements
- `mcp/working` — epistemic state and beliefs
- `mcp/historian` — drift detection and analytics
- `core/memory` — register distribution analysis

## Status

🔲 Planned — requires aggregated data from learner + historian + working
