---
description: Start session with memory context. Reads state, recent blocks, greets with summary.
agent: sint-main
---

Read the memory system and present session context:

1. Use `memory_read_state` to get current focus and pending decisions
2. Use `memory_get_chain_tail` with n=5 to see recent activity
3. Use `memory_stats` to get system stats

Present to user:
```
## Session Start

**Focus**: [list current focus items]
**Pending**: [list unresolved decisions]  
**Recent**: [last 1-2 significant blocks]
**Memory**: [X blocks, Y chain entries]

Continue or switch to something else?
```

If state.json is empty or missing, say so and ask what to work on.
