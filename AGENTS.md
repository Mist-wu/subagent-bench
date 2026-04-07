# AGENTS.md

Context for agents working in this repository.

## Project

subagent-bench evaluates multi-agent systems on two targets:

- **C6a (Orchestration)**: task decomposition, delegation, replanning, integration.
- **C6b (Execution)**: subagent tool use, correctness, and completion quality.

It borrows the `Markdown + YAML frontmatter` task format from PinchBench, but extends it to score orchestration traces explicitly instead of only end-to-end outputs.

## Architecture

- **Offline**: `src/subagent_bench/` grades recorded JSON traces. CLI entry: `src/subagent_bench/cli.py`.
- **Live**: `scripts/` runs real agents, collects transcripts, and grades them. Entry: `scripts/benchmark.py`.

Both paths use the shared task definitions in `tasks/`.

## Key directories

- `tasks/`: benchmark tasks.
- `src/subagent_bench/`: loader, schema, grading, orchestration checks, CLI, runner.
- `scripts/`: live benchmark runner and helpers.
- `examples/traces/`: golden traces.
- `examples/workspaces/`: golden artifacts.
- `tests/`: regression tests.

## Task format

Each `tasks/task_*.md` file contains:

- YAML frontmatter: `id`, `category`, `benchmark_target`, `task_type`, `dimensions`, `grading_type`, `timeout_seconds`, `workspace_files`
- `## Prompt`
- `## Expected Behavior`
- `## Grading Criteria`
- `## Automated Checks`
- `## LLM Judge Rubric` (optional)

See `tasks/TASK_TEMPLATE.md` for the full template.

## Grading system

- `automated`: deterministic Python checks
- `llm_judge`: rubric-based LLM scoring
- `hybrid`: weighted combination

Attribute failures to delegation, execution, or integration when possible.

## Trace format

Traces are JSON with an `events` array. Important event types:

- `delegate`
- `subagent_result`
- `replan`
- `verification`
- `tool_use`
- `tool_result`
- `assistant_message`
- `artifact_written`

Prefer explicit intermediate events over inferring behavior only from final outputs.

## Conventions

- Python 3.11+, dependencies managed via `pyproject.toml`.
- Tasks follow the PinchBench-style Markdown task format.
- Tests run with `pytest`.
- Live benchmark uses `uv run` (see `scripts/run.sh`).
