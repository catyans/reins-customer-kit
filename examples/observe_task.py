"""Key-free observation demo. Inputs and the $0.002 fee are synthetic."""

import argparse

from reins import configure, record_external_cost, record_outcome, step, trace
from reins.core.decorators import shutdown


@trace(agent_name="supplier_agent", task_type="supplier_lookup", policy_version="pilot-v1")
def lookup_supplier(name: str) -> dict:
    with step("Read source", kind="retrieval"):
        source = {"name": name, "country": "US"}
    with step("Validate result"):
        accepted = bool(source["name"] and source["country"])
    record_external_cost("0.002", label="simulated source fee")
    record_outcome(success=accepted, score=1.0 if accepted else 0.0)
    return source


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", default="/tmp/reins-pilot.duckdb")
    args = parser.parse_args()
    configure(storage_path=args.database, mode="observe")
    try:
        print(lookup_supplier("Example Supplier"))
        print(f"Local record: {args.database}")
    finally:
        shutdown()


if __name__ == "__main__":
    main()
