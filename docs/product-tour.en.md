# Reins, screen by screen

[Open the live workspace](https://47.245.114.167:8443/app/#research) · [简体中文](product-tour.zh-CN.md)

These are screenshots of the public Reins workspace, captured on October 10, 2026. It contains saved Agent runs on example inputs. Recorded API costs are estimates, not provider invoices. In a customer trial, your workflows and run data remain in your own environment. Some controls shown here require an operator in a private workspace.

## Work: Task workspace

![Task workspace with saved tasks and a selected multi-Agent result](images/task-workspace.png)

Start with a task your team recognizes. Select a saved run to see its business result alongside the work that produced it. The example above is a four-team review of 720 order rows; other saved cases include research, support, content, and data checks. The left list lets you switch tasks without losing their records.

![Run analysis with cost by Agent](images/run-analysis.png)

Further down that same task, **Run analysis** answers where its recorded API spend went. It shows model calls, received handoffs, and a cost breakdown by Agent. Download the run summary when you need to share the review. The amounts are usage-based estimates.

![Execution replay showing event controls and the current event](images/replay.png)

**Replay execution** walks through saved events without running the Agent again. Use Play, Previous, Next, or the slider to inspect the point where a task spent money, handed work to another Agent, or stopped. Expand **Recorded data** for the event's saved details.

![Ask AI dialog for questions about one recorded run](images/ask-ai.png)

**Ask AI** is scoped to the selected run. You can ask which Agent did which work or why the task stopped. It receives a short record of states, calls, handoffs, and estimated costs; raw prompts and source documents are not sent. Check important answers against the execution record.

## Observe: Overview and Runs

![Overview with recorded cost, attention count, trend, and task distribution](images/overview.png)

**Overview** is the first stop for a team lead: current recorded spend, results that need review, a spending trend, and the tasks behind the total. The demo has no accepted results yet, so cost per accepted result and acceptance rate show a dash rather than a made-up number.

![Runs table with task, deployment, configuration, and status](images/runs.png)

**Runs** is the searchable execution list. Filter by time, customer, team, or workflow, then open a task to inspect its steps and recorded costs. Use this when a specific run was slow, expensive, or produced an unexpected result.

## Understand: Attribution and Exceptions

![Attribution grouped by customer, with recorded cost and task count](images/attribution.png)

**Attribution** groups spend by customer, team, task type, task, model, or tool. Switch the grouping to answer who incurred a cost, then export the table as CSV. Revenue and margin are blank until you supply business data; Reins does not infer them from API charges.

![Exceptions queue with shared-budget alerts and decision history](images/exceptions.png)

**Exceptions** gathers decisions that need attention. In this demo, several child tasks reached a shared budget. Open one to see the affected task and the recorded decision. Acknowledging an alert records that it was seen; it does not restart the task.

## Control: Budgets, Policies, and Experiments

![Budgets page showing empty period-budget and shared-pool states](images/budgets.png)

**Budgets** is where a private workspace sets period limits or a shared pool for concurrent work. The public demo has no period budget or shared pool configured, so the screenshot shows the setup state. A task budget can still govern an individual example run.

![Policies table with task budgets and repeat and failure limits](images/policies.png)

**Policies** shows the rules assigned to new tasks: budget, repeat limit, failure limit, and what to do when progress stalls. A running task keeps the policy version it started with, so a later edit does not silently change that run.

![Experiments page with adapters and no reviewed comparison yet](images/experiments.png)

**Experiments** is for comparing execution configurations on the same frozen inputs after expected results are reviewed and a worker is registered. The demo lists available adapters but has no completed experiment to report. This page is where a team would compare quality before judging cost per accepted result.

## Operate: Approvals and Settings

![Quality review comparing the original task input with the observed output](images/quality-review.png)

**Approvals → Quality review** places the original input beside the saved output. A reviewer can record what result was expected and make an explicit decision. A completed process alone does not mean the business result was accepted.

![Handoffs table showing sender, recipient, goal, and state version](images/handoffs.png)

**Approvals → Handoffs** follows work passed between Agents: sender, recipient, goal, state version, and receipt. A receipt shows that state was transferred; it does not prove the receiving Agent understood it correctly. The **Operation approvals** tab is where protected actions appear when a worker requests them.

![Settings page with integration and invoice-reconciliation sections](images/settings.png)

**Settings** covers the workspace connection, Agent worker setup, provider invoice reconciliation, and business cost or revenue entries. Provider credentials stay with the worker. Private-workspace configuration and access depend on your deployment.

To connect one of your own tasks, continue with the [quickstart](quickstart.en.md). For the supported SDK and explicit-call paths, see the [integration guide](integration.en.md).
