# Benchmark Design

## Goal

`subagent-bench` exists to help choose models for a multi-agent system.

It is not primarily a general agent benchmark. It is a role-selection benchmark:

- `C6a` selects models for the `main agent`
- `C6b` selects models for the `subagent`
- `C6a + C6b + cost/latency` select models for unified use

## What We Measure

### C6a: Main-Agent Orchestration

The main agent is judged on:

- whether to delegate
- how to split work
- whether it respects dependency and parallel structure
- delegation spec quality
- integration quality
- recovery and replan

### C6b: Subagent Execution

The subagent is judged on:

- intent understanding
- tool use
- output correctness
- output format compliance
- error and timeout handling

## Why Intermediate Signals Matter

End-to-end success alone is not enough for model selection.

The benchmark records:

- spawn behavior
- delegation specs
- execution order
- subagent results
- integration and retry behavior
- transcript and tool traces

Without these signals, orchestration failure and execution failure are easy to confuse.

## Scoring

Each task uses one of:

- `automated`
- `llm_judge`
- `hybrid`

For selection, the important outputs are:

1. `Main-Agent Fit`
2. `Subagent Fit`
3. `Unified-Model Fit`
4. cost / latency / stability

## Failure Attribution

Every failure should be read as one of:

- `Delegation Failure`
- `Execution Failure`
- `Integration Failure`

This is the core reason the benchmark is useful for model choice. It tells you not only which model scored lower, but why.

## Task Types

- `T1`: delegation decision
- `T2`: single-layer decomposition
- `T3`: dependency-aware decomposition
- `T4`: parallel decomposition
- `T5`: delegation spec quality
- `T6`: failure recovery
- `T7`: multi-subagent aggregation

## Interpretation

A model is a better `main agent` candidate when it has:

- strong `C6a`
- low integration failure
- low over-delegation / under-delegation

A model is a better `subagent` candidate when it has:

- strong `C6b`
- high output fidelity
- strong error handling

A model is a better unified candidate when it has:

- strong `C6a`
- strong `C6b`
- acceptable cost and latency
