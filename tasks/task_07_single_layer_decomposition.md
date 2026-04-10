---
id: task_07_single_layer_decomposition
name: Single-Layer Task Decomposition
category: orchestration
benchmark_target: C6a
task_type: T2
dimensions: ["task_decomposition_quality", "assignment_accuracy", "delegation_spec_completeness"]
grading_type: hybrid
timeout_seconds: 300
workspace_files:
  - path: "inputs/frontend_readiness.md"
    content: |
      # Frontend Readiness

      - Accessibility review incomplete.
      - Mobile screenshots missing.
  - path: "inputs/backend_readiness.md"
    content: |
      # Backend Readiness

      - Queue retry metrics missing.
      - Migration rollback rehearsal not documented.
  - path: "inputs/docs_readiness.md"
    content: |
      # Docs Readiness

      - Runbook lacks post-deploy verification steps.
      - Support notes are still in draft.
grading_weights:
  automated: 0.6
  llm_judge: 0.4
automated_weights:
  decomposition_count_in_range: 0.25
  distinct_decomposition_scopes: 0.25
  delegation_spec_completeness: 0.25
  decomposition_integration: 0.25
---

## Prompt

Break a medium-complexity launch-prep request into 2 to 4 independent subproblems. The main agent should delegate each slice once, avoid gaps and overlap, and merge the results into `reports/launch_plan.md`. At minimum, the final plan should cover frontend readiness, backend readiness, and docs readiness.

Prefer leaving native delegation evidence in the transcript. If the runtime cannot surface those events cleanly, write `delegation_trace.json` in the workspace root as a compatibility fallback.

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
    from subagent_bench.orchestration_checks import (
        artifact_contains_score,
        delegate_events,
        delegation_fields_score,
    )

    delegations = delegate_events(trace, workspace_path)
    right_count = 1.0 if 2 <= len(delegations) <= 4 else 0.5 if len(delegations) in {1, 5} else 0.0
    unique_outputs = len({event.get("output_path") for event in delegations})
    distinct_scopes = 1.0 if delegations and unique_outputs == len(delegations) else 0.0
    complete_specs = (
        sum(delegation_fields_score(event) for event in delegations) / len(delegations)
        if delegations else 0.0
    )

    artifact = Path(workspace_path) / "reports/launch_plan.md"
    integrated = 0.0
    if artifact.exists():
        integrated = artifact_contains_score(
            workspace_path,
            "reports/launch_plan.md",
            [
                ["frontend readiness", "frontend"],
                ["backend readiness", "backend"],
                ["docs readiness", "documentation readiness", "docs"],
            ],
        )

    return {
        "decomposition_count_in_range": right_count,
        "distinct_decomposition_scopes": distinct_scopes,
        "delegation_spec_completeness": complete_specs,
        "decomposition_integration": integrated,
    }
```

## LLM Judge Rubric

### Criterion 1: Split Quality
**Score 1.0**: The decomposition covers the problem with 2-4 sensible, non-overlapping subtasks.
**Score 0.5**: The decomposition is partly sensible but has gaps or redundancy.
**Score 0.0**: The decomposition is poor or incoherent.

### Criterion 2: Delegation Clarity
**Score 1.0**: Each delegation clearly defines ownership, inputs, and expected output.
**Score 0.5**: Delegations are understandable but not fully specified.
**Score 0.0**: Delegations are vague or confusing.

### Criterion 3: Integration Reliability
**Score 1.0**: The final launch plan accurately integrates all slices.
**Score 0.5**: Integration is partial or weak.
**Score 0.0**: The final plan does not reliably combine the delegated work.
