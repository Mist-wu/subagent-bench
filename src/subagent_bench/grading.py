from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict

from subagent_bench.models import GradeResult, Task
from subagent_bench.trace import load_trace


def grade_task(task: Task, trace_path: Path, workspace_path: Path) -> GradeResult:
    trace_bundle = load_trace(trace_path)
    events = trace_bundle.get("events", [])

    automated_result = _grade_automated(task, events, workspace_path)

    if task.grading_type == "automated":
        return automated_result

    judge_result = trace_bundle.get("judge_result")
    if task.grading_type in {"llm_judge", "hybrid"} and not judge_result:
        return GradeResult(
            task_id=task.task_id,
            task_name=task.name,
            grading_type=task.grading_type,
            score=automated_result.score if task.grading_type == "hybrid" else 0.0,
            breakdown=automated_result.breakdown if task.grading_type == "hybrid" else {},
            notes="Missing judge_result payload in trace.",
        )

    if task.grading_type == "llm_judge":
        return _attach_task_metadata(
            GradeResult(
            task_id=task.task_id,
            task_name=task.name,
            grading_type="llm_judge",
            score=float(judge_result.get("score", 0.0)),
            breakdown={key: float(value) for key, value in judge_result.get("breakdown", {}).items()},
            notes=str(judge_result.get("notes", "")),
            ),
            task,
        )

    weights = task.grading_weights or {"automated": 0.5, "llm_judge": 0.5}
    auto_weight = float(weights.get("automated", 0.5))
    judge_weight = float(weights.get("llm_judge", 0.5))
    total_weight = auto_weight + judge_weight or 1.0
    judge_score = float(judge_result.get("score", 0.0))
    combined = ((automated_result.score * auto_weight) + (judge_score * judge_weight)) / total_weight
    breakdown = dict(automated_result.breakdown)
    breakdown.update({f"llm_judge.{key}": float(value) for key, value in judge_result.get("breakdown", {}).items()})
    return _attach_task_metadata(
        GradeResult(
        task_id=task.task_id,
        task_name=task.name,
        grading_type="hybrid",
        score=combined,
        breakdown=breakdown,
        notes=str(judge_result.get("notes", "")),
        ),
        task,
    )


def _grade_automated(task: Task, events: Any, workspace_path: Path) -> GradeResult:
    grading_code = _extract_python_code(task.automated_checks or "")
    if not grading_code:
        return GradeResult(
            task_id=task.task_id,
            task_name=task.name,
            grading_type="automated",
            score=0.0,
            breakdown={},
            notes="No automated checks found.",
        )

    namespace: Dict[str, Any] = {}
    exec(grading_code, namespace)
    grade = namespace.get("grade")
    if not callable(grade):
        raise ValueError(f"Task {task.task_id} does not define a callable grade(trace, workspace_path)")

    scores = grade(events, str(workspace_path))
    if not isinstance(scores, dict):
        raise ValueError(f"Task {task.task_id} returned a non-dict score payload")

    normalized = {key: float(value) for key, value in scores.items()}
    normalized["__category__"] = task.category
    normalized["__dimensions__"] = list(task.dimensions)
    score = _strip_metadata_from_average(normalized)
    return _attach_task_metadata(
        GradeResult(
        task_id=task.task_id,
        task_name=task.name,
        grading_type="automated",
        score=score,
        breakdown=normalized,
        ),
        task,
    )


def _extract_python_code(section: str) -> str:
    match = re.search(r"```python\s*(.*?)```", section, re.DOTALL)
    if match:
        return match.group(1).strip()
    return section.strip()


def _strip_metadata_from_average(scores: Dict[str, Any]) -> float:
    numeric_values = [
        float(value)
        for key, value in scores.items()
        if not key.startswith("__")
    ]
    return sum(numeric_values) / len(numeric_values) if numeric_values else 0.0


def _attach_task_metadata(result: GradeResult, task: Task) -> GradeResult:
    result.breakdown["__category__"] = task.category
    result.breakdown["__benchmark_target__"] = task.benchmark_target
    result.breakdown["__task_type__"] = task.task_type
    result.breakdown["__dimensions__"] = list(task.dimensions)
    return result
