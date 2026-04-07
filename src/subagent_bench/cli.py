from __future__ import annotations

import argparse
from pathlib import Path

from subagent_bench.runner import run_benchmark, save_results, validate_traces
from subagent_bench.task_loader import TaskLoader


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Benchmark main-agent delegation and orchestration traces.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list-tasks", help="List all benchmark tasks.")
    list_parser.add_argument("--tasks-dir", default="tasks")

    grade_parser = subparsers.add_parser("grade", help="Grade traces against task definitions.")
    grade_parser.add_argument("--tasks-dir", default="tasks")
    grade_parser.add_argument("--traces-dir", default="examples/traces")
    grade_parser.add_argument("--workspace-root", default="examples/workspaces")
    grade_parser.add_argument("--suite", default="all", help="Comma-separated task ids or 'all'.")
    grade_parser.add_argument("--output", default="results/latest.json")

    validate_parser = subparsers.add_parser("validate-traces", help="Validate trace bundles and summarize event types.")
    validate_parser.add_argument("--tasks-dir", default="tasks")
    validate_parser.add_argument("--traces-dir", default="examples/traces")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "list-tasks":
        loader = TaskLoader(Path(args.tasks_dir))
        for task in loader.load_all():
            dims = ",".join(task.dimensions)
            print(f"{task.task_id}\t{task.benchmark_target}\t{task.task_type}\t{task.category}\t{dims}\t{task.name}")
        return

    if args.command == "validate-traces":
        for summary in validate_traces(tasks_dir=Path(args.tasks_dir), traces_dir=Path(args.traces_dir)):
            print(f"{summary['task_id']}\t{summary['event_counts']}")
        return

    suite = None if args.suite == "all" else [item.strip() for item in args.suite.split(",") if item.strip()]
    run = run_benchmark(
        tasks_dir=Path(args.tasks_dir),
        traces_dir=Path(args.traces_dir),
        workspace_root=Path(args.workspace_root),
        task_ids=suite,
    )
    save_results(run, Path(args.output))

    print(f"Average score: {run.average_score:.3f}")
    for result in run.results:
        print(f"{result.task_id}\t{result.score:.3f}\t{result.notes}")
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
