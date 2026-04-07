---
id: task_02_parallel_research
name: Parallelize Independent Research Streams
category: orchestration
benchmark_target: C6a
task_type: T4
dimensions: ["dependency_correctness", "task_decomposition_quality", "integration_quality"]
grading_type: automated
timeout_seconds: 240
workspace_files: []
---

## Prompt

Prepare a launch brief by comparing frontend rollout risks and backend rollout risks. These two research streams can happen in parallel and should be delegated independently. The main agent should merge the findings into `launch_brief.md`.

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

    delegations = delegate_events(trace)
    results = subagent_results(trace)
    integration_index = next((i for i, event in enumerate(trace) if event.get("type") == "artifact_written" and event.get("path") == "launch_brief.md"), -1)

    has_two = 1.0 if len(delegations) == 2 else 0.0
    distinct_outputs = 1.0 if len({event.get("output_path") for event in delegations}) == 2 else 0.0

    result_ids = {event.get("delegation_id") for event in results if event.get("status") == "success"}
    waited = 0.0
    if integration_index != -1 and len(result_ids) == 2:
        latest_result_index = max(i for i, event in enumerate(trace) if event.get("type") == "subagent_result" and event.get("status") == "success")
        waited = 1.0 if latest_result_index < integration_index else 0.0

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
