# subagent-bench

A benchmark for evaluating multi-agent AI systems, focusing on two capabilities that existing benchmarks lack:

- **C6a**: Main-agent delegation & orchestration (task decomposition, delegation quality, failure recovery)
- **C6b**: Subagent execution (tool use, output compliance, error handling)

## Install

Requires Python 3.11 or newer.

```bash
pip install -e ".[dev]"
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv pip install -e ".[dev]"
```

## Usage

### Offline evaluation (pre-recorded traces)

```bash
# List all benchmark tasks
subagent-bench list-tasks

# Validate trace format
subagent-bench validate-traces --traces-dir examples/traces

# Grade traces
subagent-bench grade \
  --traces-dir examples/traces \
  --workspace-root examples/workspaces

# Run specific tasks
subagent-bench grade --suite task_01_delegate_or_not,task_09_subagent_code_search
```

### Live benchmark (OpenClaw agent)

```bash
# Run all tasks against a model
./scripts/run.sh --model anthropic/claude-sonnet-4

# Run specific tasks with multiple runs
./scripts/run.sh --model anthropic/claude-sonnet-4 --suite task_01_delegate_or_not --runs 3

# Use a custom judge model
./scripts/run.sh --model anthropic/claude-sonnet-4 --judge openai/gpt-4o

# Use custom API endpoint
./scripts/run.sh --model my-model --base-url https://api.example.com/v1 --api-key $MY_KEY
```

Key flags:

| Flag | Description |
|---|---|
| `--model` | Model identifier (e.g. `anthropic/claude-sonnet-4`) |
| `--suite` | `all`, `automated-only`, or comma-separated task IDs |
| `--runs` | Number of runs per task for averaging |
| `--judge` | Judge model/backend for LLM-graded tasks |
| `--base-url` | Custom OpenAI-compatible API endpoint |
| `--no-upload` | Skip leaderboard upload |
| `--timeout-multiplier` | Scale all task timeouts |

### Run tests

```bash
pytest
```

## Task set

| Task | Target | Type | What it tests |
|---|---|---|---|
| `task_01` | C6a | T1 | Delegation decision |
| `task_02` | C6a | T4 | Parallel research delegation |
| `task_03` | C6a | T6 | Failure recovery & replan |
| `task_04` | C6a | T5 | Delegation spec quality |
| `task_05` | C6a | T2 | Avoid redundant delegation |
| `task_06` | C6a | T7 | Conflicting result verification |
| `task_07` | C6a | T2 | Single-layer decomposition |
| `task_08` | C6a | T3 | Dependency-aware decomposition |
| `task_09` | C6b | search | Code search execution |
| `task_10` | C6b | transform | Output format compliance |
| `task_11` | C6b | recovery | Error handling & fallback |

## Project structure

```
tasks/              Task definitions (Markdown + YAML frontmatter)
src/subagent_bench/ Core library (loader, grading, CLI)
scripts/            Live benchmark runner (OpenClaw integration)
examples/           Golden traces and workspace outputs
tests/              Regression tests
docs/               Design documents
```

## Grading

Three grading modes:

- **automated** -- Python checks embedded in each task, fully deterministic
- **llm_judge** -- LLM evaluates transcript against a rubric
- **hybrid** -- Weighted combination of both (configurable per task)

Results include per-task scores, category/dimension aggregation, failure attribution (delegation / execution / integration), and token efficiency metrics.

## Docs

- [Benchmark design](docs/benchmark-design.md)
- [PinchBench analysis](docs/pinchbench-analysis.md)
- [Task template](tasks/TASK_TEMPLATE.md)

## License

[MIT](LICENSE)
