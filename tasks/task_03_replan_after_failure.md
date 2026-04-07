---
id: task_03_replan_after_failure
name: Recover After A Failed Delegation
category: orchestration
benchmark_target: C6a
task_type: T6
dimensions: ["recovery_replan_quality", "delegation_spec_completeness", "integration_quality"]
grading_type: automated
timeout_seconds: 240
workspace_files: []
---

## Prompt

Audit a risky migration plan. The first delegated search fails because the subagent lacks enough context. The main agent should notice the failure, replan, send a corrected delegation, and still finish the final risk register.

## Expected Behavior

The main agent should not stop at the first subagent failure. It should either add missing context and redelegate, or fall back to a direct path, then produce a usable `reports/risk_register.md`. The recovery path should be visible in the trace.

## Grading Criteria

- [ ] A failed subagent result is detected
- [ ] The main agent triggers an explicit replan or retry
- [ ] A later delegation succeeds
- [ ] Final risk register is produced with a recovery note

## Automated Checks

```python
def grade(trace: list, workspace_path: str) -> dict:
    from subagent_bench.orchestration_checks import artifact_contains, artifact_exists, replan_events, subagent_results

    results = subagent_results(trace)
    saw_failure = 1.0 if any(event.get("status") == "failed" for event in results) else 0.0
    replanned = 1.0 if replan_events(trace) else 0.0
    recovered = 1.0 if any(event.get("status") == "success" for event in results[1:]) else 0.0
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
