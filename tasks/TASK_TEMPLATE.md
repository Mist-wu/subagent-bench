---
id: task_xx_name
name: Task Display Name
category: orchestration
benchmark_target: C6a
task_type: T1
dimensions: ["delegation_decision_accuracy"]
grading_type: automated
timeout_seconds: 180
workspace_files: []
---

## Prompt

{给 agent 的真实用户请求。建议明确交代目标、输入、限制和预期输出。}

## Expected Behavior

{描述主 agent 理想的 orchestration 行为：是否应该委托、拆成几个子任务、什么可以并行、什么时候应该回收结果或 replan。}

## Grading Criteria

- [ ] Delegation decision is appropriate
- [ ] Task decomposition is complete
- [ ] Delegation spec includes enough context
- [ ] Final integration is correct

## Automated Checks

```python
def grade(trace: list, workspace_path: str) -> dict:
    return {
        "criterion_name": 1.0,
    }
```

## Additional Notes

- `trace` 是结构化 orchestration 事件列表，不再局限于普通 transcript。
- 推荐事件：`delegate`、`subagent_result`、`replan`、`assistant_message`、`artifact_written`。
- 如果后面要接 judge，可以在 trace 根对象增加 `judge_result`，并把 `grading_type` 改成 `hybrid` 或 `llm_judge`。
- `benchmark_target` 取值建议为 `C6a`、`C6b` 或 `System`。
- `task_type` 目前按 T1-T7 编号。
- `dimensions` 用于后续汇总，例如 `delegation_decision_accuracy`、`dependency_correctness`、`delegation_spec_completeness`、`result_fidelity`。
