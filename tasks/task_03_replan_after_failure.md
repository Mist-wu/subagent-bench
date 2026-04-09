---
id: task_03_replan_after_failure
name: Recover After A Failed Delegation
category: orchestration
benchmark_target: C6a
task_type: T6
dimensions: ["recovery_replan_quality", "delegation_spec_completeness", "integration_quality"]
grading_type: hybrid
timeout_seconds: 300
workspace_files:
  - path: "docs/migration_brief.md"
    content: |
      # Migration Brief

      We are renaming `invoice_id` semantics across services.
      The brief is incomplete on purpose. See the API contract and dependency notes for the missing edge cases.
  - path: "docs/api_contract.md"
    content: |
      # API Contract

      - `invoice_id` becomes required on write paths starting in v2.
      - Existing workers still emit payloads without `invoice_id`.
      - Consumers reject messages that omit the field.
  - path: "docs/dependency_notes.md"
    content: |
      # Dependency Notes

      - Billing worker deploys after API deploy.
      - Retry queue keeps old payloads for 24 hours.
      - Rollback needs dual-write compatibility.
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

## Prompt

Audit a risky migration plan. The first delegated search should be treated as failed because it does not include enough context. The main agent should notice the failure, replan, send a corrected delegation that includes `docs/api_contract.md` and `docs/dependency_notes.md`, and still finish `reports/risk_register.md`.

Prefer leaving native runtime evidence for the failed delegation, recovery, and later success in the transcript. If the runtime cannot surface those events cleanly, write `delegation_trace.json` in the workspace root as a compatibility fallback.

## Expected Behavior

The main agent should not stop at the first subagent failure. It should either add missing context and redelegate, or fall back to a direct path, then produce a usable `reports/risk_register.md`. The recovery path should be visible in the trace.

## Grading Criteria

- [ ] A failed subagent result is detected
- [ ] The main agent triggers an explicit replan, retry, or local fallback
- [ ] Recovery succeeds via a corrected delegation or local completion
- [ ] Final risk register is produced with a recovery note

## Automated Checks

```python
def grade(trace: list, workspace_path: str) -> dict:
    from subagent_bench.orchestration_checks import (
        artifact_contains,
        artifact_exists,
        local_recovery_events,
        replan_events,
        subagent_results,
    )

    results = subagent_results(trace, workspace_path)
    local_recoveries = local_recovery_events(trace, workspace_path)
    saw_failure = 1.0 if any(event.get("status") == "failed" for event in results) else 0.0
    replanned = 1.0 if replan_events(trace, workspace_path) else 0.0
    recovered = 1.0 if any(event.get("status") == "success" for event in results[1:]) else 0.5 if local_recoveries else 0.0
    risk_register = 1.0 if artifact_exists(workspace_path, "reports/risk_register.md") and artifact_contains(
        workspace_path,
        "reports/risk_register.md",
        ["recovered after retry", "missing api contract", "mitigation"],
    ) else 0.0

    return {
        "failure_detected": saw_failure,
        "replan_or_retry": replanned,
        "later_success": recovered,
        "final_output_with_recovery_note": risk_register,
    }
```

## LLM Judge Rubric

### Criterion 1: Split Quality
**Score 1.0**: The recovery plan correctly reframes the work after failure, whether by redelegation or a clear local fallback.
**Score 0.5**: Recovery exists but the revised path is only partly well-scoped.
**Score 0.0**: No meaningful recovery plan appears.

### Criterion 2: Delegation Clarity
**Score 1.0**: The recovery path adds the missing context or otherwise makes the corrected execution path explicit.
**Score 0.5**: The recovery path is partially clearer but still underspecified.
**Score 0.0**: The recovery path leaves the original ambiguity unresolved.

### Criterion 3: Integration Reliability
**Score 1.0**: The final output reflects the recovery path and remains reliable.
**Score 0.5**: The output exists but recovery handling is only partly reflected.
**Score 0.0**: The final output does not reliably incorporate the recovery.
