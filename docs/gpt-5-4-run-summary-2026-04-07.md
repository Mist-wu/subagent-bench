# GPT-5.4 Run Summary

Run date: 2026-04-07  
Model: `openai-codex/gpt-5.4`  
Suite: all 11 tasks  
Run id: `0013`  
Result JSON: [results/live-openai-full-final/0013_openai-codex-gpt-5-4.json](/Users/wu/Github/subagent-bench/results/live-openai-full-final/0013_openai-codex-gpt-5-4.json)  
Transcripts: [results/live-openai-full-final/0013_transcripts](/Users/wu/Github/subagent-bench/results/live-openai-full-final/0013_transcripts)

## Headline

`gpt-5.4` scored `6.70 / 11`, or `60.9%`, on the full live `subagent-bench` run.

The clearest conclusion is that `C6b` is already strong while `C6a` remains the main bottleneck:

- `C6a` orchestration average: `48.4%` across 8 tasks
- `C6b` execution average: `94.2%` across 3 tasks

This run supports the benchmark design hypothesis: measuring only subagent execution would significantly overestimate system quality. The main agent is often able to choose a reasonable split, but it still fails on waiting, integration, dependency ordering, and recovery.

## Selection Translation

- `gpt-5.4` is suitable as a `subagent`.
- `gpt-5.4` still has clear weaknesses as a `main agent`.
- In a split-role architecture with a stronger orchestrator and a stronger executor, `gpt-5.4` looks more like an executor candidate.
- If the system requires one model to handle both orchestration and execution, `gpt-5.4` is usable but not the best candidate.

## Score Table

| Task | Target | Type | Score | Interpretation |
|---|---|---|---:|---|
| `task_01_delegate_or_not` | C6a | T1 | 0.9733 | Very strong delegation decision; local vs delegated split was mostly correct and well integrated. |
| `task_02_parallel_research` | C6a | T4 | 0.2467 | Parallel split was good, but the main agent yielded before collecting and merging delegated results. |
| `task_03_replan_after_failure` | C6a | T6 | 0.0000 | No meaningful recovery behavior; failed delegation was not followed by a real replan and corrected retry. |
| `task_04_fixed_subagent_spec_quality` | C6a | T5 | 0.5400 | Delegation target was mostly right, but spec quality and completion reliability were only partial. |
| `task_05_avoid_redundant_delegation` | C6a | T2 | 0.9600 | Strong orchestration restraint; the agent kept a narrow scope local and avoided redundant delegation. |
| `task_06_verify_conflicting_results` | C6a | T7 | 0.5167 | Conflict arbitration was logically correct, but execution overhead and incomplete automated signals pulled the score down. |
| `task_07_single_layer_decomposition` | C6a | T2 | 0.6333 | Decomposition was clean, but the final merge was not fully reliable. |
| `task_08_dependency_aware_decomposition` | C6a | T3 | 0.0000 | Dependency-aware sequencing failed; the agent reused an unrelated plan instead of respecting required order. |
| `task_09_subagent_code_search` | C6b | execution_search | 0.9175 | Strong execution quality with correct report contents; only efficiency noise remained. |
| `task_10_subagent_output_transform` | C6b | execution_transform | 0.9100 | Correct output structure and fidelity; minor deductions came from unnecessary tool activity. |
| `task_11_subagent_error_handling` | C6b | execution_recovery | 1.0000 | Fully passed the automated fallback/error-handling task. |

## Main Findings

### 1. Execution is much stronger than orchestration

`gpt-5.4` is already reliable at bounded execution tasks:

- exact code search
- deterministic output transformation
- fallback/error handling

But orchestration quality is uneven:

- it can make good local-vs-delegate decisions
- it can write decent delegation specs
- it often fails to wait for delegated work to finish
- it often fails to merge delegated outputs back into the final artifact
- it is weak on recovery and dependency-aware replanning

### 2. The most important failure mode is not “bad delegation choice”

The biggest losses were not caused by obviously wrong delegation policy. In several tasks, the split itself was reasonable, but end-to-end orchestration still failed because the main agent:

- yielded too early
- did not integrate subagent outputs
- did not run a real retry after failure
- did not respect dependency order

That distinction matters. If this benchmark only measured whether the agent spawned the “right” subtask, `task_02` and `task_07` would look much better than they actually are.

### 3. Recovery and dependency handling remain the hardest orchestration slices

The two zero-score orchestration tasks were:

- `task_03_replan_after_failure`
- `task_08_dependency_aware_decomposition`

Those tasks require the main agent to notice failure, change plan, and continue with new context or correct ordering. This appears to be materially harder than:

- deciding whether to delegate
- avoiding redundant delegation
- writing a plausible delegation spec

## Efficiency

- Total tokens: `1,555,010`
- Total requests: `99`
- Total cost: `$1.1231`
- Total execution time: `1160.32s`
- Average tokens per task: `141,364.5`

Most expensive tasks were not necessarily the best-performing ones. `task_03` and `task_04` consumed a large amount of budget while still underperforming, which is another signal that orchestration failures can be expensive even when execution quality is high.

## Runtime Notes

This was a full live run with hybrid grading preserved. To make the run stable enough to complete, the benchmark runtime was hardened in several places:

- fixed exact agent-to-workspace matching to avoid cross-run workspace contamination
- added recovery for transient `session file locked` OpenClaw failures
- made `delegation_trace.json` parsing tolerant to both object and top-level-array formats
- made judge-response parsing robust to noisy prefixes like repeated `NO_REPLY`
- added a compact fallback judge prompt when a provider flags the original prompt as potential policy risk

These changes did not reduce benchmark scope or remove grading functionality; they were runtime compatibility fixes needed to make the full benchmark runnable end-to-end.

## Conclusion

This run validates the benchmark direction.

If the goal is to evaluate multi-agent systems rather than single-agent coding ability, `C6a` must be measured separately from `C6b`. `gpt-5.4` is already strong as a subagent executor, but its main-agent orchestration quality is still far from its execution ceiling. The benchmark is therefore capturing a real and decision-relevant gap rather than a redundant restatement of subagent competence.
