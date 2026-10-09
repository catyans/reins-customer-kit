# Choose how to connect your Agent

Start with the path your Agent already uses. You only need to change the calls you want Reins to see. Reins requires Python 3.10+.

| Your current setup | Start by observing | To control spending later |
| --- | --- | --- |
| OpenAI Chat Completions `.create` or Anthropic Messages `.create` | `configure(mode="observe")` + `@trace` + application outcome check | Verified prices, complete input token bound, finite output bound, approved same-provider models, then opt-in enforce. |
| Native Gemini or custom paid API/tool | Wrap each paid operation with `Workflow.call` / `acall` in observe mode | Supply a conservative `max_cost` that includes internal retries, actual returned cost and usage, and opt in after review. |
| LangChain, CrewAI, OpenAI Agents callbacks, or OTel | Callback observation can supplement task tracing | Callbacks alone are not an admission gate; add an explicit paid-call path for control. |
| HTTP proxy | Experimental observation only | Use a supported SDK or explicit Workflow for control. |

Use [observe_task.py](../examples/observe_task.py) for a no-key SDK pattern and [control_task.py](../examples/control_task.py) for a no-key explicit call. The control example needs a locally running `reins control serve` service. [multi_agent.py](../examples/multi_agent.py) shows real child tasks and a versioned handoff. All example prices are simulated.

[provider_patterns.py](../examples/provider_patterns.py) has copyable OpenAI Chat Completions, Anthropic Messages, and native Gemini explicit-call functions. Pass your existing clients or provider adapter; no key is stored in the file. Its simple nonempty-text checks are placeholders: replace them with your business acceptance rule. The Gemini adapter must return actual usage and an actual-cost calculation based on verified rates.

## What changes in your code

The [before](../examples/customer_before.py) and [after](../examples/customer_after.py) functions use the **same provider callable, prompt, and returned business value**. The after version receives a Reins Workflow and calls `workflow.acall` around the already-existing provider operation. The provider must return actual usage and cost, or the application must calculate them from verified rates. `max_cost` must be an upper bound, not a typical average. The application supplies the acceptance check; a saved response is not automatically accepted.

For an SDK-only first pilot, wrap the complete task and record `record_outcome(success=...)`. `record_retry()` describes an actual application retry. `record_external_cost()` reports an already incurred fee; it is not an admission guard. Do not add the same provider charge twice through both SDK instrumentation and an explicit call. Reins suppresses nested SDK admission inside an explicit call, but the integration must still bound the full nested charge.

## Running the explicit examples

In another terminal, start the customer-local control service:

```bash
reins control serve
```

Then run:

```bash
python examples/control_task.py --token-file ~/.reins/control.token
python examples/multi_agent.py --token-file ~/.reins/control.token
```

These scripts create example workflows through the local operator credential and do not make provider requests. In customer production, use separate operator and worker credentials, provision tasks and policies through the operator, and give a trusted worker only its worker credential. Do not expose the loopback service publicly. The product console and customer code should run in the customer's environment.

## Checks before using it on real work

- Identity: identify customer, task type, policy version and parent/child task. Pass `operation_inputs` that describe the actual request for exact-repeat detection.
- Outcome: record a customer-defined validator; finish the root workflow with `accepted=True` only when its business result passed. Review partial results separately.
- Accounting: provider list prices are estimates until reconciled to real bills. Include tool, evaluation, infrastructure and human-review costs when calculating unit economics. A timeout with unknown charge stays reserved.
- Recovery: a rejected call does not execute; an already dispatched request cannot be unbilled. Do not automatically retry an uncertain paid operation. Multi-Agent handoff records a versioned state transfer, not proof that the receiver understood it.
- Scope: only instrumented calls are governed. Cross-host shared budgets, arbitrary framework methods and unsupported provider features are outside this pilot path. See the matching private Reins version's README before enabling strict control.
