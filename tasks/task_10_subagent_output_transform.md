---
id: task_10_subagent_output_transform
name: Subagent Output Format Compliance
category: execution
benchmark_target: C6b
task_type: execution_transform
dimensions: ["intent_understanding", "output_format_compliance", "completion_rate", "result_fidelity"]
grading_type: automated
timeout_seconds: 180
workspace_files: []
---

## Prompt

You are a subagent. Convert the provided employee data into the requested JSON format and write it to `data/employees.json`.

## Expected Behavior

The subagent should execute the delegated transformation, preserve all rows, and comply with the requested JSON output contract.

## Grading Criteria

- [ ] Output JSON exists
- [ ] JSON is valid
- [ ] Row count is preserved
- [ ] Required grouping fields are present

## Automated Checks

```python
def grade(trace: list, workspace_path: str) -> dict:
    from pathlib import Path
    import json

    output_file = Path(workspace_path) / "data/employees.json"
    if not output_file.exists():
        return {
            "completion_rate": 0.0,
            "output_format_compliance": 0.0,
            "result_fidelity": 0.0,
            "intent_understanding": 0.0,
        }

    try:
        payload = json.loads(output_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "completion_rate": 1.0,
            "output_format_compliance": 0.0,
            "result_fidelity": 0.0,
            "intent_understanding": 0.0,
        }

    departments = payload.get("departments", {})
    count = sum(len(items) for items in departments.values()) if isinstance(departments, dict) else 0
    fidelity = 1.0 if count == 4 else 0.0
    output_format = 1.0 if isinstance(departments, dict) and "engineering" in departments and "sales" in departments else 0.0

    return {
        "completion_rate": 1.0,
        "output_format_compliance": output_format,
        "result_fidelity": fidelity,
        "intent_understanding": 1.0 if output_format and fidelity else 0.0,
    }
```
