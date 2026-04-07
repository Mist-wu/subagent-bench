---
id: task_05_avoid_redundant_delegation
name: Avoid Redundant Delegation
category: orchestration
benchmark_target: C6a
task_type: T2
dimensions: ["task_decomposition_quality", "delegation_decision_accuracy"]
grading_type: automated
timeout_seconds: 180
workspace_files: []
---

## Prompt

The main agent needs code search findings for a single backend migration area. A bad orchestration policy would spawn multiple overlapping subagents that all inspect the same scope. A good policy should either keep the work local or issue one focused delegation.

## Expected Behavior

The main agent should avoid duplicate delegation over the same scope. One focused delegation is acceptable; multiple overlapping delegations are not.

## Grading Criteria

- [ ] No overlapping delegations are created
- [ ] Delegation count stays minimal
- [ ] Final artifact is produced
- [ ] Final artifact cites a single consistent scope

## Automated Checks

```python
def grade(trace: list, workspace_path: str) -> dict:
    from pathlib import Path
    from subagent_bench.orchestration_checks import delegate_events

    delegations = delegate_events(trace)
    scopes = [tuple(event.get("inputs", [])) for event in delegations]
    unique_scopes = len(set(scopes))

    no_overlap = 1.0 if len(delegations) == unique_scopes else 0.0
    minimal_count = 1.0 if len(delegations) <= 1 else 0.0

    artifact = Path(workspace_path) / "reports/backend_migration_findings.md"
    artifact_exists = 1.0 if artifact.exists() else 0.0

    consistent_scope = 0.0
    if artifact.exists():
        content = artifact.read_text(encoding="utf-8").lower()
        consistent_scope = 1.0 if "backend migration" in content and "single search pass" in content else 0.0

    return {
        "no_overlapping_delegations": no_overlap,
        "minimal_delegation_count": minimal_count,
        "artifact_exists": artifact_exists,
        "consistent_scope": consistent_scope,
    }
```
