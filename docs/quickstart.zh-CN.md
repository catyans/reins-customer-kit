# 快速上手：看清一个真实任务的全过程

这份指南写给已有多步骤 Python Agent、且能访问 Reins 私有仓库的工程师。第一次接入建议和 Reins 工程师一起预留约一小时。

## 1. 安装 Reins

使用 Python 3.10+ 和虚拟环境。接受 `catyans/reins` 私有仓库邀请后，从仓库安装试用版：

```bash
git clone git@github.com:catyans/reins.git /path/to/reins
python -m pip install /path/to/reins
```

模型密钥继续放在原有的密钥管理位置。为这次试用新建本地数据库；不要让两个 Reins 进程同时写入同一个文件。

## 2. 选一个任务，先说清什么叫“做得好”

挑一个输入明确、结果能由团队检查的任务，先保存几组代表性输入的原始输出。再商定什么结果算可用，比如必填字段齐全、资料来源可核对。程序没有报错，不代表任务做成了。

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

任务开始前只配置一次 Reins。用 `step()` 标出应用本来就知道的步骤。在这个任务里，受支持的 OpenAI Chat Completions 和 Anthropic Messages 调用会自动记录。其他模型或框架见[接入指南](integration.zh-CN.md)。

## 3. 运行和查看

用相同输入分别运行接入前后的代码，确认 prompt、结果和对外操作没有变化。Agent 运行时，可以打开 `http://127.0.0.1:8765` 看本地时间线。结束后执行：

```bash
reins compare --database ./pilot.duckdb --task-type supplier_lookup
```

在同一处查看任务步骤、模型调用、应用报告的重试、结果是否合格，以及已知和待核对的费用。基础任务记录默认不保存完整 prompt。若以后使用控制工作流，另一个数据库可能保存输入和输出；使用前先决定保存多久、由谁访问。

## 4. 再决定是否需要预算控制

模型、工具以及多 Agent 共享预算的接入方法见[接入指南](integration.zh-CN.md)。先一起确定每次付费操作最多可能花多少钱、价格是否核实、允许使用哪些模型和工具，以及任务停止时保留什么。控制工作流先用观察模式跑；看过真实记录和建议后，再为新任务开启执行控制。只有经过 Reins 的调用会受到控制。

## 暂停或撤回试用

如果只接入了观察功能，移除新增的 `configure`、`@trace`、`step` 和结果记录调用，再重启 Agent。控制工作流可以让**新任务**回到观察模式，或恢复原来的调用路径；已在运行的任务不会因此改变。待核对费用查清后，再按团队的保留政策处理本地记录。

第一次复盘时，对比原来的业务结果、接入后记录的调用与费用。对外只分享团队同意的材料。
