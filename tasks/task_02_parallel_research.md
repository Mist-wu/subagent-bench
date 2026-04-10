---
id: task_02_parallel_research
name: Parallelize Independent Research Streams
category: orchestration
benchmark_target: C6a
task_type: T4
dimensions: ["dependency_correctness", "task_decomposition_quality", "integration_quality"]
grading_type: hybrid
timeout_seconds: 300
workspace_files:
  - path: "inputs/frontend_rollout.md"
    content: |
      # Frontend Rollout Notes

      - Client bundle recently added an untested lazy-loading path for billing pages.
      - Feature flag `billing-redesign` is enabled for 5% of traffic.
      - No mobile QA sign-off has been recorded yet.
  - path: "inputs/backend_rollout.md"
    content: |
      # Backend Rollout Notes

      - Queue workers were resized last week but no soak test was captured.
      - A schema migration introduces a nullable-to-required transition for `invoice_id`.
      - Rollback steps exist but have not been rehearsed.
  - path: "launch_brief.md"
    content: |
      # Launch Brief

      Pending research.
grading_weights:
  automated: 0.6
  llm_judge: 0.4
automated_weights:
  parallel_delegations: 0.25
  concurrency_overlap: 0.2
  non_overlapping_outputs: 0.2
  waits_for_both_results: 0.2
  merged_brief: 0.15
---

## Prompt

Prepare a launch brief by comparing frontend rollout risks and backend rollout risks. These two research streams can happen in parallel and should be delegated independently. Write the delegated outputs to `reports/frontend_risks.md` and `reports/backend_risks.md`, then merge the findings into `launch_brief.md`.

Prefer leaving native delegation evidence in the transcript. If the runtime cannot surface those events cleanly, write `delegation_trace.json` in the workspace root as a compatibility fallback. Each delegation entry should include `delegation_id`, `assignee`, `instruction`, `inputs`, `success_criteria`, and `output_path`.

## Expected Behavior

The main agent should create two non-overlapping delegations, wait for both results, and then integrate them into one decision memo. It should avoid redundant overlap between subagents and should not finalize before both delegated results arrive.

## Grading Criteria

- [ ] Two delegations are created for independent scopes
- [ ] Delegations write to distinct output artifacts
- [ ] Main agent integrates only after both subagent results arrive
- [ ] Final brief references both frontend and backend findings

## Automated Checks

```python
def grade(trace: list, workspace_path: str) -> dict:
    from pathlib import Path
    from subagent_bench.orchestration_checks import (
        artifact_contains_score,
        concurrent_delegate_events,
        delegate_events,
        native_delegate_events,
        native_event_coverage_score,
        native_subagent_results,
        subagent_results,
    )

    delegations = delegate_events(trace, workspace_path)
    concurrent = concurrent_delegate_events(trace, workspace_path)
    results = subagent_results(trace, workspace_path)
    native_delegations = native_delegate_events(trace)
    native_results = native_subagent_results(trace)

    has_two = min(
        max(0.0, 1.0 - (0.5 * abs(len(delegations) - 2))),
        native_event_coverage_score(len(native_delegations), len(delegations), expected_min=2),
    )
    overlap = min(1.0, len(concurrent) / 2) if delegations else 0.0
    unique_outputs = {event.get("output_path") for event in delegations if event.get("output_path")}
    distinct_outputs = (len(unique_outputs) / len(delegations)) if delegations else 0.0

    result_ids = {event.get("delegation_id") for event in results if event.get("status") == "success"}
    delegation_ids = {event.get("delegation_id") for event in delegations}
    waited = min(
        len(result_ids & delegation_ids) / 2,
        native_event_coverage_score(len(native_results), len(results), expected_min=2),
    )

    launch_brief = Path(workspace_path) / "launch_brief.md"
    merged = 0.0
    if launch_brief.exists():
        merged = artifact_contains_score(
            workspace_path,
            "launch_brief.md",
            [
                ["frontend", "frontend findings", "frontend risks"],
                ["backend", "backend findings", "backend risks"],
            ],
        )

    return {
        "parallel_delegations": has_two,
        "concurrency_overlap": overlap,
        "non_overlapping_outputs": distinct_outputs,
        "waits_for_both_results": waited,
        "merged_brief": merged,
    }
```

## LLM Judge Rubric

### Criterion 1: Split Quality
**Score 1.0**: The task is split into two clean, parallelizable streams with no redundant overlap.
**Score 0.5**: Parallelization is partly correct but leaves overlap or weak boundaries.
**Score 0.0**: The split is confused or not meaningfully parallel.

### Criterion 2: Delegation Clarity
**Score 1.0**: Each delegation clearly scopes the frontend/backend stream and expected output.
**Score 0.5**: Delegations are somewhat understandable but underspecified.
**Score 0.0**: Delegations are unclear or ambiguous.

### Criterion 3: Integration Reliability
**Score 1.0**: The final brief reliably combines both streams into one coherent launch view.
**Score 0.5**: Integration is incomplete or weakly synthesized.
**Score 0.0**: Results are merged unreliably or not merged.
