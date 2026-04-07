from pathlib import Path

from subagent_bench.runner import run_benchmark


def test_example_suite_scores_perfectly() -> None:
    run = run_benchmark(
        tasks_dir=Path("tasks"),
        traces_dir=Path("examples/traces"),
        workspace_root=Path("examples/workspaces"),
    )

    assert len(run.results) == 11
    assert run.average_score == 1.0
    payload = run.to_dict()
    assert payload["category_scores"]["orchestration"] == 1.0
    assert payload["category_scores"]["execution"] == 1.0
    assert payload["benchmark_target_scores"]["C6a"] == 1.0
    assert payload["benchmark_target_scores"]["C6b"] == 1.0
    assert payload["task_type_scores"]["T7"] == 1.0
    assert payload["dimension_scores"]["result_verification_quality"] == 1.0
    assert payload["system_metrics"]["end_to_end_task_success"] == 1.0
    assert payload["failure_attribution_counts"]["Delegation Failure"] == 0
    assert payload["failure_attribution_counts"]["Execution Failure"] == 0
