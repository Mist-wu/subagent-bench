---
id: task_01_delegate_or_not
name: Delegate Only The Expensive Slice
category: orchestration
benchmark_target: C6a
task_type: T1
dimensions: ["delegation_decision_accuracy", "delegation_spec_completeness", "integration_quality"]
grading_type: hybrid
timeout_seconds: 300
workspace_files:
  - path: "release-checklist.md"
    content: |
      # Release Checklist

      - [ ] Rename the `Changelog` heading in `answer.md` to `Release Notes`.
      - [ ] Run a repo-wide dependency audit and save it to `reports/dependency_audit.md`.
      - [ ] Summarize the dependency audit in `answer.md`.
  - path: "answer.md"
    content: |
      # Release Checklist Review

      ## Changelog

      - Trivial rename pending.
      - Dependency audit pending.
  - path: "package.json"
    content: |
      {
        "name": "release-candidate",
        "version": "0.9.0",
        "scripts": {
          "build": "tsc -p tsconfig.json"
        },
        "dependencies": {
          "express": "^4.18.0",
          "lodash": "^4.17.21"
        }
      }
  - path: "src/api/server.ts"
    content: |
      import express from "express";

      export function buildServer() {
        const app = express();
        app.get("/healthz", (_req, res) => res.json({ ok: true }));
        return app;
      }
grading_weights:
  automated: 0.6
  llm_judge: 0.4
---

## Prompt

Review the provided release checklist. The main agent should handle the trivial heading rename in `answer.md` directly, but it should delegate the repo-wide audit to a subagent. The delegated subagent should write its findings to `reports/dependency_audit.md`, and the main agent should integrate that result into `answer.md`.

For benchmark observability, also write `delegation_trace.json` in the workspace root with this exact schema:

```json
{
  "delegations": [
    {
      "delegation_id": "dependency-audit",
      "assignee": "subagent",
      "instruction": "Run the repo-wide dependency audit",
      "inputs": ["release-checklist.md", "package.json", "src/api/server.ts"],
      "success_criteria": "Create reports/dependency_audit.md with blockers and warnings",
      "output_path": "reports/dependency_audit.md"
    }
  ],
  "subagent_results": [
    {
      "delegation_id": "dependency-audit",
      "status": "success",
      "summary": "Short summary of the delegated result"
    }
  ],
  "replans": [],
  "verifications": [
    {
      "artifact": "answer.md",
      "checks": ["rename handled directly", "dependency audit integrated"]
    }
  ]
}
```

## Expected Behavior

The main agent should create exactly one delegation for the expensive audit, provide enough context for the subagent to finish independently, and avoid delegating the trivial work. After the subagent returns, the main agent should synthesize the audit into the final answer.

## Grading Criteria

- [ ] Exactly one delegation is created
- [ ] Delegation spec contains goal, inputs, success criteria, and output path
- [ ] Delegated artifact is produced
- [ ] Main agent integrates the delegated result into `answer.md`

## Automated Checks

```python
def grade(trace: list, workspace_path: str) -> dict:
    from subagent_bench.orchestration_checks import (
        artifact_contains,
        artifact_exists,
        delegate_events,
        delegation_fields_present,
    )

    delegations = delegate_events(trace, workspace_path)
    only_one = 1.0 if len(delegations) == 1 else 0.0
    complete_spec = 1.0 if delegations and delegation_fields_present(delegations[0]) else 0.0
    delegated_artifact = 1.0 if artifact_exists(workspace_path, "reports/dependency_audit.md") else 0.0
    integrated = 1.0 if (
        artifact_contains(
            workspace_path,
            "answer.md",
            ["dependency audit", "reports/dependency_audit.md", "release notes"],
        )
        or artifact_contains(
            workspace_path,
            "answer.md",
            ["dependency audit", "reports/dependency_audit.md", "rename handled directly"],
        )
    ) else 0.0

    return {
        "delegates_when_needed": only_one,
        "avoids_over_delegation": only_one,
        "delegation_spec_completeness": complete_spec,
        "delegated_artifact_exists": delegated_artifact,
        "integration_quality": integrated,
    }
```

## LLM Judge Rubric

### Criterion 1: Split Quality
**Score 1.0**: Delegates only the expensive slice and keeps trivial work local.
**Score 0.5**: Delegation choice is partly reasonable but includes avoidable delegation or misses useful delegation.
**Score 0.0**: Delegation policy is clearly wrong for the task.

### Criterion 2: Delegation Clarity
**Score 1.0**: The delegated instruction is clear, scoped, and contains the context needed to act independently.
**Score 0.5**: The instruction is understandable but underspecified.
**Score 0.0**: The delegation is vague or missing critical information.

### Criterion 3: Integration Reliability
**Score 1.0**: Final answer accurately integrates the delegated result and keeps the main-thread work coherent.
**Score 0.5**: Integration is partial or somewhat unreliable.
**Score 0.0**: Integration is missing or misleading.
