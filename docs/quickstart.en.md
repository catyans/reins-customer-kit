# Quickstart: see one real Agent task from start to finish

This guide is for an engineer with a multi-step Python Agent and access to the private Reins repository. Plan for about an hour with a Reins engineer the first time.

## 1. Install Reins

Use Python 3.10+ and a virtual environment. After accepting your invitation to `catyans/reins`, install the pilot version from the private repository:

```bash
git clone git@github.com:catyans/reins.git /path/to/reins
python -m pip install /path/to/reins
```

Keep model credentials where you already manage secrets. Create a fresh local database for this trial; do not have two Reins processes write to the same file.

## 2. Pick a task and decide what "good" means

Pick a task with a clear input and a result your team can check. Save its original output for a few representative inputs. Decide what makes the result usable—for example, required fields and checked sources. A function returning without an error is not enough.

```python
from reins import configure, record_outcome, step, trace

configure(storage_path="./pilot.duckdb", mode="observe", dashboard=True)

@trace(agent_name="supplier_agent", task_type="supplier_lookup",
       policy_version="pilot-observe-v1", budget="$0.50")
async def research_supplier(source):
    async with step("collect sources", kind="retrieval"):
        pages = await collect_sources(source)
    async with step("prepare result"):
        result = await existing_agent(pages)
    record_outcome(success=required_fields_and_sources_pass(result))
    return result
```

Configure Reins once before tasks start. Use `step()` for stages your application already knows about. Supported OpenAI Chat Completions and Anthropic Messages calls inside the task are recorded automatically. Other providers and frameworks are covered in the [integration guide](integration.en.md).

## 3. Run and inspect

Run the original and connected versions on the same inputs. Check that prompts, results and outside actions are unchanged. While the Agent is running, open `http://127.0.0.1:8765` to see its local timeline. After the run:

```bash
reins compare --database ./pilot.duckdb --task-type supplier_lookup
```

Look at the task steps, model calls, retries your application reported, result checks, known costs and amounts still to verify. The basic task record does not store full prompts by default. If you later use the control workflow, its separate database may also hold inputs and outputs; choose a retention policy before using it.

![Example of a full-workspace run analysis with cost by Agent](images/run-analysis.png)

This image is from the [public full-workspace demo](product-tour.en.md), where a multi-Agent task shows its calls, handoffs, and estimated cost by Agent. Your first SDK observation run uses the local timeline described above; it will not automatically have every control-workspace panel. The tour shows what you can inspect after connecting the corresponding workflow features.

## 4. Decide whether budget control would help

For paid model or tool calls and shared multi-Agent budgets, follow [the integration guide](integration.en.md). Agree on an upper cost limit for each paid operation, checked prices, allowed models and tools, and what to keep if a task stops. Run the control workflow in observation mode first. Turn on enforcement for new tasks only after reviewing real runs and the suggested decisions. Only connected calls can be controlled.

## Undo or pause the pilot

For observation, remove the added `configure`, `@trace`, `step` and outcome calls, then restart the Agent. For a control workflow, switch **new** tasks back to observation or restore the original call path. A policy change will not alter a task already running. Keep the local record until pending provider charges have been checked, then follow your organization's retention policy.

For the first review, compare the result, recorded calls and costs with the original run. Share only material your team approves.
