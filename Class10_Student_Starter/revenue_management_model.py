from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple, Optional
import pandas as pd
import gurobipy as gp
from gurobipy import GRB


HERE = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = HERE / "data"


STATUS_NAME = {
    GRB.LOADED: "LOADED",
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.INF_OR_UNBD: "INF_OR_UNBD",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.CUTOFF: "CUTOFF",
    GRB.ITERATION_LIMIT: "ITERATION_LIMIT",
    GRB.NODE_LIMIT: "NODE_LIMIT",
    GRB.TIME_LIMIT: "TIME_LIMIT",
    GRB.SOLUTION_LIMIT: "SOLUTION_LIMIT",
    GRB.INTERRUPTED: "INTERRUPTED",
    GRB.NUMERIC: "NUMERIC",
    GRB.SUBOPTIMAL: "SUBOPTIMAL",
}


def load_base_data(data_dir: Path | str = DEFAULT_DATA_DIR):
    """Load and validate the East-West Airlines CSV files."""
    data_dir = Path(data_dir)

    fares_df = pd.read_csv(data_dir / "fares.csv")
    demand_df = pd.read_csv(data_dir / "demand.csv")
    capacity_df = pd.read_csv(data_dir / "capacity.csv")
    legs_df = pd.read_csv(data_dir / "itinerary_legs.csv")

    required = {
        "fares.csv": (fares_df, {"Itinerary", "FareClass", "Fare"}),
        "demand.csv": (demand_df, {"Itinerary", "FareClass", "MeanDemand"}),
        "capacity.csv": (capacity_df, {"Leg", "Capacity"}),
        "itinerary_legs.csv": (legs_df, {"Itinerary", "Leg"}),
    }

    for filename, (df, cols) in required.items():
        missing = cols - set(df.columns)
        if missing:
            raise ValueError(f"{filename} is missing columns: {sorted(missing)}")

    if (fares_df["Fare"] < 0).any():
        raise ValueError("Fares must be nonnegative.")
    if (demand_df["MeanDemand"] < 0).any():
        raise ValueError("Demand must be nonnegative.")
    if (capacity_df["Capacity"] < 0).any():
        raise ValueError("Capacity must be nonnegative.")

    fare_keys = set(zip(fares_df["Itinerary"], fares_df["FareClass"]))
    demand_keys = set(zip(demand_df["Itinerary"], demand_df["FareClass"]))
    if fare_keys != demand_keys:
        raise ValueError("Fare and demand tables must contain the same itinerary/class keys.")

    itineraries = sorted(fares_df["Itinerary"].unique().tolist())
    fare_classes = sorted(fares_df["FareClass"].unique().tolist())
    legs = capacity_df["Leg"].tolist()

    unknown_itins = set(legs_df["Itinerary"]) - set(itineraries)
    unknown_legs = set(legs_df["Leg"]) - set(legs)
    if unknown_itins:
        raise ValueError(f"Unknown itineraries in itinerary_legs.csv: {sorted(unknown_itins)}")
    if unknown_legs:
        raise ValueError(f"Unknown legs in itinerary_legs.csv: {sorted(unknown_legs)}")

    fare = {
        (row.Itinerary, row.FareClass): float(row.Fare)
        for row in fares_df.itertuples(index=False)
    }
    demand = {
        (row.Itinerary, row.FareClass): float(row.MeanDemand)
        for row in demand_df.itertuples(index=False)
    }
    capacity = {
        row.Leg: float(row.Capacity)
        for row in capacity_df.itertuples(index=False)
    }

    uses_leg = {(leg, itin): 0 for leg in legs for itin in itineraries}
    for row in legs_df.itertuples(index=False):
        uses_leg[(row.Leg, row.Itinerary)] = 1

    return {
        "itineraries": itineraries,
        "fare_classes": fare_classes,
        "legs": legs,
        "fare": fare,
        "demand": demand,
        "capacity": capacity,
        "uses_leg": uses_leg,
    }


