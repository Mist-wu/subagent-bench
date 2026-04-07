from pathlib import Path

from subagent_bench.runner import validate_traces
from subagent_bench.trace import load_trace


def test_validate_trace_summaries_cover_all_tasks() -> None:
    summaries = validate_traces(tasks_dir=Path("tasks"), traces_dir=Path("examples/traces"))
    assert len(summaries) == 6
    assert summaries[0]["task_id"] == "task_01_delegate_or_not"


def test_trace_loader_accepts_structured_bundle() -> None:
    bundle = load_trace(Path("examples/traces/task_06_verify_conflicting_results.json"))
    assert len(bundle["events"]) == 6
    assert bundle["events"][4]["type"] == "verification"
