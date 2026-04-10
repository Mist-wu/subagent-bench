"""
Compatibility wrappers for the core task model and loader.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from _paths import ensure_src_on_path

ensure_src_on_path()

from subagent_bench.models import Task as CoreTask
from subagent_bench.task_loader import TaskLoader as CoreTaskLoader


class Task(CoreTask):
    """Backwards-compatible task wrapper for the live benchmark scripts."""

    def __init__(
        self,
        task_id: str,
        name: str,
        category: str,
        grading_type: str,
        timeout_seconds: int,
        workspace_files: List[Dict[str, Any]],
        prompt: str,
        expected_behavior: str,
        grading_criteria: List[str],
        automated_checks: Optional[str] = None,
        llm_judge_rubric: Optional[str] = None,
        automated_weights: Optional[Dict[str, float]] = None,
        grading_weights: Optional[Dict[str, float]] = None,
        file_path: Optional[Path] = None,
        frontmatter: Optional[Dict[str, Any]] = None,
        *,
        benchmark_target: str = "C6a",
        task_type: str = "",
        dimensions: Optional[List[str]] = None,
    ):
        frontmatter = frontmatter or {}
        super().__init__(
            task_id=task_id,
            name=name,
            category=category,
            benchmark_target=str(frontmatter.get("benchmark_target", benchmark_target)),
            task_type=str(frontmatter.get("task_type", task_type)),
            dimensions=list(frontmatter.get("dimensions", dimensions or [])),
            grading_type=grading_type,
            timeout_seconds=timeout_seconds,
            workspace_files=workspace_files,
            prompt=prompt,
            expected_behavior=expected_behavior,
            grading_criteria=grading_criteria,
            automated_checks=automated_checks,
            llm_judge_rubric=llm_judge_rubric,
            automated_weights=automated_weights,
            grading_weights=grading_weights,
            file_path=file_path,
            frontmatter=frontmatter,
        )

    def __repr__(self) -> str:
        return f"Task(id={self.task_id}, name={self.name}, category={self.category})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "category": self.category,
            "benchmark_target": self.benchmark_target,
            "task_type": self.task_type,
            "dimensions": self.dimensions,
            "grading_type": self.grading_type,
            "timeout_seconds": self.timeout_seconds,
            "workspace_files": self.workspace_files,
            "prompt": self.prompt,
            "expected_behavior": self.expected_behavior,
            "grading_criteria": self.grading_criteria,
            "has_automated_checks": self.automated_checks is not None,
            "has_llm_judge_rubric": self.llm_judge_rubric is not None,
            "automated_weights": self.automated_weights,
            "grading_weights": self.grading_weights,
            "frontmatter": self.frontmatter,
        }


class TaskLoader(CoreTaskLoader):
    """Compatibility wrapper that preserves the legacy scripts API."""

    def load_all_tasks(self) -> List[Task]:
        return self.load_all()

    def load_all(self) -> List[Task]:
        return [self.load_task(task_file) for task_file in sorted(self.tasks_dir.glob("task_*.md"))]

    def load_task(self, task_file: Path) -> Task:
        task = super().load_task(task_file)
        return Task(
            task_id=task.task_id,
            name=task.name,
            category=task.category,
            benchmark_target=task.benchmark_target,
            task_type=task.task_type,
            dimensions=list(task.dimensions),
            grading_type=task.grading_type,
            timeout_seconds=task.timeout_seconds,
            workspace_files=task.workspace_files,
            prompt=task.prompt,
            expected_behavior=task.expected_behavior,
            grading_criteria=task.grading_criteria,
            automated_checks=task.automated_checks,
            llm_judge_rubric=task.llm_judge_rubric,
            automated_weights=task.automated_weights,
            grading_weights=task.grading_weights,
            file_path=task.file_path,
            frontmatter=dict(task.frontmatter),
        )
