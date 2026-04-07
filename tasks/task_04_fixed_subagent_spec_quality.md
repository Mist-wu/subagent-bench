---
id: task_04_fixed_subagent_spec_quality
name: Fixed Subagent Spec Quality
category: orchestration
dimensions: ["spec_quality", "delegation_policy"]
grading_type: automated
timeout_seconds: 180
workspace_files: []
---

## Prompt

The main agent must delegate a documentation extraction task to a fixed subagent. The benchmark is not about the subagent itself. It is about whether the main agent provides enough context, constraints, and output requirements for the fixed subagent to succeed without clarification.

## Expected Behavior

The main agent should create one delegation with explicit inputs, constraints, success criteria, and output format. The subagent should then be able to write `reports/extracted_api_summary.md` successfully.

## Grading Criteria

- [ ] Exactly one delegation is created
- [ ] Delegation includes complete context fields
- [ ] Delegation specifies output format expectations
- [ ] The expected artifact is produced

## Automated Checks

```python
def grade(trace: list, workspace_path: str) -> dict:
    from pathlib import Path
    from subagent_bench.orchestration_checks import delegate_events, delegation_fields_present

    delegations = delegate_events(trace)
    exactly_one = 1.0 if len(delegations) == 1 else 0.0
    spec_complete = 1.0 if delegations and delegation_fields_present(delegations[0]) else 0.0

    output_format = 0.0
    if delegations:
        instruction = delegations[0].get("instruction", "").lower()
        output_format = 1.0 if "markdown" in instruction and "headings" in instruction else 0.0

    artifact = Path(workspace_path) / "reports/extracted_api_summary.md"
    produced = 1.0 if artifact.exists() else 0.0

    return {
        "single_delegation": exactly_one,
        "complete_spec": spec_complete,
        "output_format_specified": output_format,
        "artifact_produced": produced,
    }
```
