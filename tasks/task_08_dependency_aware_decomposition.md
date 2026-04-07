---
id: task_08_dependency_aware_decomposition
name: Dependency-Aware Decomposition
category: orchestration
benchmark_target: C6a
task_type: T3
dimensions: ["dependency_correctness", "task_decomposition_quality", "recovery_replan_quality"]
grading_type: hybrid
timeout_seconds: 240
workspace_files: []
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

## Prompt

Plan a migration where schema analysis must happen before code remediation. The main agent should not run the remediation subtask before the dependency input is ready. It should produce `reports/dependency_plan.md`.

## Expected Behavior

The main agent should model the dependency correctly, delegate the schema scan first, and only then launch the remediation planning step. Incorrect parallelization should fail this task.

## Grading Criteria

- [ ] Two delegations are created
- [ ] Dependency order is respected
- [ ] Later delegation consumes earlier output
- [ ] Final plan mentions schema-before-remediation ordering

## Automated Checks

```python
def grade(trace: list, workspace_path: str) -> dict:
    from pathlib import Path

    delegate_indices = [(index, event) for index, event in enumerate(trace) if event.get("type") == "delegate"]
    ordered = 0.0
    dependency_link = 0.0

    if len(delegate_indices) == 2:
        first = delegate_indices[0][1]
        second = delegate_indices[1][1]
        ordered = 1.0 if first.get("delegation_id") == "schema-scan" and second.get("delegation_id") == "remediation-plan" else 0.0
        second_inputs = second.get("inputs", [])
        dependency_link = 1.0 if "reports/schema_scan.md" in second_inputs else 0.0

    artifact = Path(workspace_path) / "reports/dependency_plan.md"
    final_plan = 0.0
    if artifact.exists():
        content = artifact.read_text(encoding="utf-8").lower()
        final_plan = 1.0 if "schema before remediation" in content else 0.0

    return {
        "expected_dependency_delegations": 1.0 if len(delegate_indices) == 2 else 0.0,
        "dependency_correctness": ordered,
        "downstream_consumes_upstream_output": dependency_link,
        "dependency_aware_final_plan": final_plan,
    }
```

## LLM Judge Rubric

### Criterion 1: Split Quality
**Score 1.0**: The decomposition captures the upstream/downstream dependency cleanly.
**Score 0.5**: The dependency is partly recognized but not strongly represented.
**Score 0.0**: The split ignores or mishandles dependency structure.

### Criterion 2: Delegation Clarity
**Score 1.0**: The downstream task clearly states that it depends on upstream output.
**Score 0.5**: Dependency is implied but not explicit enough.
**Score 0.0**: Dependency information is absent or unclear.

### Criterion 3: Integration Reliability
**Score 1.0**: The final dependency plan reflects the ordered execution reliably.
**Score 0.5**: The final plan is only partly dependency-aware.
**Score 0.0**: The final plan is unreliable or inconsistent with the dependency.
