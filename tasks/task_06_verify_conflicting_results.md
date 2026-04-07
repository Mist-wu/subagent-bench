---
id: task_06_verify_conflicting_results
name: Verify Conflicting Subagent Results
category: orchestration
benchmark_target: C6a
task_type: T7
dimensions: ["recovery_replan_quality", "integration_quality", "result_verification_quality"]
grading_type: hybrid
timeout_seconds: 240
workspace_files:
  - path: "reports/subagent_safe.md"
    content: |
      # Subagent Result A

      Conclusion: rollout is safe.
      Reasoning: no migration risk was observed in the sampled checks.
  - path: "reports/subagent_unsafe.md"
    content: |
      # Subagent Result B

      Conclusion: rollout is unsafe.
      Reasoning: migration ordering has not been verified.
  - path: "rollout-policy.md"
    content: |
      # Rollout Policy

      Source of truth:
      - Any rollout that changes required fields is unsafe until migration ordering is verified.
      - Verification must cite the source document used for the decision.
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

## Prompt

Two subagents have already returned conflicting conclusions about whether a rollout is safe. Their outputs are in `reports/subagent_safe.md` and `reports/subagent_unsafe.md`. The main agent should not blindly merge them. It should verify the conflict by consulting `rollout-policy.md`, then produce `reports/final_decision.md`.

Prefer leaving native runtime evidence for both subagent results and the verification step in the transcript. If the runtime cannot surface those events cleanly, write `delegation_trace.json` in the workspace root as a compatibility fallback.

## Expected Behavior

The main agent should detect the contradiction, run a verification step, and base the final decision on the verified source instead of raw delegation outputs.

## Grading Criteria

- [ ] Conflicting subagent results are present
- [ ] A verification step is recorded
- [ ] Final decision is written after verification
- [ ] Final artifact references the source of truth

## Automated Checks

```python
def grade(trace: list, workspace_path: str) -> dict:
    from pathlib import Path
    from subagent_bench.orchestration_checks import subagent_results, verification_events

    results = subagent_results(trace, workspace_path)
    contradictory = 0.0
    if len(results) >= 2:
        summaries = [
            (event.get("summary") or event.get("conclusion") or "").lower()
            for event in results[:2]
        ]
        contradictory = 1.0 if "safe" in summaries[0] and "unsafe" in summaries[1] else 0.0

    verification = 1.0 if verification_events(trace, workspace_path) else 0.0
    ordered = verification

    artifact = Path(workspace_path) / "reports/final_decision.md"
    cited_source = 0.0
    if artifact.exists():
        content = artifact.read_text(encoding="utf-8").lower()
        cited_source = 1.0 if "source of truth" in content and "rollout-policy.md" in content else 0.0

    return {
        "conflicting_results_detected": contradictory,
        "verification_recorded": verification,
        "decision_after_verification": ordered,
        "source_of_truth_cited": cited_source,
    }
```

## LLM Judge Rubric

### Criterion 1: Split Quality
**Score 1.0**: The main agent handles the conflicting delegated outputs in a disciplined way.
**Score 0.5**: Conflict handling exists but is somewhat ad hoc.
**Score 0.0**: The conflict is ignored or mishandled.

### Criterion 2: Delegation Clarity
**Score 1.0**: The delegated asks are clear enough that the conflict is interpretable rather than accidental noise.
**Score 0.5**: Delegations are only partly interpretable.
**Score 0.0**: Delegations are too unclear to support meaningful comparison.

### Criterion 3: Integration Reliability
**Score 1.0**: The final decision is grounded in verification and integrates evidence reliably.
**Score 0.5**: The final decision gestures at verification but remains somewhat shaky.
**Score 0.0**: The final integration is unreliable.