def _validate_updates(base, capacity_updates, demand_updates):
    """Validate scenario updates before model construction."""
    capacity_updates = capacity_updates or {}
    demand_updates = demand_updates or {}

    for leg, value in capacity_updates.items():
        if leg not in base["capacity"]:
            raise ValueError(
                f"Unknown flight leg '{leg}'. Valid legs: {base['legs']}"
            )
        if value < 0:
            raise ValueError(f"Capacity for {leg} must be nonnegative.")

    valid_demand_keys = set(base["demand"])
    for key, value in demand_updates.items():
        if key not in valid_demand_keys:
            valid = sorted(f"{i},{f}" for i, f in valid_demand_keys)
            raise ValueError(
                f"Unknown demand key {key}. Valid itinerary/class keys include: {valid}"
            )
        if value < 0:
            raise ValueError(f"Demand for {key} must be nonnegative.")


def solve_revenue_management(
    capacity_updates: Optional[Dict[str, float]] = None,
    demand_updates: Optional[Dict[Tuple[str, str], float]] = None,
    data_dir: Path | str = DEFAULT_DATA_DIR,
    output_flag: int = 0,
):
    """
    Solve one deterministic East-West Airlines scenario.

    Only capacity and mean-demand values are scenario inputs.
    The fare table, itinerary-leg mapping, and mathematical formulation
    are fixed by the approved model specification.
    """
    base = load_base_data(data_dir)
    capacity_updates = dict(capacity_updates or {})
    demand_updates = dict(demand_updates or {})

    _validate_updates(base, capacity_updates, demand_updates)

    capacity = dict(base["capacity"])
    capacity.update(capacity_updates)

    demand = dict(base["demand"])
    demand.update(demand_updates)

    model = gp.Model("East_West_Revenue_Management")
    model.Params.OutputFlag = output_flag
    # Force simplex so LP dual/shadow-price information is consistently available.
    model.Params.Method = 0

    x = model.addVars(
        base["itineraries"],
        base["fare_classes"],
        lb=0.0,
        name="Bookings",
    )

    model.setObjective(
        gp.quicksum(
            base["fare"][i, f] * x[i, f]
            for i in base["itineraries"]
            for f in base["fare_classes"]
        ),
        GRB.MAXIMIZE,
    )

    cap_constr = model.addConstrs(
        (
            gp.quicksum(
                base["uses_leg"][leg, i] * x[i, f]
                for i in base["itineraries"]
                for f in base["fare_classes"]
            )
            <= capacity[leg]
            for leg in base["legs"]
        ),
        name="Capacity",
    )

    model.addConstrs(
        (
            x[i, f] <= demand[i, f]
            for i in base["itineraries"]
            for f in base["fare_classes"]
        ),
        name="Demand",
    )

    model.optimize()

    status = STATUS_NAME.get(model.Status, f"STATUS_{model.Status}")
    result = {
        "status": status,
        "inputs_used": {
            "capacity_updates": capacity_updates,
            "demand_updates": {
                f"{i},{f}": v for (i, f), v in demand_updates.items()
            },
            "capacity": capacity,
        },
    }

    if model.Status != GRB.OPTIMAL:
        return result

    bookings = {
        f"{i},{f}": x[i, f].X
        for i in base["itineraries"]
        for f in base["fare_classes"]
    }

    leg_load = {
        leg: sum(
            base["uses_leg"][leg, i] * x[i, f].X
            for i in base["itineraries"]
            for f in base["fare_classes"]
        )
        for leg in base["legs"]
    }

    shadow_prices = {
        leg: cap_constr[leg].Pi
        for leg in base["legs"]
    }

    capacity_slack = {
        leg: cap_constr[leg].Slack
        for leg in base["legs"]
    }

    result.update(
        {
            "objective": model.ObjVal,
            "bookings": bookings,
            "leg_load": leg_load,
            "capacity_slack": capacity_slack,
            "shadow_prices": shadow_prices,
            "binding_legs": [
                leg for leg in base["legs"]
                if abs(capacity_slack[leg]) <= 1e-6
            ],
        }
    )

    return result
