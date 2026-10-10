# Try Reins with one of your Agent workflows

[简体中文](README.zh-CN.md) · [English handbook](docs/pdf/reins-pilot-en.pdf) · [中文手册](docs/pdf/reins-pilot-zh-CN.pdf)

**Customer install pack:** [integration skill and private repository access](用户安装包/).

When an Agent keeps working, it can be hard to tell which calls were useful, what the whole task cost, or whether the result was good enough. Reins puts those answers around the **task**, so your team can inspect the run and decide where spending should continue or stop.

This kit helps you try Reins on one existing Python workflow. The first run only records what happens. After you have seen your own task history, you can decide whether to add budget rules.

## See the product

[![Reins task workspace showing saved Agent tasks and a multi-Agent review](docs/images/task-workspace.png)](https://47.245.114.167:8443/app/#research)

The [public demo](https://47.245.114.167:8443/app/#research) lets you open a saved task, inspect its result, and replay what happened. The pictured inputs are examples; the displayed API costs are recorded estimates. Your own trial runs and data stay in your environment.

![Run analysis showing API cost, model calls, handoffs, and cost by Agent](docs/images/run-analysis.png)

This is the view to use when someone asks, “What did this task cost, and which Agent spent it?” The [visual product tour](docs/product-tour.en.md) walks through every screen, including cost attribution, budgets, quality review, and the execution replay.

## Start here

Reins itself is in a private repository. Ask your Reins contact for read-only access to `catyans/reins`, then install it in a Python 3.10+ virtual environment:

```bash
git clone git@github.com:catyans/reins.git /path/to/reins
python -m pip install /path/to/reins
```

From this kit, run a local example without an API key:

```bash
python examples/observe_task.py --database /tmp/reins-pilot.duckdb
reins compare --database /tmp/reins-pilot.duckdb --task-type supplier_lookup
```

The example uses a made-up task and fee. For a useful trial, follow the [quickstart](docs/quickstart.en.md) to record one of your own tasks and its acceptance result. You can then see its steps, model calls, costs and outcome together. Your prompts and run data stay in your environment.

## What to read next

| Guide | When to use it |
| --- | --- |
| [Quickstart](docs/quickstart.en.md) | Connect one task, inspect a run and undo the change. |
| [Visual product tour](docs/product-tour.en.md) | See every page of the current web workspace and what you can do there. |
| [Integration guide](docs/integration.en.md) | Choose the right connection for your model provider and Agent framework. |
| [Examples](examples/) | Copy a small working pattern or compare code before and after integration. |
| [Integration skill](用户安装包/skill/reins-integrate/SKILL.md) | Have Codex or Claude Code prepare a small patch for your repository. |

Every guide also has a Chinese version. The short PDF handbooks are ready to share with a teammate who prefers to read offline.

## Adapt your code with the integration skill

From this kit's directory, run:

```bash
./scripts/install-skill.sh --target /absolute/path/to/customer-repo --assistant both
```

Use `--assistant codex` or `--assistant claude` if you only use one assistant. The script copies the skill into your repository; it does not change your Agent code. In Codex, ask for `$reins-integrate`; in Claude Code, use `/reins-integrate`. The assistant will inspect one workflow, add observation where the code supports it, and leave a note explaining the change. Review the patch and your business success check before using it. Run `./scripts/install-skill.sh --help` for removal instructions.

Reins records calls that you connect to it. Observation does not block spending. Budget control is a separate step that needs your approval and reliable cost bounds; the [integration guide](docs/integration.en.md) explains the supported paths. Recorded API costs may still need checking against provider bills.

This kit is open source under Apache-2.0. For access or help with a trial, contact the person who invited you to the private Reins repository. Please keep API keys and customer data out of public issues.

## Build the PDF handbooks

The ready-to-read files are in [docs/pdf](docs/pdf/). To rebuild them from [LaTeX sources](docs/tex/) with XeLaTeX, `latexmk`, `ctex` and Chinese fonts installed, run `latexmk -xelatex -output-directory=tmp/pdfs docs/tex/reins-pilot-en.tex` and repeat with `docs/tex/reins-pilot-zh-CN.tex`.
