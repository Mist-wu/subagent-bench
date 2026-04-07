# Benchmark Design

## 目标

这个仓库聚焦一个更窄、也更容易被现有 benchmark 忽略的问题：

`main agent` 是否能正确判断何时委托、如何拆解任务、如何写出高质量委托，以及如何在 subagent 失败后重规划。

## 基本原则

### 1. 主 agent 能力单独评估

这个库优先测：

- delegation policy
- task decomposition
- prompt packaging for subagents
- integration and recovery

它不假设 subagent execution 已经天然正确。

### 2. 自动评分优先

每个任务都应尽量用确定性规则评分，例如：

- delegation 数量
- 是否缺字段
- 是否提前集成
- 是否存在重复委托
- 是否发生 replan
- 关键 artifact 是否存在且包含必要字段

### 3. 任务必须能映射到真实 agent 失败模式

任务不是为了“做难题”，而是为了覆盖真实多 agent 失败模式：

- 过度委托
- 漏委托
- 重复委托
- 依赖顺序错误
- 委托说明不完整
- 子任务失败后停摆
- 子任务结果冲突时不会校验

## 当前任务维度

- `delegation_policy`
- `parallelization`
- `spec_quality`
- `replanning`
- `integration`
- `verification`

## 当前任务集

### task_01_delegate_or_not

测主 agent 是否只把昂贵部分委托出去。

### task_02_parallel_research

测主 agent 是否识别两个互相独立的研究流，并在两边返回后再集成。

### task_03_replan_after_failure

测 subagent 第一次失败后，主 agent 是否补上下文并重试。

### task_04_fixed_subagent_spec_quality

固定 subagent，只看主 agent 委托说明质量是否足以让 subagent 独立完成。

### task_05_avoid_redundant_delegation

测主 agent 是否避免把高度重叠的问题派给多个 subagent 重复做。

### task_06_verify_conflicting_results

测两个 subagent 返回冲突结论时，主 agent 是否会做验证，而不是直接拼接。

## Trace 契约

最小 trace bundle 结构：

```json
{
  "events": [
    {"type": "delegate", "...": "..."},
    {"type": "subagent_result", "...": "..."},
    {"type": "artifact_written", "...": "..."}
  ]
}
```

可选字段：

- `judge_result`
- `timestamp`
- `agent`
- `metadata`

## 结果解释

建议同时看三层结果：

1. 任务分数
2. 维度平均分
3. end-to-end 成功率

如果后续引入真实 subagent execution，可以进一步拆出：

- `delegation_score`
- `execution_score`
- `integration_score`
