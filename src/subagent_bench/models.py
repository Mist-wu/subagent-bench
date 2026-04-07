from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


@dataclass
class Task:
    task_id: str
    name: str
    category: str
    benchmark_target: str
    task_type: str
    dimensions: List[str]
    grading_type: str
    timeout_seconds: int
    workspace_files: List[Dict[str, Any]]
    prompt: str
    expected_behavior: str
    grading_criteria: List[str]
    automated_checks: Optional[str] = None
    llm_judge_rubric: Optional[str] = None
    grading_weights: Optional[Dict[str, float]] = None
    file_path: Optional[Path] = None
    frontmatter: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GradeResult:
    task_id: str
    task_name: str
    grading_type: str
    score: float
    breakdown: Dict[str, Any]
    notes: str = ""
    failure_attribution: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "grading_type": self.grading_type,
            "score": self.score,
            "breakdown": self.breakdown,
            "notes": self.notes,
            "failure_attribution": self.failure_attribution,
        }


@dataclass
class BenchmarkRun:
    results: List[GradeResult]

    @property
    def average_score(self) -> float:
        if not self.results:
            return 0.0
        return sum(result.score for result in self.results) / len(self.results)

    def to_dict(self) -> Dict[str, Any]:
        by_target: Dict[str, List[float]] = {}
        by_task_type: Dict[str, List[float]] = {}
        by_category: Dict[str, List[float]] = {}
        by_dimension: Dict[str, List[float]] = {}
        for result in self.results:
            category = result.breakdown.get("__category__")
            if category:
                by_category.setdefault(str(category), []).append(result.score)
            benchmark_target = result.breakdown.get("__benchmark_target__")
            if benchmark_target:
                by_target.setdefault(str(benchmark_target), []).append(result.score)
            task_type = result.breakdown.get("__task_type__")
            if task_type:
                by_task_type.setdefault(str(task_type), []).append(result.score)
            dimensions = result.breakdown.get("__dimensions__")
            if isinstance(dimensions, list):
                for dimension in dimensions:
                    by_dimension.setdefault(str(dimension), []).append(result.score)

        return {
            "average_score": self.average_score,
            "benchmark_target_scores": {
                key: sum(values) / len(values) for key, values in sorted(by_target.items())
            },
            "task_type_scores": {
                key: sum(values) / len(values) for key, values in sorted(by_task_type.items())
            },
            "category_scores": {
                key: sum(values) / len(values) for key, values in sorted(by_category.items())
            },
            "dimension_scores": {
                key: sum(values) / len(values) for key, values in sorted(by_dimension.items())
            },
            "system_metrics": {
                "end_to_end_task_success": self._metric_fraction(lambda result: result.score >= 0.999),
                "over_delegation_rate": self._inverse_average("avoids_over_delegation"),
                "under_delegation_rate": self._inverse_average("delegates_when_needed"),
                "execution_normalized_delegation_score": self._average_for_task_type("T5"),
            },
            "failure_attribution_counts": self._failure_attribution_counts(),
            "results": [result.to_dict() for result in self.results],
        }

    def _average_for_task_type(self, task_type: str) -> float | None:
        values = [
            result.score
            for result in self.results
            if result.breakdown.get("__task_type__") == task_type
        ]
        if not values:
            return None
        return sum(values) / len(values)

    def _inverse_average(self, key: str) -> float | None:
        values = [
            float(result.breakdown[key])
            for result in self.results
            if key in result.breakdown
        ]
        if not values:
            return None
        return 1.0 - (sum(values) / len(values))

    def _metric_fraction(self, predicate: Callable[[GradeResult], bool]) -> float:
        if not self.results:
            return 0.0
        count = sum(1 for result in self.results if predicate(result))
        return count / len(self.results)

    def _failure_attribution_counts(self) -> Dict[str, int]:
        counts = {
            "Delegation Failure": 0,
            "Execution Failure": 0,
            "Integration Failure": 0,
        }
        for result in self.results:
            for label in result.failure_attribution:
                counts[label] = counts.get(label, 0) + 1
        return counts
