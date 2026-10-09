---
name: reins-integrate
description: Integrate Reins into one existing Python Agent workflow for a customer pilot. Use when asked to add task tracing, outcome recording, or opt-in runtime cost control to customer Agent code.
---

# Integrate one customer workflow with Reins

Work in the customer's repository. Reins is a separate private Python dependency; this skill does not grant access or install it. Read `references/integration.md` for the supported paths and API details before editing.

1. Inspect the repository's instructions, dependency versions, Agent entrypoint, provider calls, task boundaries, existing quality check and tests. Identify one complete business task, including any child Agents and paid tool calls. If the task boundary or acceptance check cannot be determined from code, ask for that information; do not invent success.
2. Preserve existing prompts, provider selection, business output and side effects. Start with `mode="observe"`. For supported OpenAI Chat Completions or Anthropic Messages calls, configure Reins once at process startup and add `@trace` around the complete task, explicit `step` calls only where the app knows a stage, and `record_outcome` based on the existing validator. For native Gemini or custom paid calls, use an explicit `Workflow.call`/`acall` only where the application can provide an honest maximum and actual charge; otherwise record the task boundary and explain the missing call-level cost.
3. Keep all credentials, raw customer inputs, provider responses and local ledgers in the customer environment. Do not upload them, print secrets, or place them in committed fixtures. Reins controls only calls routed through it. Do not silently enable `enforce`, change models, disable retries, deploy, or run paid experiments. If the customer explicitly asks for enforcement, use the reviewed baseline and the prerequisites in the reference first.
4. Run the smallest relevant existing tests and one key-free sample or mocked task. Compare original and instrumented business outputs and side effects. If tests cannot run, report the exact reason. Leave a concise `REINS_INTEGRATION.md` in the customer repository: which workflow changed, whether it observes or controls calls, which costs are covered, how it was tested, how to inspect a run, and how to undo the change. Do not include secrets or customer records.

For unsupported language, provider method or framework behavior, stop at a precise integration note rather than fabricating interception. Keep the patch scoped to the selected task.
