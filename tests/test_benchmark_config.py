import argparse
import sys
from pathlib import Path

import pytest


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from benchmark import _validate_judge_configuration  # noqa: E402
from lib_tasks import Task, TaskLoader  # noqa: E402


def _task(grading_type: str) -> Task:
    return Task(
        task_id="task_x",
        name="x",
        category="orchestration",
        grading_type=grading_type,
        timeout_seconds=30,
        workspace_files=[],
        prompt="Do work",
        expected_behavior="",
        grading_criteria=[],
    )


def test_self_judge_is_rejected_for_judged_tasks() -> None:
    args = argparse.Namespace(model="model-a", judge=None, allow_self_judge=False)

    with pytest.raises(ValueError):
        _validate_judge_configuration(args, [_task("hybrid")])


def test_self_judge_override_is_allowed() -> None:
    args = argparse.Namespace(model="model-a", judge=None, allow_self_judge=True)

    _validate_judge_configuration(args, [_task("hybrid")])


def test_automated_only_suite_does_not_require_independent_judge() -> None:
    args = argparse.Namespace(model="model-a", judge=None, allow_self_judge=False)

    _validate_judge_configuration(args, [_task("automated")])


def test_script_task_uses_frontmatter_for_core_metadata() -> None:
    task = Task(
        task_id="task_x",
        name="x",
        category="execution",
        grading_type="automated",
        timeout_seconds=30,
        workspace_files=[],
        prompt="Do work",
        expected_behavior="",
        grading_criteria=[],
        frontmatter={
            "benchmark_target": "C6b",
            "task_type": "T5",
            "dimensions": ["tool_use_correctness"],
        },
    )

    assert task.benchmark_target == "C6b"
    assert task.task_type == "T5"
    assert task.dimensions == ["tool_use_correctness"]


def test_script_task_loader_reuses_core_task_metadata() -> None:
    tasks = TaskLoader(Path("tasks")).load_all_tasks()

    assert len(tasks) == 11
    assert tasks[3].benchmark_target == "C6a"
    assert tasks[8].benchmark_target == "C6b"
    assert tasks[8].task_type == "execution_search"
