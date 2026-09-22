from __future__ import annotations

import argparse
import json
import sys

from revenue_management_model import solve_revenue_management


def parse_capacity(items):
    updates = {}
    for item in items or []:
        try:
            leg, raw = item.split("=", 1)
            updates[leg.strip()] = float(raw)
        except Exception as exc:
            raise ValueError(
                f"Invalid --capacity value '{item}'. Use LEG=VALUE, e.g. BC=180."
            ) from exc
    return updates


def parse_demand(items):
    updates = {}
    for item in items or []:
        try:
            lhs, raw = item.split("=", 1)
            itinerary, fare_class = [x.strip() for x in lhs.split(",", 1)]
            updates[(itinerary, fare_class)] = float(raw)
        except Exception as exc:
            raise ValueError(
                "Invalid --demand value "
                f"'{item}'. Use ITINERARY,CLASS=VALUE, e.g. BL,Q=40."
            ) from exc
    return updates


def compact_result(result):
    """Keep comparison output readable for an agent and for classroom display."""
    keep = [
        "status",
        "objective",
        "inputs_used",
        "bookings",
        "leg_load",
        "capacity_slack",
        "shadow_prices",
        "binding_legs",
    ]
    return {k: result[k] for k in keep if k in result}


def compare_results(base, scenario):
    comparison = {
        "baseline_status": base["status"],
        "scenario_status": scenario["status"],
    }

    if base["status"] == "OPTIMAL" and scenario["status"] == "OPTIMAL":
        comparison["baseline_objective"] = base["objective"]
        comparison["scenario_objective"] = scenario["objective"]
        comparison["objective_change"] = scenario["objective"] - base["objective"]

        booking_changes = {}
        keys = sorted(set(base["bookings"]) | set(scenario["bookings"]))
        for key in keys:
            delta = scenario["bookings"].get(key, 0.0) - base["bookings"].get(key, 0.0)
            if abs(delta) > 1e-6:
                booking_changes[key] = delta
        comparison["booking_changes"] = booking_changes

    return comparison


def print_pretty(payload):
    """Human-readable view used by the instructor before the live agent demo."""
    if "baseline" in payload:
        print("BASELINE")
        print("-" * 60)
        print_pretty(payload["baseline"])
        print("\nSCENARIO")
        print("-" * 60)
        print_pretty(payload["scenario"])
        print("\nCOMPARISON")
        print("-" * 60)
        comp = payload["comparison"]
        for k, v in comp.items():
            print(f"{k}: {v}")
        return

    print(f"Status: {payload.get('status')}")
    if payload.get("status") != "OPTIMAL":
        if "error" in payload:
            print(f"Error: {payload['error']}")
        return

    print(f"Objective revenue: ${payload['objective']:,.2f}")
    print(f"Binding legs: {', '.join(payload['binding_legs'])}")
    print("Shadow prices:")
    for leg, value in payload["shadow_prices"].items():
        print(f"  {leg}: ${value:,.2f}")
    print("Inputs used:")
    print(json.dumps(payload["inputs_used"], indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Approved East-West Airlines optimization scenario tool."
    )
    parser.add_argument(
        "--capacity",
        action="append",
        default=[],
        help="Capacity update LEG=VALUE. Repeat flag for multiple legs.",
    )
    parser.add_argument(
        "--demand",
        action="append",
        default=[],
        help="Demand update ITINERARY,CLASS=VALUE. Repeat flag for multiple products.",
    )
    parser.add_argument(
        "--compare-base",
        action="store_true",
        help="Solve the baseline and the requested scenario and report the difference.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print a human-readable report instead of JSON.",
    )
    args = parser.parse_args()

    try:
        capacity_updates = parse_capacity(args.capacity)
        demand_updates = parse_demand(args.demand)

        scenario = solve_revenue_management(
            capacity_updates=capacity_updates,
            demand_updates=demand_updates,
            output_flag=0,
        )

        if args.compare_base:
            base = solve_revenue_management(output_flag=0)
            payload = {
                "baseline": compact_result(base),
                "scenario": compact_result(scenario),
                "comparison": compare_results(base, scenario),
            }
        else:
            payload = compact_result(scenario)

    except Exception as exc:
        payload = {
            "status": "INPUT_ERROR",
            "error": str(exc),
        }

    if args.pretty:
        print_pretty(payload)
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))

    if payload.get("status") == "INPUT_ERROR":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
