---
id: task_08_dependency_aware_decomposition
name: Dependency-Aware Decomposition
category: orchestration
benchmark_target: C6a
task_type: T3
dimensions: ["dependency_correctness", "task_decomposition_quality", "recovery_replan_quality"]
grading_type: hybrid
timeout_seconds: 300
workspace_files:
  - path: "schema/current_schema.sql"
    content: |
      CREATE TABLE invoices (
        id UUID PRIMARY KEY,
        invoice_id TEXT NULL,
        status TEXT NOT NULL
      );
  - path: "schema/target_schema.sql"
    content: |
      CREATE TABLE invoices (
        id UUID PRIMARY KEY,
        invoice_id TEXT NOT NULL,
        status TEXT NOT NULL
      );
  - path: "src/remediation_notes.md"
    content: |
      # Remediation Notes

      Application code still assumes `invoice_id` may be null in several write paths.
grading_weights:
  automated: 0.6
  llm_judge: 0.4
automated_weights:
  expected_dependency_delegations: 0.2
  dependency_correctness: 0.35
  downstream_consumes_upstream_output: 0.25
  dependency_aware_final_plan: 0.2
---

## Prompt

Plan a migration where schema analysis must happen before code remediation. The main agent should delegate the schema scan to `reports/schema_scan.md` first, then delegate remediation planning to `reports/remediation_plan.md` using that scan as an input, and finally produce `reports/dependency_plan.md`.

Prefer leaving native delegation evidence in the transcript. If the runtime cannot surface those events cleanly, write `delegation_trace.json` in the workspace root as a compatibility fallback.

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
    from subagent_bench.orchestration_checks import artifact_contains_score, delegate_events, phrase_group_score

    delegations = delegate_events(trace, workspace_path)
    ordered = 0.0
    dependency_link = 0.0

    if len(delegations) == 2:
        first = delegations[0]
        second = delegations[1]
        first_signature = " ".join(str(first.get(key, "")) for key in ["delegation_id", "instruction", "output_path"])
        second_signature = " ".join(str(second.get(key, "")) for key in ["delegation_id", "instruction", "output_path"])
        first_is_schema = phrase_group_score(first_signature, [["schema"], ["scan", "analysis", "audit"]])
        second_is_remediation = phrase_group_score(second_signature, [["remediation", "fix"], ["plan"]])
        ordered = min(first_is_schema, second_is_remediation)
        second_inputs = second.get("inputs", [])
        dependency_link = 1.0 if "reports/schema_scan.md" in second_inputs else 0.5 if "schema" in str(second.get("instruction", "")).lower() else 0.0

    artifact = Path(workspace_path) / "reports/dependency_plan.md"
    final_plan = 0.0
    if artifact.exists():
        final_plan = artifact_contains_score(
            workspace_path,
            "reports/dependency_plan.md",
            [
                ["schema before remediation", "schema-first remediation", "schema analysis before remediation"],
            ],
        )

    return {
        "expected_dependency_delegations": 1.0 if len(delegations) == 2 else 0.5 if len(delegations) == 1 else 0.0,
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
