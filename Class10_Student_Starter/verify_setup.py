from __future__ import annotations

import importlib
import sys


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"[ OK ] {message}")


def main() -> None:
    required = ["gurobipy", "pandas", "streamlit"]
    missing = []

    for package in required:
        try:
            module = importlib.import_module(package)
            version = getattr(module, "__version__", "installed")
            ok(f"{package}: {version}")
        except Exception:
            missing.append(package)

    if missing:
        fail(
            "Missing package(s): " + ", ".join(missing) +
            ". Install the missing package(s) in the same Python environment."
        )

    try:
        from revenue_management_model import solve_revenue_management
    except Exception as exc:
        fail(f"Could not import the approved optimization backend: {exc}")

    try:
        base = solve_revenue_management(output_flag=0)
    except Exception as exc:
        fail(f"Base-case solve failed: {exc}")

    if base.get("status") != "OPTIMAL":
        fail(f"Base case did not return OPTIMAL. Status: {base.get('status')}")

    if abs(base["objective"] - 182280.0) > 1e-4:
        fail(f"Unexpected base revenue: {base['objective']}")
    ok("Base case: OPTIMAL, revenue = $182,280")

    try:
        scenario = solve_revenue_management(
            capacity_updates={"BC": 180},
            output_flag=0,
        )
    except Exception as exc:
        fail(f"BC=180 scenario solve failed: {exc}")

    if scenario.get("status") != "OPTIMAL":
        fail(f"BC=180 scenario did not return OPTIMAL. Status: {scenario.get('status')}")

    if abs(scenario["objective"] - 179040.0) > 1e-4:
        fail(f"Unexpected BC=180 revenue: {scenario['objective']}")

    delta = scenario["objective"] - base["objective"]
    if abs(delta + 3240.0) > 1e-4:
        fail(f"Unexpected revenue change: {delta}")

    ok("BC=180 scenario: revenue = $179,040; change = -$3,240")
    print("\nEnvironment and analytical backend are ready for Class 10.")


if __name__ == "__main__":
    main()
