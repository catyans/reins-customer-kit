"""Key-free two-agent handoff demo; requires `reins control serve` locally."""

import argparse
from pathlib import Path
from uuid import uuid4

from reins.control import Client, bind_context, workflow


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--token-file", default="~/.reins/control.token")
    parser.add_argument("--url", default="http://127.0.0.1:8795")
    args = parser.parse_args()
    client = Client(args.url, token_file=Path(args.token_file).expanduser())
    reviewer_id = str(uuid4())
    handoff_id = str(uuid4())
    with workflow(
        client=client,
        customer_id="pilot-example",
        task_type="supplier-review",
        workflow_id=str(uuid4()),
        budget="0.20",
        mode="observe",
    ) as run:
        with run.task(task_id=reviewer_id, budget="0.05") as reviewer:
            reviewer_context = reviewer.export_context()
        with run.task(budget="0.08") as collector:
            source = collector.call(
                lambda: ({"supplier": "Example Supplier", "country": "US"}, "0.003"),
                model="demo/simulated-lookup",
                category="model",
                max_cost="0.01",
                operation_inputs={"supplier": "Example Supplier"},
                validator=lambda value: bool(value.get("country")),
                validation_name="country_present",
            )
            state = collector.write_state(
                "supplier-source", source, expected_version=0, source="collector"
            )
            collector.handoff(
                reviewer_id,
                goal="Check the supplier record",
                inputs={"required_fields": ["supplier", "country"]},
                completed=["collect"],
                state_name="supplier-source",
                version=state["version"],
                handoff_id=handoff_id,
            )
        with bind_context(reviewer_context, client=client) as reviewer:
            reviewer.receive_handoff(handoff_id, version=state["version"])
            reviewed = reviewer.read_state("supplier-source")
        accepted = bool(reviewed["payload"].get("country"))
        run.finish(accepted=accepted)
        print({"workflow_id": run.context["workflow_id"], "accepted": accepted})


if __name__ == "__main__":
    main()
