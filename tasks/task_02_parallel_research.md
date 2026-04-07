---
id: task_02_parallel_research
name: Parallelize Independent Research Streams
category: orchestration
benchmark_target: C6a
task_type: T4
dimensions: ["dependency_correctness", "task_decomposition_quality", "integration_quality"]
grading_type: hybrid
timeout_seconds: 240
workspace_files: []
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

## Prompt

Prepare a launch brief by comparing frontend rollout risks and backend rollout risks. These two research streams can happen in parallel and should be delegated independently. The main agent should merge the findings into `launch_brief.md`.

For benchmark observability, also write `delegation_trace.json` in the workspace root capturing `delegations`, `subagent_results`, `replans`, and `verifications`.

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
    from subagent_bench.orchestration_checks import delegate_events, subagent_results

    delegations = delegate_events(trace, workspace_path)
    results = subagent_results(trace, workspace_path)

    has_two = 1.0 if len(delegations) == 2 else 0.0
    distinct_outputs = 1.0 if len({event.get("output_path") for event in delegations}) == 2 else 0.0

    result_ids = {event.get("delegation_id") for event in results if event.get("status") == "success"}
    waited = 1.0 if len(result_ids) == 2 else 0.0

    launch_brief = Path(workspace_path) / "launch_brief.md"
    merged = 0.0
    if launch_brief.exists():
        content = launch_brief.read_text(encoding="utf-8").lower()
        merged = 1.0 if "frontend" in content and "backend" in content else 0.0

    return {
        "parallel_delegations": has_two,
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
