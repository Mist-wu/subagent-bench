---
id: task_01_delegate_or_not
name: Delegate Only The Expensive Slice
category: orchestration
benchmark_target: C6a
task_type: T1
dimensions: ["delegation_decision_accuracy", "delegation_spec_completeness", "integration_quality"]
grading_type: automated
timeout_seconds: 180
workspace_files: []
---

## Prompt

Review a release checklist that contains one trivial action and one expensive repo-wide audit. The main agent should handle the trivial rename itself, but it should delegate the repo-wide audit to a subagent and then integrate the result into `answer.md`.

## Expected Behavior

The main agent should create exactly one delegation for the expensive audit, provide enough context for the subagent to finish independently, and avoid delegating the trivial work. After the subagent returns, the main agent should synthesize the audit into the final answer.

## Grading Criteria

- [ ] Exactly one delegation is created
- [ ] Delegation spec contains goal, inputs, success criteria, and output path
- [ ] Delegated artifact is produced
- [ ] Main agent integrates the delegated result into `answer.md`

## Automated Checks

```python
def grade(trace: list, workspace_path: str) -> dict:
    from subagent_bench.orchestration_checks import (
        artifact_contains,
        artifact_exists,
        delegate_events,
        delegation_fields_present,
    )

    delegations = delegate_events(trace)
    only_one = 1.0 if len(delegations) == 1 else 0.0
    complete_spec = 1.0 if delegations and delegation_fields_present(delegations[0]) else 0.0
    delegated_artifact = 1.0 if artifact_exists(workspace_path, "reports/dependency_audit.md") else 0.0
    integrated = 1.0 if artifact_contains(
        workspace_path,
        "answer.md",
        ["dependency audit", "reports/dependency_audit.md", "rename handled directly"],
    ) else 0.0

    return {
        "delegates_when_needed": only_one,
        "avoids_over_delegation": only_one,
        "delegation_spec_completeness": complete_spec,
        "delegated_artifact_exists": delegated_artifact,
        "integration_quality": integrated,
    }
```
