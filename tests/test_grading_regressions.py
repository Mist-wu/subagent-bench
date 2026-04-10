import json
from pathlib import Path

from subagent_bench.grading import grade_task
from subagent_bench.task_loader import TaskLoader


def test_partial_trace_receives_partial_credit(tmp_path) -> None:
    task = TaskLoader(Path("tasks")).load_task(Path("tasks/task_01_delegate_or_not.md"))

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "reports").mkdir()
    (workspace / "answer.md").write_text(
        "# Release Notes\n\nDependency review integrated from dependency_audit.md.\n",
        encoding="utf-8",
    )
    (workspace / "reports" / "dependency_audit.md").write_text(
        "Dependency audit findings.\n",
        encoding="utf-8",
    )
    (workspace / "delegation_trace.json").write_text(
        json.dumps(
            {
                "delegations": [
                    {
                        "delegation_id": "dep-audit",
                        "assignee": "subagent",
                        "instruction": "Run the audit",
                        "inputs": ["package.json"],
                        "success_criteria": ["Write the report"],
                    }
                ],
                "subagent_results": [
                    {
                        "delegation_id": "dep-audit",
                        "status": "success",
                        "summary": "Done",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    trace = tmp_path / "trace.json"
    trace.write_text(json.dumps({"events": []}), encoding="utf-8")

    result = grade_task(task, trace, workspace)

    assert 0.0 < result.score < 1.0
    assert result.breakdown["delegation_spec_completeness"] == 5 / 6
    assert result.breakdown["delegated_artifact_exists"] == 0.5

