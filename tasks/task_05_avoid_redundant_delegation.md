---
id: task_05_avoid_redundant_delegation
name: Avoid Redundant Delegation
category: orchestration
benchmark_target: C6a
task_type: T2
dimensions: ["task_decomposition_quality", "delegation_decision_accuracy"]
grading_type: hybrid
timeout_seconds: 240
workspace_files:
  - path: "docs/migration_scope.md"
    content: |
      # Backend Migration Scope

      Focus only on the backend migration around invoice persistence.
      Avoid duplicate investigation of the same files.
  - path: "src/backend/migration_service.ts"
    content: |
      export function migrateInvoiceRecord(record: { invoiceId?: string }) {
        if (!record.invoiceId) {
          throw new Error("missing invoice id");
        }
        return { migrated: true, invoiceId: record.invoiceId };
      }
grading_weights:
  automated: 0.6
  llm_judge: 0.4
automated_weights:
  no_overlapping_delegations: 0.35
  minimal_delegation_count: 0.25
  artifact_exists: 0.15
  consistent_scope: 0.25
---

## Prompt

The main agent needs code search findings for a single backend migration area. A bad orchestration policy would spawn multiple overlapping subagents that all inspect the same scope. A good policy should either keep the work local or issue one focused delegation that writes `reports/backend_migration_findings.md` and explicitly notes it was done in a single search pass.

Prefer leaving native delegation evidence in the transcript. If the runtime cannot surface those events cleanly, write `delegation_trace.json` in the workspace root as a compatibility fallback.

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
    from subagent_bench.orchestration_checks import artifact_contains_score, delegate_events

    delegations = delegate_events(trace, workspace_path)
    scopes = [tuple(event.get("inputs", [])) for event in delegations]
    unique_scopes = len(set(scopes))

    no_overlap = 1.0 if len(delegations) <= 1 else (unique_scopes / len(delegations))
    minimal_count = 1.0 if len(delegations) <= 1 else 0.0

    artifact = Path(workspace_path) / "reports/backend_migration_findings.md"
    artifact_exists = 1.0 if artifact.exists() else 0.0

    consistent_scope = 0.0
    if artifact.exists():
        consistent_scope = artifact_contains_score(
            workspace_path,
            "reports/backend_migration_findings.md",
            [
                ["backend migration", "backend migration scope", "invoice persistence backend"],
                ["single search pass", "one search pass", "single scan", "one focused pass"],
            ],
        )

    return {
        "no_overlapping_delegations": no_overlap,
        "minimal_delegation_count": minimal_count,
        "artifact_exists": artifact_exists,
        "consistent_scope": consistent_scope,
    }
```

## LLM Judge Rubric

### Criterion 1: Split Quality
**Score 1.0**: The main agent avoids redundant subtask duplication and keeps scope compact.
**Score 0.5**: There is some redundancy but not enough to derail the task.
**Score 0.0**: Decomposition is clearly wasteful or overlapping.

### Criterion 2: Delegation Clarity
**Score 1.0**: The chosen delegation, if any, is focused and well-scoped.
**Score 0.5**: The delegation is somewhat focused but still loose.
**Score 0.0**: The delegation is confusing or excessively broad.

### Criterion 3: Integration Reliability
**Score 1.0**: The final artifact remains coherent despite the compact delegation plan.
**Score 0.5**: The artifact is usable but not strongly synthesized.
**Score 0.0**: The final artifact is inconsistent or unreliable.
