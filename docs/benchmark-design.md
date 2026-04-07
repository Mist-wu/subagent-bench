# Benchmark Design

## 二、评测对象

### C6a: Main-Agent Delegation / Orchestration

测主 agent 的任务分配能力：

- 是否该委托
- 如何拆分子任务
- 是否识别依赖与并行关系
- 是否把任务派给正确的 subagent / skill / tool path
- 委托说明是否完整
- subagent 返回后是否整合、校验、补救、replan

### C6b: Subagent Execution

测子 agent 的执行能力：

- 是否正确理解委托意图
- 是否独立使用工具完成任务
- 是否按要求产出结果
- 是否处理异常、超时、缺信息场景

## 三、评测输入与观测信号

除最终输出文件外，必须记录中间过程：

- 是否 spawn subagent
- spawn 数量
- 每个 subtask 的 delegation spec
- subtask 执行顺序与依赖关系
- subagent 返回结果
- 主 agent 的整合与重试行为
- 全部 transcript / tool_use / skill routing 轨迹

没有这些中间信号，就只能测 end-to-end，无法区分“分配错”还是“执行错”。

## 四、核心指标

### C6a 指标

- `delegation_decision_accuracy`
- `task_decomposition_quality`
- `dependency_correctness`
- `assignment_accuracy`
- `delegation_spec_completeness`
- `recovery_replan_quality`
- `integration_quality`
- `result_verification_quality`

### C6b 指标

- `intent_understanding`
- `tool_use_correctness`
- `completion_rate`
- `output_format_compliance`
- `timeout_error_handling`
- `result_fidelity`

### 系统级指标

- `end_to_end_task_success`
- `cost / latency`
- `over_delegation_rate`
- `under_delegation_rate`
- `execution_normalized_delegation_score`

当前仓库已经内置：

- `end_to_end_task_success`
- `over_delegation_rate`
- `under_delegation_rate`
- `execution_normalized_delegation_score`

`cost / latency` 仍依赖接入真实 runtime trace。

## 六、评分方式

### C6a 用 hybrid

自动检查：

- 是否 spawn
- spawn 数量
- delegation spec 字段是否齐全
- 是否按预期依赖执行
- 是否产生重复子任务
- 是否触发 replan

LLM Judge：

- 拆分是否合理
- 委托说明是否清晰
- 结果整合是否可靠

### C6b 用 hybrid / automated

自动检查：

- 文件存在性
- 内容完整性
- 精确匹配路径 / 数字 / 函数名 / 行号
- 工具调用正确性
- 输出格式正确性

LLM Judge：

- 分析质量

当前仓库实现上：

- `C6a` 任务默认使用 `hybrid`
- `C6b` 任务使用 `hybrid / automated` 混合配置
- judge 结果通过 trace 中的 `judge_result` 字段注入

## 七、错误归因规则

失败必须拆成三类：

- `Delegation Failure`
- `Execution Failure`
- `Integration Failure`

当前仓库已经把这三类错误归因内置到评分结果里：

- `C6a` 中与拆分、派发、spec、replan 相关的失败归为 `Delegation Failure`
- `C6b` 中与工具使用、结果保真、异常处理相关的失败归为 `Execution Failure`
- 与整合、验证、最终裁决相关的失败归为 `Integration Failure`

这些归因会进入结果 JSON 的：

- 单任务 `failure_attribution`
- 汇总级 `failure_attribution_counts`

## 五、任务类型

- `T1` 是否委托
- `T2` 单层拆分
- `T3` 依赖型拆分
- `T4` 并行型拆分
- `T5` 委托说明质量
- `T6` 失败恢复
- `T7` 多 subagent 聚合

## 当前任务映射

### C6a

- `task_01_delegate_or_not` -> `T1`
- `task_05_avoid_redundant_delegation` -> `T2`
- `task_07_single_layer_decomposition` -> `T2`
- `task_08_dependency_aware_decomposition` -> `T3`
- `task_02_parallel_research` -> `T4`
- `task_04_fixed_subagent_spec_quality` -> `T5`
- `task_03_replan_after_failure` -> `T6`
- `task_06_verify_conflicting_results` -> `T7`

### C6b

- `task_09_subagent_code_search`
- `task_10_subagent_output_transform`
- `task_11_subagent_error_handling`

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

当前 schema 已支持：

- `delegate`
- `subagent_result`
- `replan`
- `verification`
- `assistant_message`
- `artifact_written`
- `tool_use`
- `tool_result`

## 结果解释

建议同时看四层结果：

1. 单任务分数
2. `benchmark_target_scores`
3. `task_type_scores`
4. `system_metrics`
