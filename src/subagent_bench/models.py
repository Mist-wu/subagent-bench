from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class Task:
    task_id: str
    name: str
    category: str
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
    breakdown: Dict[str, float]
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "grading_type": self.grading_type,
            "score": self.score,
            "breakdown": self.breakdown,
            "notes": self.notes,
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
        by_category: Dict[str, List[float]] = {}
        by_dimension: Dict[str, List[float]] = {}
        for result in self.results:
            category = result.breakdown.get("__category__")
            if category:
                by_category.setdefault(str(category), []).append(result.score)
            dimensions = result.breakdown.get("__dimensions__")
            if isinstance(dimensions, list):
                for dimension in dimensions:
                    by_dimension.setdefault(str(dimension), []).append(result.score)

        return {
            "average_score": self.average_score,
            "category_scores": {
                key: sum(values) / len(values) for key, values in sorted(by_category.items())
            },
            "dimension_scores": {
                key: sum(values) / len(values) for key, values in sorted(by_dimension.items())
            },
            "results": [result.to_dict() for result in self.results],
        }
