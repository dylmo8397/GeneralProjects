---
name: explain-solution
description: Explain a tool-backed East-West Airlines optimization result to a manager using concise business language. Use only after obtaining solver evidence from the approved scenario tool.
---

# Explain Optimization Result

## Workflow

1. Obtain the relevant result from `scenario_tool.py` if it has not already been obtained.
2. Confirm solver status.
3. Explain:
   - scenario inputs;
   - objective revenue;
   - binding flight legs / bottlenecks;
   - important booking changes if comparing scenarios.
4. Distinguish facts from interpretation.
5. Do not imply that the deterministic LP captures all booking uncertainty.

## Output style

Use concise managerial language.
Avoid raw solver jargon unless it helps the decision.
Do not call a result optimal unless the tool returned `OPTIMAL`.
