# subagent-bench

一个面向多 agent 系统的 benchmark 基线仓库，重点补 `PinchBench` 还没有单独测清楚的两部分：

- `C6a: Main-Agent Delegation / Orchestration`
- `C6b: Subagent Execution`

这个仓库刻意借鉴了 `PinchBench` 最值得复用的设计：

- 任务仍然用 Markdown + YAML frontmatter 定义，方便评审和扩任务。
- 评分优先走自动化检查，保证复现性。
- 允许继续沿用 workspace 文件模拟，而不是一开始就接真实外部系统。

同时它补了几件 `PinchBench` 目前没有显式建模的能力：

- 把 `main agent` 的任务拆解、委托决策、委托说明质量、结果回收与 replan 单独打分。
- 把 `subagent execution` 单独建成可自动评分的任务集。
- 引入结构化 orchestration trace，而不是只看最终文件。
- 把“主 agent 分配错了”和“subagent 执行差了”分开归因。

## 当前实现

当前仓库已经包含一个可跑的双层 benchmark 基线：

- `tasks/`：沿用 `PinchBench` 风格的任务定义。
- `src/subagent_bench/`：任务加载、trace 读取、自动评分、CLI。
- `examples/traces/`：`C6a + C6b` 示例 trace。
- `examples/workspaces/`：与示例 trace 对应的输出工件。
- `tests/`：基础回归测试。
- `docs/`：`PinchBench` 借鉴/改进分析，以及 benchmark 设计文档。

## Orchestration Trace 约定

本仓库默认从离线 trace 评分，不直接绑定某个 agent runtime。trace 可以是单个 JSON 对象，或 JSONL 事件流。

推荐事件类型：

- `delegate`：主 agent 发起委托
- `subagent_result`：子 agent 返回结果
- `replan`：主 agent 在失败或新信息后重新规划
- `verification`：主 agent 对冲突结果做二次核验
- `assistant_message`：主 agent 或子 agent 的自然语言消息
- `tool_use` / `tool_result`：用于 `C6b` 执行质量评分
- `artifact_written`：写入关键输出

示例 `delegate` 事件：

```json
{
  "type": "delegate",
  "delegation_id": "backend-audit",
  "assignee": "repo_searcher",
  "instruction": "Audit backend changes and write reports/backend_findings.md",
  "inputs": ["src/backend", "docs/api-contract.md"],
  "constraints": ["Do not modify source files"],
  "success_criteria": ["List breaking changes", "Reference file paths"],
  "output_path": "reports/backend_findings.md"
}
```

## 为什么不直接复刻 PinchBench

`PinchBench` 非常适合作为基线，但如果目标是评估 subagent 系统，直接照搬会有两个缺口：

1. 它更像 end-to-end agent benchmark，本质上主要覆盖了 `S1`。
2. 它默认主 agent 已经拆对了、派对了、说明白了，不足以回答 orchestration 本身的质量。

所以更合理的路线是：

- 先保留 `PinchBench` 的任务定义和自动评分思想。
- 再把 orchestration 事件与指标加进来。
- 等真的需要 runtime 级观测或 agent tree 分析时，再决定是否拆成独立框架。

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
.venv/bin/python -m pip install --upgrade pip setuptools wheel
pip install -e ".[dev]"
python -m subagent_bench.cli list-tasks
python -m subagent_bench.cli validate-traces --traces-dir examples/traces
python -m subagent_bench.cli grade --traces-dir examples/traces --workspace-root examples/workspaces
pytest
```

## 当前任务集

- `task_01_delegate_or_not`
  - `C6a / T1`，测是否该委托。
- `task_05_avoid_redundant_delegation`
  - `C6a / T2`，测单层拆分的冗余控制。
- `task_07_single_layer_decomposition`
  - `C6a / T2`，测 2-4 个子任务的完整拆分。
- `task_08_dependency_aware_decomposition`
  - `C6a / T3`，测依赖顺序与错误并行。
- `task_02_parallel_research`
  - `C6a / T4`，测并行识别与整合。
- `task_04_fixed_subagent_spec_quality`
  - `C6a / T5`，固定 subagent，只测 delegation spec。
- `task_03_replan_after_failure`
  - `C6a / T6`，测失败恢复与 replan。
- `task_06_verify_conflicting_results`
  - `C6a / T7`，测冲突结果下的验证与最终裁决。
- `task_09_subagent_code_search`
  - `C6b`，测意图理解、工具使用和结果保真。
- `task_10_subagent_output_transform`
  - `C6b`，测输出格式与结果保真。
- `task_11_subagent_error_handling`
  - `C6b`，测异常恢复与降级。

## 当前能力

- 按任务评分 orchestration trace
- 按任务评分 subagent execution trace
- 校验 trace schema
- 输出任务级、benchmark target 级、task type 级、dimension 级汇总
- 输出系统级指标：`end_to_end_task_success`、`over_delegation_rate`、`under_delegation_rate`、`execution_normalized_delegation_score`
- 支持后续接入 `judge_result`

## 文档

- [PinchBench 分析](docs/pinchbench-analysis.md)
- [Benchmark 设计](docs/benchmark-design.md)

## 下一步建议

如果你后面要接真实 runtime，我建议优先补这几项：

- trace exporter：把真实主 agent / subagent 事件导出为这里的结构。
- runtime cost / latency 采集：补齐系统级效率指标。
- execution-normalized delegation score：固定 subagent，只比较 main agent 的委托质量。
- 双层评分：`delegation_score` 和 `execution_score` 分开展示，再给一个 end-to-end 总分。
