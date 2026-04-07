---
id: task_11_subagent_error_handling
name: Subagent Error Handling
category: execution
benchmark_target: C6b
task_type: execution_recovery
dimensions: ["timeout_error_handling", "completion_rate", "result_fidelity"]
grading_type: automated
timeout_seconds: 180
workspace_files: []
---

## Prompt

You are a subagent. A first tool call fails because a source document is missing. Recover by using the fallback document and still write `reports/recovered_summary.md`.

## Expected Behavior

The subagent should detect the failure, switch to the fallback input, and complete the delegated output instead of silently aborting.

## Grading Criteria

- [ ] Failure is observed
- [ ] Fallback action is taken
- [ ] Final report exists
- [ ] Final report reflects the fallback source

## Automated Checks

```python
def grade(trace: list, workspace_path: str) -> dict:
    from pathlib import Path
    from subagent_bench.orchestration_checks import transcript_has_tool_call, transcript_has_tool_result_error

    saw_failure = 1.0 if transcript_has_tool_result_error(trace, "read_primary") else 0.0
    fallback = 1.0 if transcript_has_tool_call(trace, "read_fallback") else 0.0

    artifact = Path(workspace_path) / "reports/recovered_summary.md"
    completion = 1.0 if artifact.exists() else 0.0
    fidelity = 0.0
    if artifact.exists():
        content = artifact.read_text(encoding="utf-8").lower()
        fidelity = 1.0 if "fallback source" in content and "recovered summary" in content else 0.0

    return {
        "timeout_error_handling": 1.0 if saw_failure and fallback else 0.0,
        "completion_rate": completion,
        "result_fidelity": fidelity,
    }
```
