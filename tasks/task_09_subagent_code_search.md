---
id: task_09_subagent_code_search
name: Subagent Code Search Execution
category: execution
benchmark_target: C6b
task_type: execution_search
dimensions: ["intent_understanding", "tool_use_correctness", "completion_rate", "result_fidelity"]
grading_type: hybrid
timeout_seconds: 180
workspace_files:
  - path: "src/api/users.ts"
    content: |
      import { db } from "../db";
      
      export function listUsers() {
        return db.query("SELECT id, email FROM users");
      }
      
      export function createUser(email: string) {
        return db.insert("users", { email });
      }
      
      export function deleteUser(id: string) {
        return db.delete("users", { id });
      }
      
      export function getUserById(id: string) {
        return db.rawQuery("SELECT * FROM users WHERE id = ?", [id]);
      }
  - path: "src/api/orders.ts"
    content: |
      import { db } from "../db";
      
      export function listOrders() {
        return db.query("SELECT id, status FROM orders");
      }
      
      export function createOrder(payload: unknown) {
        return db.insert("orders", payload);
      }
      
      export function getOrder(id: string) {
        return db.query("SELECT id, status FROM orders WHERE id = ?", [id]);
      }
      
      export function cancelOrder(id: string) {
        return db.update("orders", { status: "canceled" }, { id });
      }
      
      export function getOrdersByUser(userId: string) {
        return db.rawQuery("SELECT * FROM orders WHERE user_id = ?", [userId]);
      }
      
      export function summarizeOrders() {
        return db.query("SELECT status, count(*) FROM orders GROUP BY status");
      }
      
      export function reopenOrder(id: string) {
        return db.update("orders", { status: "open" }, { id });
      }
      
      export function archiveOrder(id: string) {
        return db.update("orders", { archived: true }, { id });
      }
      
      export function countOrders() {
        return db.query("SELECT count(*) FROM orders");
      }
      
      export function listFailedOrders() {
        return db.query("SELECT id FROM orders WHERE status = 'failed'");
      }
      
      export function lookupLegacyOrders(status: string) {
        return db.rawQuery("SELECT * FROM orders_legacy WHERE status = ?", [status]);
      }
grading_weights:
  automated: 0.7
  llm_judge: 0.3
---

## Prompt

You are a subagent. Search the codebase for deprecated `db.rawQuery()` calls and write a precise report to `reports/raw_query_report.md`. Preserve exact file paths and line numbers.

## Expected Behavior

The subagent should understand the delegated goal, use search tooling correctly, find all targeted occurrences, and produce the requested report without asking the main agent for clarification.

## Grading Criteria

- [ ] Search tool is used
- [ ] Report artifact exists
- [ ] All occurrences are captured
- [ ] Report preserves paths and line numbers

## Automated Checks

```python
def grade(trace: list, workspace_path: str) -> dict:
    from pathlib import Path
    from subagent_bench.orchestration_checks import transcript_has_tool_call

    used_search_tool = 1.0 if transcript_has_tool_call(trace, "exec", "rawQuery") else 0.0
    artifact = Path(workspace_path) / "reports/raw_query_report.md"
    artifact_exists = 1.0 if artifact.exists() else 0.0

    fidelity = 0.0
    if artifact.exists():
        content = artifact.read_text(encoding="utf-8").lower()
        fidelity = 1.0 if "src/api/users.ts:14" in content and "src/api/orders.ts:22" in content and "src/api/orders.ts:41" in content else 0.0

    return {
        "tool_use_correctness": used_search_tool,
        "completion_rate": artifact_exists,
        "result_fidelity": fidelity,
        "intent_understanding": 1.0 if artifact_exists and fidelity else 0.0,
    }
```

## LLM Judge Rubric

### Criterion 1: Analysis Quality
**Score 1.0**: The report is precise, correctly scoped, and useful for remediation.
**Score 0.5**: The report is partly useful but thin or somewhat imprecise.
**Score 0.0**: The report is low-quality or not useful.

### Criterion 2: Execution Quality
**Score 1.0**: The subagent executes independently and cleanly with no unnecessary wandering.
**Score 0.5**: Execution is adequate but inefficient or shaky.
**Score 0.0**: Execution quality is poor.
