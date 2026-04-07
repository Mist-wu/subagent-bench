---
id: task_09_subagent_code_search
name: Subagent Code Search Execution
category: execution
benchmark_target: C6b
task_type: execution_search
dimensions: ["intent_understanding", "tool_use_correctness", "completion_rate", "result_fidelity"]
grading_type: automated
timeout_seconds: 180
workspace_files: []
---

## Prompt

You are a subagent. Search the codebase for deprecated `db.rawQuery()` calls and write a precise report to `reports/raw_query_report.md`.

## Expected Behavior

The subagent should understand the delegated goal, use search tooling correctly, find all targeted occurrences, and produce the requested report without asking the main agent for clarification.

## Grading Criteria

- [ ] Search tool is used
- [ ] Report artifact exists
- [ ] All occurrences are captured
- [ ] Report preserves paths and line numbers

## Automated Checks

```python
def grade(trace: list, workspace_path: str) -> dict:
    from pathlib import Path

    used_search_tool = 1.0 if any(event.get("type") == "tool_use" and event.get("tool") == "rg" for event in trace) else 0.0
    artifact = Path(workspace_path) / "reports/raw_query_report.md"
    artifact_exists = 1.0 if artifact.exists() else 0.0

    fidelity = 0.0
    if artifact.exists():
        content = artifact.read_text(encoding="utf-8").lower()
        fidelity = 1.0 if "src/api/users.ts:14" in content and "src/api/orders.ts:22" in content and "src/api/orders.ts:41" in content else 0.0

    return {
        "tool_use_correctness": used_search_tool,
        "completion_rate": artifact_exists,
        "result_fidelity": fidelity,
        "intent_understanding": 1.0 if artifact_exists and fidelity else 0.0,
    }
```
