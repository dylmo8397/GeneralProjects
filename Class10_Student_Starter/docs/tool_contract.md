# Scenario Tool Contract

## Approved command

Run the deterministic optimizer through:

```bash
py scenario_tool.py
```

On macOS, replace `py` with `python3`.

The default output is structured JSON so an AI agent can inspect it reliably.

## Base case

```bash
py scenario_tool.py
```

Human-readable version:

```bash
py scenario_tool.py --pretty
```

Expected base revenue:

`182280`

## Capacity changes

Syntax:

```bash
py scenario_tool.py --capacity LEG=VALUE
```

Example:

```bash
py scenario_tool.py --capacity BC=180
```

To compare with the base case:

```bash
py scenario_tool.py --capacity BC=180 --compare-base
```

Expected scenario revenue for `BC=180`:

`179040`

Expected revenue change:

`-3240`

## Demand changes

Syntax:

```bash
py scenario_tool.py --demand ITINERARY,CLASS=VALUE
```

Example:

```bash
py scenario_tool.py --demand BL,Q=40
```

Multiple updates can be supplied by repeating flags:

```bash
py scenario_tool.py \
  --capacity BC=180 \
  --capacity CL=170 \
  --demand BL,Q=40 \
  --demand BL,Y=15 \
  --compare-base
```

## Invalid inputs

Examples:

```bash
py scenario_tool.py --capacity XX=180
py scenario_tool.py --capacity BC=-10
```

The tool should return a structured `INPUT_ERROR`. The agent must report the
error rather than silently modifying the request.

## JSON output

A normal optimal result includes:

- `status`
- `objective`
- `inputs_used`
- `bookings`
- `leg_load`
- `capacity_slack`
- `shadow_prices`
- `binding_legs`

A comparison result includes:

- `baseline`
- `scenario`
- `comparison`
  - `baseline_objective`
  - `scenario_objective`
  - `objective_change`
  - `booking_changes`

## Evidence rule

An agent may claim a numerical optimum only after obtaining it from this
approved tool and confirming `status = OPTIMAL`.
