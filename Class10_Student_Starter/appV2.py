from __future__ import annotations

import streamlit as st

from revenue_management_model import load_base_data, solve_revenue_management
from scenario_tool import compare_results


LEG_LABELS = {
    "BC": "Boston → Chicago",
    "NC": "New York → Chicago",
    "CS": "Chicago → San Francisco",
    "CL": "Chicago → Los Angeles",
}

ITINERARY_LABELS = {
    "BC": "Boston → Chicago",
    "BS": "Boston → San Francisco",
    "BL": "Boston → Los Angeles",
    "NC": "New York → Chicago",
    "NS": "New York → San Francisco",
    "NL": "New York → Los Angeles",
    "CS": "Chicago → San Francisco",
    "CL": "Chicago → Los Angeles",
}

FARE_CLASS_LABELS = {
    "Q": "Discounted",
    "Y": "Unrestricted",
}


@st.cache_data(show_spinner=False)
def solve_base_case():
    return solve_revenue_management(output_flag=0)


st.set_page_config(
    page_title="East-West Capacity Planner",
    page_icon="✈️",
    layout="centered",
)

st.title("East-West Capacity Planner")
st.write(
    "Compare a remaining-capacity scenario with the approved base plan. "
    "Enter the seats still available on each flight leg."
)

try:
    base_data = load_base_data()
    baseline = solve_base_case()
except Exception as exc:
    st.error(f"The optimization service could not start: {exc}")
    st.stop()

if baseline.get("status") != "OPTIMAL":
    st.error(
        "The base case did not solve to optimality "
        f"(solver status: {baseline.get('status', 'UNKNOWN')})."
    )
    st.stop()


def reset_capacity_inputs():
    for leg in base_data["legs"]:
        st.session_state[f"capacity_{leg}"] = float(base_data["capacity"][leg])
    st.session_state.pop("scenario_result", None)
    st.session_state.pop("submitted_inputs", None)


st.subheader("Remaining capacity")
st.button("Reset to Baseline", on_click=reset_capacity_inputs)
columns = st.columns(2)
capacities = {}
for index, leg in enumerate(base_data["legs"]):
    with columns[index % 2]:
        capacities[leg] = st.number_input(
            LEG_LABELS[leg],
            min_value=0.0,
            value=float(base_data["capacity"][leg]),
            step=1.0,
            key=f"capacity_{leg}",
        )

demand_updates = {}
with st.expander("Advanced Scenario Inputs"):
    override_demand = st.checkbox(
        "Modify one demand forecast",
        help="The approved model supports changing mean-demand forecasts.",
    )
    if override_demand:
        demand_keys = sorted(base_data["demand"])
        selected_demand_key = st.selectbox(
            "Itinerary and fare class",
            options=demand_keys,
            format_func=lambda key: (
                f"{ITINERARY_LABELS[key[0]]} — {FARE_CLASS_LABELS[key[1]]}"
            ),
        )
        itinerary, fare_class = selected_demand_key
        demand_updates[selected_demand_key] = st.number_input(
            "Mean-demand forecast",
            min_value=0.0,
            value=float(base_data["demand"][selected_demand_key]),
            step=1.0,
            key=f"demand_{itinerary}_{fare_class}",
        )

current_inputs = (
    tuple((leg, capacities[leg]) for leg in base_data["legs"]),
    tuple(sorted(demand_updates.items())),
)
previous_inputs = st.session_state.get("submitted_inputs")
if previous_inputs is not None and previous_inputs != current_inputs:
    st.session_state.pop("scenario_result", None)
    st.session_state.pop("submitted_inputs", None)

if st.button("Run scenario", type="primary", use_container_width=True):
    with st.spinner("Optimizing the scenario…"):
        try:
            st.session_state["scenario_result"] = solve_revenue_management(
                capacity_updates=capacities,
                demand_updates=demand_updates,
                output_flag=0,
            )
            st.session_state["submitted_inputs"] = current_inputs
        except Exception as exc:
            st.session_state["scenario_result"] = {
                "status": "INPUT_ERROR",
                "error": str(exc),
            }
            st.session_state["submitted_inputs"] = current_inputs

