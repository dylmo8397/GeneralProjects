---
name: compare-scenarios
description: Compare an approved East-West Airlines capacity or demand scenario with the base case using the repository's deterministic scenario tool. Do not use for unsupported model changes.
---

# Compare Scenarios

Follow this workflow exactly.

## Inputs

Identify the user's requested:

- capacity updates; and/or
- mean-demand updates.

If required numerical values are missing, ask for clarification.

Do not invent a model change or business preference.

## Workflow

1. Read `docs/tool_contract.md` if the command syntax is unclear.
2. Run the approved `scenario_tool.py` with `--compare-base`.
3. Check the baseline and scenario statuses.
4. If either is not `OPTIMAL`, report the status and stop the comparison.
5. Report:
   - scenario inputs used;
   - baseline objective;
   - scenario objective;
   - objective change;
   - major nonzero booking changes.
6. Keep tool evidence distinct from managerial interpretation.

## Final checks

- Never fabricate an optimal value.
- Never silently change fares, constraints, or the network.
- State the scenario actually solved.
