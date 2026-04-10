# subagent-bench

[English](README.md) | [中文](README_CN.md)

多智能体编排能力基准测试。用于回答：哪个模型最适合做主 Agent、哪个最适合做子 Agent、哪个能同时胜任两者。

## 为什么需要

传统基准测试只评估单 Agent 端到端表现。`subagent-bench` 专注于它们忽略的维度：

- **C6a（编排能力）** — 任务分解、委派、并行调度、失败重规划、结果整合
- **C6b（执行能力）** — 子 Agent 工具调用、输出正确性、异常处理

其中 `C6b` 的 live 题默认要求主代理通过 OpenClaw 原生 `sessions_spawn` 启动真实子会话来完成 leaf work，而不是让主会话“扮演 subagent”。

一个模型可能执行力很强但编排能力差，反之亦然。本基准帮你区分。

## 快速开始

```bash
# 安装（需要 Python 3.11+）
pip install -e ".[dev]"

# 离线评分（基于已有 trace）
subagent-bench grade \
  --traces-dir examples/traces \
  --workspace-root examples/workspaces

# 在线基准测试
./scripts/run.sh --model anthropic/claude-sonnet-4
```

## 命令行参数

| 参数 | 说明 |
|---|---|
| `--model` | 被测模型 |
| `--suite` | `all` 或指定任务 ID |
| `--runs` | 重复运行次数（取均值） |
| `--judge` | 覆盖默认评判模型 |
| `--base-url` | 自定义 OpenAI 兼容接口 |
| `--no-upload` | 跳过结果上传 |

## 解读结果

| 得分模式 | 解读 |
|---|---|
| C6a 高，C6b 低 | 适合用作**主 Agent** |
| C6a 低，C6b 高 | 适合用作**子 Agent** |
| 两项都高 | **统一模型**候选 |

## 任务集

| 任务 | 评测维度 | 说明 |
|---|---|---|
| `task_01` | C6a | 委派决策 |
| `task_02` | C6a | 并行委派 |
| `task_03` | C6a | 失败恢复与重规划 |
| `task_04` | C6a | 委派指令质量 |
| `task_05` | C6a | 避免冗余委派 |
| `task_06` | C6a | 冲突结果验证 |
| `task_07` | C6a | 单层分解 |
| `task_08` | C6a | 依赖感知分解 |
| `task_09` | C6b | 代码搜索执行 |
| `task_10` | C6b | 输出格式合规 |
| `task_11` | C6b | 异常处理 |

## 任务格式

每个任务是一个带 YAML frontmatter 的 Markdown 文件：

```yaml
---
id: task_01
benchmark_target: C6a
task_type: T1
dimensions: ["delegation_decision_accuracy"]
grading_type: automated     # automated | llm_judge | hybrid
timeout_seconds: 180
---
```

各 section：`## Prompt`、`## Expected Behavior`、`## Grading Criteria`、`## Automated Checks`、`## LLM Judge Rubric`。

## Trace 格式

Trace 为 JSON，包含 `events` 数组，关键事件类型：

| 事件 | 含义 |
|---|---|
| `delegate` | 主 Agent 向子 Agent 委派任务 |
| `subagent_result` | 子 Agent 返回结果 |
| `replan` | 主 Agent 重新规划 |
| `tool_use` / `tool_result` | 工具调用及返回 |
| `artifact_written` | 产物写入 |
| `verification` | 结果核验 |

## 评分机制

三种模式，通过任务 frontmatter 的 `grading_type` 配置：

- **`automated`** — 每个任务的 `## Automated Checks` 区块内嵌确定性 Python 函数 `grade(trace, workspace_path) → dict`，加权平均得出 `[0.0, 1.0]` 分数。
- **`llm_judge`** — 将任务 prompt、transcript 摘要、rubric 拼成结构化 prompt 发给裁判 LLM，返回 `{"scores": {...}, "total": float}`。所有任务统一三个评分维度：`split_quality`、`delegation_clarity`、`integration_reliability`。
- **`hybrid`** — 两者加权组合，通过 frontmatter 的 `grading_weights` 配置（如 `automated: 0.6`、`llm_judge: 0.4`）。

失败归因分为：**委派失败**、**执行失败**、**整合失败**。

**离线 vs 在线：**

| | 离线（`subagent-bench grade`） | 在线（`scripts/benchmark.py`） |
|---|---|---|
| Trace 来源 | `examples/traces/` 中的预录 JSON | 实时执行 Agent |
| LLM 评判 | 读取 trace 中已嵌入的 `judge_result` | 实时调用裁判 API |
| 适用场景 | 回归测试 | 对真实 Agent 跑完整基准 |

对于 C6a，评分优先消费 transcript 中的原生信号；`delegation_trace.json` 仅作为兼容 fallback。失败恢复既可通过重新委派体现，也可通过主会话本地修复获得部分分。

## 项目结构

```
tasks/              → 基准任务定义
src/subagent_bench/ → 离线评分、模式定义、CLI
scripts/            → 在线测试运行器
examples/           → 示例 trace 与工作区输出
docs/               → 设计文档与结果汇总
tests/              → 回归测试
```

## 文档

- [基准设计](docs/benchmark-design.md)
- [结果汇总模板](docs/result-summary-template.md)
- [PinchBench 分析](docs/pinchbench-analysis.md)
- [任务模板](tasks/TASK_TEMPLATE.md)

## 许可

[MIT](LICENSE)
