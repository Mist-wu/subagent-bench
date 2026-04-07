# subagent-bench

`subagent-bench` is a model-selection benchmark for multi-agent systems.

It is designed to answer three questions:

- which model is best suited for the `main agent`
- which model is best suited for the `subagent`
- which model is acceptable as a single model for both roles

The benchmark separates:

- `C6a`: main-agent orchestration
- `C6b`: subagent execution

That separation matters for model selection. A model can be strong at execution and still be weak at delegation, waiting, integration, or replan.

## Install

Requires Python 3.11+.

```bash
pip install -e ".[dev]"
```

## Run

Offline grading:

```bash
subagent-bench grade \
  --traces-dir examples/traces \
  --workspace-root examples/workspaces
```

Live benchmark:

```bash
./scripts/run.sh --model anthropic/claude-sonnet-4
```

Useful flags:

| Flag | Meaning |
|---|---|
| `--model` | model under test |
| `--suite` | `all` or specific task IDs |
| `--runs` | repeat runs for averaging |
| `--judge` | override judge model |
| `--base-url` | custom OpenAI-compatible endpoint |
| `--no-upload` | skip upload |

## How To Read Results

Use the benchmark for selection, not just scoring.

- high `C6a`, lower `C6b`: better `main agent` candidate
- lower `C6a`, high `C6b`: better `subagent` candidate
- high on both with acceptable cost/latency: better unified-model candidate

The final output should be read as:

1. `Main-Agent Fit`
2. `Subagent Fit`
3. `Unified-Model Fit`
4. cost / latency / stability tradeoffs

## Task Set

| Task | Target | Type | Purpose |
|---|---|---|---|
| `task_01` | C6a | T1 | delegation decision |
| `task_02` | C6a | T4 | parallel delegation |
| `task_03` | C6a | T6 | recovery and replan |
| `task_04` | C6a | T5 | delegation spec quality |
| `task_05` | C6a | T2 | avoid redundant delegation |
| `task_06` | C6a | T7 | conflict verification |
| `task_07` | C6a | T2 | single-layer decomposition |
| `task_08` | C6a | T3 | dependency-aware decomposition |
| `task_09` | C6b | execution_search | code search execution |
| `task_10` | C6b | execution_transform | output compliance |
| `task_11` | C6b | execution_recovery | error handling |

## Layout

```text
tasks/              benchmark tasks
src/subagent_bench/ offline grading and CLI
scripts/            live runner
examples/           sample traces and outputs
docs/               design notes and result summaries
tests/              regression tests
```

## Docs

- [Benchmark design](docs/benchmark-design.md)
- [Result summary template](docs/result-summary-template.md)
- [PinchBench analysis](docs/pinchbench-analysis.md)
- [Task template](tasks/TASK_TEMPLATE.md)
