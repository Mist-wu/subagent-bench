from pathlib import Path

from subagent_bench.task_loader import TaskLoader


def test_loads_all_tasks() -> None:
    loader = TaskLoader(Path("tasks"))
    tasks = loader.load_all()

    assert len(tasks) == 11
    assert tasks[0].task_id == "task_01_delegate_or_not"
    assert tasks[1].grading_type == "automated"
    assert tasks[3].benchmark_target == "C6a"
    assert tasks[3].task_type == "T5"
    assert tasks[8].benchmark_target == "C6b"
