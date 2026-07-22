---
description: End session. Write summary, update state, verify chain.
agent: sint-main
---

End the current session gracefully:

1. Ask user: "Ready to close? Any final notes?"

2. Use `memory_write_session` to log session_end with summary:
   - What was accomplished
   - What blocks were created
   - Any decisions made

3. Use `memory_update_state` to save:
   - Current focus (what to continue next)
   - Any new pending decisions
   - Update last_session to current date

4. Use `memory_verify_chain` for a quick integrity check

5. Present to user:
   ```
   Session saved.
   Next time: [specific continuation point]
   Blocks created this session: [count]
   Chain status: [valid/any issues]
   
   Anything to add before we close?
   ```
