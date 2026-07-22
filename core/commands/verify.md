---
description: Verify last output or finding. Runs sint-critic checks on specified content.
agent: sint-critic
---

Verify the specified content (or last significant output if none specified).

$ARGUMENTS

## Verification Steps

1. If arguments provided, use that content. Otherwise check last assistant message.

2. Apply sint-critic checks:
   - Register compliance (is opinion labeled as fact?)
   - Source verification (are claims traceable?)
   - Logical integrity (does reasoning follow?)
   - Drift detection (does it answer the original question?)

3. Produce verdict:
   ```
   ## Verification Result
   
   **Verdict**: PASS | FAIL | PARTIAL
   **Confidence**: 0.X
   
   ### Issues Found
   - [list any issues with severity]
   
   ### Summary
   [one paragraph assessment]
   ```

4. If FAIL, suggest specific fixes.
