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

st.subheader("Remaining capacity")
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

current_inputs = tuple((leg, capacities[leg]) for leg in base_data["legs"])
previous_inputs = st.session_state.get("submitted_inputs")
if previous_inputs is not None and previous_inputs != current_inputs:
    st.session_state.pop("scenario_result", None)
    st.session_state.pop("submitted_inputs", None)

if st.button("Run scenario", type="primary", use_container_width=True):
    with st.spinner("Optimizing the scenario…"):
        try:
            st.session_state["scenario_result"] = solve_revenue_management(
                capacity_updates=capacities,
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
    st.info("Set the remaining capacities, then run the scenario.")
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

    solved_capacity = scenario.get("inputs_used", {}).get("capacity")
    if solved_capacity:
        st.markdown("**Scenario actually solved**")
        st.table(
            [
                {
                    "Flight leg": LEG_LABELS[leg],
                    "Remaining capacity": solved_capacity[leg],
                }
                for leg in base_data["legs"]
            ]
        )
