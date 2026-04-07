---
id: task_07_single_layer_decomposition
name: Single-Layer Task Decomposition
category: orchestration
benchmark_target: C6a
task_type: T2
dimensions: ["task_decomposition_quality", "assignment_accuracy", "delegation_spec_completeness"]
grading_type: automated
timeout_seconds: 240
workspace_files: []
---

## Prompt

Break a medium-complexity launch-prep request into 2 to 4 independent subproblems. The main agent should delegate each slice once, avoid gaps and overlap, and merge the results into `reports/launch_plan.md`.

## Expected Behavior

The main agent should decompose the task into a small set of complete, non-redundant subproblems. Each delegation should own a distinct scope and output path. The final launch plan should reflect all delegated areas.

## Grading Criteria

- [ ] Delegation count stays within 2 to 4
- [ ] Delegated scopes are distinct
- [ ] Delegation specs are complete
- [ ] Final launch plan integrates all delegated outputs

## Automated Checks

```python
def grade(trace: list, workspace_path: str) -> dict:
    from pathlib import Path
    from subagent_bench.orchestration_checks import delegate_events, delegation_fields_present

    delegations = delegate_events(trace)
    right_count = 1.0 if 2 <= len(delegations) <= 4 else 0.0
    unique_outputs = len({event.get("output_path") for event in delegations})
    distinct_scopes = 1.0 if delegations and unique_outputs == len(delegations) else 0.0
    complete_specs = 1.0 if delegations and all(delegation_fields_present(event) for event in delegations) else 0.0

    artifact = Path(workspace_path) / "reports/launch_plan.md"
    integrated = 0.0
    if artifact.exists():
        content = artifact.read_text(encoding="utf-8").lower()
        integrated = 1.0 if "frontend readiness" in content and "backend readiness" in content and "docs readiness" in content else 0.0

    return {
        "decomposition_count_in_range": right_count,
        "distinct_decomposition_scopes": distinct_scopes,
        "delegation_spec_completeness": complete_specs,
        "decomposition_integration": integrated,
    }
```
