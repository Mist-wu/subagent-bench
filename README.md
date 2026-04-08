# subagent-bench

[English](README.md) | [中文](README_CN.md)

A benchmark for evaluating **multi-agent orchestration**. Helps you answer: which model works best as the main agent, which as the subagent, and which can do both.

## Why

Most benchmarks test single-agent end-to-end performance. `subagent-bench` measures what they miss:

- **C6a (Orchestration)** — delegation, parallelism, replanning, integration
- **C6b (Execution)** — subagent tool use, correctness, error handling

A model can ace execution but fail at orchestration. This benchmark tells you which is which.

## Quick Start

```bash
# Install (Python 3.11+)
pip install -e ".[dev]"

# Grade recorded traces (offline)
subagent-bench grade \
  --traces-dir examples/traces \
  --workspace-root examples/workspaces

# Run live benchmark
./scripts/run.sh --model anthropic/claude-sonnet-4
```

## CLI Flags

| Flag | Description |
|---|---|
| `--model` | Model under test |
| `--suite` | `all` or specific task IDs |
| `--runs` | Repeat count for averaging |
| `--judge` | Override judge model |
| `--base-url` | Custom OpenAI-compatible endpoint |
| `--no-upload` | Skip result upload |

## Reading Results

| Score Pattern | Interpretation |
|---|---|
| High C6a, Low C6b | Best as **main agent** |
| Low C6a, High C6b | Best as **subagent** |
| High both | **Unified model** candidate |

## Tasks

| Task | Target | Description |
|---|---|---|
| `task_01` | C6a | Delegation decision |
| `task_02` | C6a | Parallel delegation |
| `task_03` | C6a | Recovery & replan |
| `task_04` | C6a | Delegation spec quality |
| `task_05` | C6a | Avoid redundant delegation |
| `task_06` | C6a | Conflict verification |
| `task_07` | C6a | Single-layer decomposition |
| `task_08` | C6a | Dependency-aware decomposition |
| `task_09` | C6b | Code search execution |
| `task_10` | C6b | Output compliance |
| `task_11` | C6b | Error handling |

## Project Structure

```
tasks/              → Benchmark task definitions
src/subagent_bench/ → Offline grading, schema, CLI
scripts/            → Live benchmark runner
examples/           → Sample traces & workspaces
docs/               → Design docs & result summaries
tests/              → Regression tests
```

## Docs

- [Benchmark Design](docs/benchmark-design.md)
- [Result Summary Template](docs/result-summary-template.md)
- [PinchBench Analysis](docs/pinchbench-analysis.md)
- [Task Template](tasks/TASK_TEMPLATE.md)

## License

[MIT](LICENSE)
