# subagent-bench

[English](README.md) | [中文](README_CN.md)

A benchmark for evaluating **multi-agent orchestration**. Helps you answer: which model works best as the main agent, which as the subagent, and which can do both.

## Why

Most benchmarks test single-agent end-to-end performance. `subagent-bench` measures what they miss:

- **C6a (Orchestration)** — delegation, parallelism, replanning, integration
- **C6b (Execution)** — subagent tool use, correctness, error handling

A model can ace execution but fail at orchestration. This benchmark tells you which is which.

Live `C6b` tasks are evaluated through OpenClaw's native `sessions_spawn` path so the leaf work is completed by a real child session instead of by the main session roleplaying as a subagent.

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

## Task Format

Each task is a Markdown file with YAML frontmatter:

```yaml
---
id: task_01
benchmark_target: C6a
task_type: T1
dimensions: ["delegation_decision_accuracy"]
grading_type: automated     # automated | llm_judge | hybrid
timeout_seconds: 180
---
```

Sections: `## Prompt`, `## Expected Behavior`, `## Grading Criteria`, `## Automated Checks`, `## LLM Judge Rubric`.

## Trace Format

Traces are JSON with an `events` array. Key event types:

| Event | Meaning |
|---|---|
| `delegate` | Main agent delegates to subagent |
| `subagent_result` | Subagent returns result |
| `replan` | Main agent replans |
| `tool_use` / `tool_result` | Tool call and response |
| `artifact_written` | Output artifact written |
| `verification` | Result verification |

## Grading

Three modes, configured per task via `grading_type`:

- **`automated`** — deterministic Python `grade(trace, workspace_path) → dict` embedded in each task's `## Automated Checks` block; scores are weighted-averaged to `[0.0, 1.0]`.
- **`llm_judge`** — structured prompt (task prompt + transcript + rubric) sent to a judge LLM; returns `{"scores": {...}, "total": float}`. All tasks share three criteria: `split_quality`, `delegation_clarity`, `integration_reliability`.
- **`hybrid`** — weighted combination of both, configured via `grading_weights` in frontmatter (e.g., `automated: 0.6`, `llm_judge: 0.4`).

Failures are attributed to one of: **Delegation**, **Execution**, or **Integration**.

**Offline vs Live:**

| | Offline (`subagent-bench grade`) | Live (`scripts/benchmark.py`) |
|---|---|---|
| Trace source | Pre-recorded JSON in `examples/traces/` | Real-time agent execution |
| LLM judge | Reads embedded `judge_result` from trace | Calls judge API in real time |
| Use case | Regression testing | Full benchmark against real agents |

## Project Structure

```
tasks/              → Benchmark task definitions
src/subagent_bench/ → Offline grading, schema, CLI
scripts/            → Live benchmark runner
examples/           → Sample traces & workspaces
docs/               → Design docs & result summaries
tests/              → Regression tests
```

## Scoring Notes

`C6a` grading prefers native transcript signals first and treats `delegation_trace.json` as a compatibility fallback. Recovery can be recognized either as a corrected redelegation or as a visible main-session local fix after a failed delegation.

## Docs

- [Benchmark Design](docs/benchmark-design.md)
- [Result Summary Template](docs/result-summary-template.md)
- [PinchBench Analysis](docs/pinchbench-analysis.md)
- [Task Template](tasks/TASK_TEMPLATE.md)

## License

[MIT](LICENSE)
