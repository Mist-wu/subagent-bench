---
id: task_04_fixed_subagent_spec_quality
name: Fixed Subagent Spec Quality
category: orchestration
benchmark_target: C6a
task_type: T5
dimensions: ["delegation_spec_completeness", "assignment_accuracy"]
grading_type: hybrid
timeout_seconds: 180
workspace_files: []
grading_weights:
  automated: 0.6
  llm_judge: 0.4
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

## LLM Judge Rubric

### Criterion 1: Split Quality
**Score 1.0**: The main agent delegates exactly the right slice to the fixed subagent.
**Score 0.5**: Delegation is broadly appropriate but somewhat mis-scoped.
**Score 0.0**: The chosen delegated slice is clearly wrong.

### Criterion 2: Delegation Clarity
**Score 1.0**: The spec is crisp, complete, and actionable without follow-up questions.
**Score 0.5**: The spec is understandable but missing important details.
**Score 0.0**: The spec is too vague to execute reliably.

### Criterion 3: Integration Reliability
**Score 1.0**: The delegated artifact matches the expected contract implied by the spec.
**Score 0.5**: The artifact is usable but contract expectations are only partly met.
**Score 0.0**: The delegated result is not reliable enough to integrate.
