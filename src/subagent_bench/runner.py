from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Optional

from subagent_bench.grading import grade_task
from subagent_bench.models import BenchmarkRun
from subagent_bench.schema import summarize_trace_types
from subagent_bench.task_loader import TaskLoader
from subagent_bench.trace import load_trace


def run_benchmark(
    *,
    tasks_dir: Path,
    traces_dir: Path,
    workspace_root: Path,
    task_ids: Optional[Iterable[str]] = None,
) -> BenchmarkRun:
    loader = TaskLoader(tasks_dir)
    tasks = loader.load_all()
    selected = set(task_ids or [])
    if selected:
        tasks = [task for task in tasks if task.task_id in selected]

    results = []
    for task in tasks:
        trace_path = traces_dir / f"{task.task_id}.json"
        workspace_path = workspace_root / task.task_id
        if not trace_path.exists():
            raise FileNotFoundError(f"Missing trace for {task.task_id}: {trace_path}")
        if not workspace_path.exists():
            raise FileNotFoundError(f"Missing workspace for {task.task_id}: {workspace_path}")
        results.append(grade_task(task, trace_path, workspace_path))

    return BenchmarkRun(results=results)


def save_results(run: BenchmarkRun, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(run.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def validate_traces(*, tasks_dir: Path, traces_dir: Path) -> List[dict]:
    loader = TaskLoader(tasks_dir)
    summaries = []
    for task in loader.load_all():
        trace_path = traces_dir / f"{task.task_id}.json"
        bundle = load_trace(trace_path)
        summaries.append(
            {
                "task_id": task.task_id,
                "trace_path": str(trace_path),
                "event_counts": summarize_trace_types(bundle.get("events", [])),
            }
        )
    return summaries
