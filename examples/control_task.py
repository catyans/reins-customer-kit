"""Key-free explicit control demo; requires `reins control serve` locally."""

import argparse
from pathlib import Path
from uuid import uuid4

from reins.control import Client, workflow


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--token-file", default="~/.reins/control.token")
    parser.add_argument("--url", default="http://127.0.0.1:8795")
    args = parser.parse_args()
    client = Client(args.url, token_file=Path(args.token_file).expanduser())
    with workflow(
        client=client,
        customer_id="pilot-example",
        task_type="support-reply",
        workflow_id=str(uuid4()),
        budget="0.10",
        mode="observe",
    ) as run:
        run.progress("Drafting", 0, 1)
        result = run.call(
            lambda: ({"reply": "We received your request."}, "0.004"),
            model="demo/simulated-model",
            category="model",
            max_cost="0.01",
            operation_inputs={"ticket": "example-001"},
            validator=lambda value: bool(value.get("reply")),
            validation_name="reply_present",
        )
        run.progress("Drafting", 1, 1)
        run.finish(accepted=bool(result["reply"]))
        print({"workflow_id": run.context["workflow_id"], "result": result})


if __name__ == "__main__":
    main()
