# East-West Airlines Model Specification

## Purpose

Determine the revenue-maximizing number of reservations to accept for each
westbound itinerary and fare class using a deterministic LP.

This is the approved analytical model for the Class 9 agent-harness demo.

## Sets

Flight legs:

- `BC`: Boston → Chicago
- `NC`: New York → Chicago
- `CS`: Chicago → San Francisco
- `CL`: Chicago → Los Angeles

Itineraries:

- `BC`, `BS`, `BL`, `NC`, `NS`, `NL`, `CS`, `CL`

Fare classes:

- `Q`: discounted/restricted
- `Y`: unrestricted

## Decision variables

For itinerary `i` and fare class `f`:

`x[i,f]` = number of accepted reservations.

Variables are continuous and nonnegative in this deterministic LP.

## Objective

Maximize total fare revenue:

`sum_i sum_f fare[i,f] * x[i,f]`

## Capacity constraints

For every flight leg `l`:

`sum_i sum_f a[l,i] * x[i,f] <= capacity[l]`

where `a[l,i] = 1` when itinerary `i` uses leg `l`.

## Demand constraints

For every itinerary/fare-class pair:

`x[i,f] <= mean_demand[i,f]`

The model uses mean demand as a deterministic upper bound.

## Base-case reference results

With the provided CSV data:

- Optimal revenue: **$182,280**
- All four flight legs are binding.
- Capacity shadow prices:
  - BC = $160
  - NC = $250
  - CS = $160
  - CL = $200

These values are for instructor reference and can also be reproduced by
running the approved tool.

## Important limitation

This LP is a deterministic planning approximation. It does not itself model
the sequential stochastic arrival process of bookings. In Class 7, its shadow
prices were used to motivate bid-price controls.

Class 9 focuses on how an AI agent should use this already-approved analytical
model, not on changing its formulation.
