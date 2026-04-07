# AGENTS.md

This file provides context for AI agents working in this repository.

## What this project is

subagent-bench is a benchmark for evaluating multi-agent AI systems. It scores two separate capabilities:

- **C6a (Orchestration)**: How well a main agent decomposes tasks, delegates to subagents, writes delegation specs, handles failures, and integrates results.
- **C6b (Execution)**: How well subagents understand instructions, use tools, produce correct outputs, and handle errors.

## Architecture

There are two evaluation paths:

1. **Offline** (`src/subagent_bench/`): Grades pre-recorded JSON traces against task definitions. Entry point is the `subagent-bench` CLI (`src/subagent_bench/cli.py`).
2. **Live** (`scripts/`): Executes real agents via OpenClaw, collects transcripts, grades them. Entry point is `scripts/benchmark.py`.

Both paths share the same task definitions in `tasks/`.

## Key directories

- `tasks/` -- Benchmark task definitions. Each is a Markdown file with YAML frontmatter, a prompt, expected behavior, grading criteria, and embedded Python grading code.
- `src/subagent_bench/` -- Core library: task loading (`task_loader.py`), trace schema validation (`schema.py`), grading engine (`grading.py`), orchestration checks (`orchestration_checks.py`), CLI (`cli.py`), runner (`runner.py`).
- `scripts/` -- Live benchmark: agent lifecycle (`lib_agent.py`), grading (`lib_grading.py`), task loading (`lib_tasks.py`), main runner (`benchmark.py`).
- `examples/traces/` -- Golden trace files (one JSON per task).
- `examples/workspaces/` -- Golden workspace outputs (artifacts produced by each task).
- `tests/` -- Pytest regression tests.

## Task format

Each task file (`tasks/task_*.md`) contains:

- YAML frontmatter: `id`, `category` (orchestration/execution), `benchmark_target` (C6a/C6b), `task_type`, `dimensions`, `grading_type`, `timeout_seconds`, `workspace_files`.
- `## Prompt` -- Instruction given to the agent.
- `## Expected Behavior` -- Ideal behavior description.
- `## Grading Criteria` -- Pass/fail checklist.
- `## Automated Checks` -- Python `grade(trace, workspace_path)` function returning a score dict.
- `## LLM Judge Rubric` -- Rubric for LLM-based evaluation (optional).

See `tasks/TASK_TEMPLATE.md` for the full template.

## Grading system

- **automated**: Deterministic Python checks (`exec`'d from each task's `## Automated Checks`).
- **llm_judge**: LLM evaluates transcript against rubric criteria.
- **hybrid**: Weighted combination of both.

Scores are attributed to failure categories: delegation failure, execution failure, or integration failure.

## Trace format

Traces are JSON with an `events` array. Key event types: `delegate`, `subagent_result`, `replan`, `verification`, `tool_use`, `tool_result`, `assistant_message`, `artifact_written`.

## Conventions

- Python 3.11+, dependencies managed via `pyproject.toml`.
- Tasks use the PinchBench-style Markdown + YAML frontmatter format.
- Tests run with `pytest`.
- Live benchmark uses `uv run` (see `scripts/run.sh`).