scenario = st.session_state.get("scenario_result")

if scenario is None:
    st.info("Set the scenario inputs, then run the scenario.")
else:
    st.divider()
    st.subheader("Scenario results")

    status = scenario.get("status", "UNKNOWN")
    if status == "OPTIMAL":
        comparison = compare_results(baseline, scenario)
        revenue_change = comparison["objective_change"]

        st.success(f"Solver status: {status}")
        baseline_col, scenario_col = st.columns(2)
        baseline_col.metric(
            "Baseline revenue",
            f"${comparison['baseline_objective']:,.0f}",
        )
        scenario_col.metric(
            "Scenario revenue",
            f"${comparison['scenario_objective']:,.0f}",
        )

        st.markdown("### Revenue impact")
        st.metric("Change from baseline", f"${revenue_change:+,.0f}")

        binding_legs = scenario.get("binding_legs", [])
        if binding_legs:
            st.warning(
                "**Flight legs at capacity:** "
                + " · ".join(LEG_LABELS[leg] for leg in binding_legs)
            )
        else:
            st.success("No flight legs are at capacity in this scenario.")

        st.markdown("### Booking decisions that change")
        booking_rows = []
        for key, change in sorted(
            comparison["booking_changes"].items(),
            key=lambda item: abs(item[1]),
            reverse=True,
        ):
            itinerary, fare_class = key.split(",", 1)
            booking_rows.append(
                {
                    "Itinerary": ITINERARY_LABELS[itinerary],
                    "Fare class": FARE_CLASS_LABELS.get(fare_class, fare_class),
                    "Baseline": f"{baseline['bookings'][key]:,.1f}",
                    "Scenario": f"{scenario['bookings'][key]:,.1f}",
                    "Change": f"{change:+,.1f}",
                }
            )

        if booking_rows:
            st.dataframe(
                booking_rows,
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.info("No booking decisions change materially in this scenario.")
    else:
        st.error(f"The scenario did not solve to optimality. Solver status: {status}")
        if scenario.get("error"):
            st.write(scenario["error"])

    inputs_used = scenario.get("inputs_used", {})
    solved_capacity = inputs_used.get("capacity")
    solved_demand_updates = inputs_used.get("demand_updates", {})
    if solved_capacity:
        st.markdown("### Scenario Inputs Used")
        st.dataframe(
            [
                {
                    "Flight leg": LEG_LABELS[leg],
                    "Remaining capacity": f"{solved_capacity[leg]:,.0f} seats",
                }
                for leg in base_data["legs"]
            ],
            hide_index=True,
            use_container_width=True,
        )
        if solved_demand_updates:
            st.markdown("**Demand forecast override**")
            st.dataframe(
                [
                    {
                        "Itinerary": ITINERARY_LABELS[key.split(",", 1)[0]],
                        "Fare class": FARE_CLASS_LABELS.get(
                            key.split(",", 1)[1],
                            key.split(",", 1)[1],
                        ),
                        "Mean-demand forecast": f"{value:,.0f} bookings",
                    }
                    for key, value in solved_demand_updates.items()
                ],
                hide_index=True,
                use_container_width=True,
            )

    if status == "OPTIMAL":
        with st.expander("Binding flight legs and shadow prices"):
            if binding_legs:
                st.dataframe(
                    [
                        {
                            "Binding flight leg": LEG_LABELS[leg],
                            "Shadow price": (
                                f"${scenario['shadow_prices'][leg]:,.0f} per seat"
                            ),
                        }
                        for leg in binding_legs
                    ],
                    hide_index=True,
                    use_container_width=True,
                )
            else:
                st.write("No flight legs are binding in this scenario.")
