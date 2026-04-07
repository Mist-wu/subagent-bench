from pathlib import Path

from subagent_bench.runner import run_benchmark


def test_example_suite_scores_perfectly() -> None:
    run = run_benchmark(
        tasks_dir=Path("tasks"),
        traces_dir=Path("examples/traces"),
        workspace_root=Path("examples/workspaces"),
    )

    assert len(run.results) == 6
    assert run.average_score == 1.0
    payload = run.to_dict()
    assert payload["category_scores"]["orchestration"] == 1.0
    assert payload["dimension_scores"]["verification"] == 1.0
