# Class 10 — Vibe-Coding Prompt Cards

These prompts are intentionally written in terms of **desired behavior** rather
than Streamlit syntax.

## Prompt 1 — Inspect before editing

> Inspect this repository. Do not modify any files. Identify which existing
> files contain the approved optimization logic, which function/tool should be
> reused by a manager-facing interface, and how you would add a thin Streamlit
> interface without duplicating or modifying the optimization model. Give me a
> short implementation plan only.

### What to check before proceeding

- Did the agent identify `revenue_management_model.py` as protected analytical logic?
- Does the plan reuse the existing solver function/tool?
- Does it propose a UI layer rather than a new LP?

---

## Prompt 2 — Build Version 1

> Implement the minimal Streamlit interface you proposed. It should let a
> manager change remaining capacity on the four flight legs and compare the
> resulting optimal revenue with the base case. Show solver status, scenario
> revenue, and revenue difference from baseline. Use full city-pair names in
> the visible interface. Reuse the approved optimization backend and do not
> modify or duplicate the LP formulation.

Run the app with:

```bash
py -m streamlit run app.py
```

On macOS use `python3 -m streamlit run app.py`.

---

## Prompt 3 — Improve the manager view

> The interface works. Improve it for a manager without changing the optimizer.
> Show baseline and scenario revenue side by side, emphasize the revenue change,
> and add a table containing only booking decisions that change materially.
> Keep the interface simple and decision-focused.

---

## Prompt 4 — Add analytical traceability

> Add a compact "Scenario Inputs Used" section based on the values returned by
> the approved backend, not merely the values displayed in the form. Also make
> binding flight legs and their shadow prices available in a secondary section.
> Do not change any protected analytical file.

---

# Optional iteration challenges

Pick **one** in the second build round.

### A. Reset

> Add a Reset to Baseline control that restores all four capacity inputs to their
> base values. Do not change backend logic.

### B. Binding legs

> Make binding flight legs easy for a manager to identify, but keep the interface
> visually simple.

### C. Advanced demand input

> Add an "Advanced Scenario Inputs" section that lets the user modify one selected
> itinerary/fare-class demand forecast. Use only demand changes already supported
> by the approved backend.

### D. Download

> Add a CSV download of the scenario comparison results. Do not duplicate the
> optimization model.

### E. Explanation

> Add a concise manager-facing interpretation below the numerical results. Base
> factual claims only on returned solver evidence, and do not invent business
> recommendations that are not supported by the model.
