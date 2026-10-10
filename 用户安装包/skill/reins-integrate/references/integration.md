# Reins integration reference for this kit

This reference covers the Reins pilot version. Before changing customer code, check that the installed Reins package supports the API shown here. Python 3.10+ is required.

## First choice: observe an existing task

```python
from reins import configure, record_outcome, trace

configure(storage_path="/private/path/pilot.duckdb", mode="observe")

@trace(agent_name="my_agent", task_type="my_business_task", policy_version="pilot-v1")
async def run_task(data):
    result = await existing_agent(data)
    record_outcome(success=existing_business_validator(result))
    return result
```

Configure once before concurrent work. Use a separate DuckDB writer per file. Within this trace, supported Anthropic Messages and OpenAI Chat Completions `.create` paths are auto-instrumented; framework callbacks and OTel observe but cannot guarantee admission. Native Gemini is not auto-patched. The local HTTP proxy is experimental observation only. `record_retry()` is for actual application retries; `record_external_cost()` reports a fee after it occurs and does not pre-authorize spending. A process-local dashboard may be enabled with `dashboard=True`; it binds to loopback and is read only.

## Explicit paid operation and multi-Agent control

The control service uses `from reins.control import Client, workflow, bind_context`. A real customer deployment uses separate operator and worker credentials. The operator provisions policies and tasks; a trusted worker binds to a registered task. The examples in this kit use a local operator token only to keep the demo small.

```python
with workflow(client=client, customer_id="customer-id", task_type="my-task",
              budget="0.50", mode="observe") as run:
    result = run.call(execute, model="provider/model", category="model",
                      max_cost="0.05", operation_inputs={"id": item_id})
    run.finish(accepted=existing_business_validator(result))
```

`execute` must return `(JSON-serializable result, actual USD cost)`. For async work use `await run.acall(...)` with an async `execute`. `max_cost` is a conservative complete upper bound, including internal retries and nested charges. Unknown provider charges stay pending for reconciliation. Wrap paid tools as well as model calls if their cost should enter the task budget. Use `run.task(...)` for child work; pass exported context through queues and `bind_context` in a trusted worker. `write_state`, `handoff`, `receive_handoff` and `read_state` record versioned transfers; they do not prove semantic understanding.

Only after the customer reviews an observe-mode baseline may they choose `mode="enforce"` for new tasks. SDK strict admission additionally requires exact pinned prices, a trusted complete input token counter, finite output bounds, and approved same-provider alternatives. Provider retries must be accounted for. Control cannot stop or refund a request already sent. Never use demo prices or a constant token counter for customer enforcement. If no complete bound is available, remain in observe mode and state the limitation.

## What to verify

- Same input, prompt, business output and external side effects before and after integration.
- The complete task and any child tasks appear once; business outcome comes from the application validator.
- Captured costs match returned usage or explicit actual-cost calculation; unknown amounts remain pending.
- No key, raw prompt, customer source data or ledger is committed or uploaded.
- The integration note identifies exact commands to run and revert the patch.
