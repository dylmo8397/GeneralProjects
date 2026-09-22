# East-West Airlines — Class 10 Interface Build

## Goal for this class

Build a **thin manager-facing Streamlit interface** around the approved
East-West Airlines optimization backend.

The interface may make the optimizer easier to use. It must not silently
change the optimization problem.

## Protected analytical sources of truth

Treat these files as **approved and protected** during the Class 10 build:

- `revenue_management_model.py` — approved Gurobi formulation.
- `scenario_tool.py` — approved scenario command/tool.
- `data/` — approved base fares, demand, capacities, and itinerary-leg mapping.
- `docs/model_spec.md` — approved model specification.
- `docs/tool_contract.md` — approved tool contract.

Do **not** modify, duplicate, or replace the optimization formulation while
building the interface unless the instructor explicitly asks for model
development.

## Allowed interface work

You may create or edit files that implement the user interface, especially:

- `app.py`
- optional UI/helper files if truly useful
- interface documentation

Keep the UI layer thin. It should call the approved backend rather than copy
LP variables, objective terms, or constraints into the interface code.

## Before editing

When asked to build or modify the interface:

1. Inspect the repository first.
2. Identify which existing function/tool should be reused.
3. State a short implementation plan.
4. Do not edit until the user's request authorizes implementation.

## Minimum interface contract

The first working version should let a manager:

- change remaining capacity on the four flight legs;
- compare the scenario with the base case;
- see solver status;
- see optimal revenue and revenue change from baseline.

Use business-facing labels such as `Boston → Chicago`, not only internal codes
such as `BC`.

## Analytical traceability

A polished interface is not enough. The interface must preserve evidence.

- Never display an "optimal" result unless solver status is `OPTIMAL`.
- Make the scenario actually solved visible to the user.
- Prefer showing values from backend `inputs_used`, not merely echoing form fields.
- Do not silently reuse a stale result after inputs change.

## Input and model boundaries

- Capacity inputs must be nonnegative.
- Invalid input should be rejected clearly.
- A valid but unsupported request is not permission to rewrite the model.

Example unsupported request:

> "Protect at least 40 seats for Y-class Boston–Chicago."

The current approved scenario model changes capacities and demand forecasts;
it does not contain a Y-class protection constraint. Explain that boundary
rather than silently adding a new constraint.

## Known-answer regression tests

Use these cases to audit the interface:

### Base case

- Revenue = `$182,280`
- All four flight legs bind.

### BC capacity = 180; all other capacities = 200

- Scenario revenue = `$179,040`
- Revenue change from baseline = `-$3,240`

If the interface does not reproduce these values, investigate before adding
more features.

## Skills

Repo-scoped Class 9 Skills remain under `.agents/skills/` for reference.
They are **not the focus of Class 10**. The core task is vibe-coding and
auditing the interface.
