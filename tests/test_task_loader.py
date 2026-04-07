from pathlib import Path

from subagent_bench.task_loader import TaskLoader


def test_loads_three_tasks() -> None:
    loader = TaskLoader(Path("tasks"))
    tasks = loader.load_all()

    assert len(tasks) == 6
    assert tasks[0].task_id == "task_01_delegate_or_not"
    assert tasks[1].grading_type == "automated"
    assert tasks[3].dimensions == ["spec_quality", "delegation_policy"]
