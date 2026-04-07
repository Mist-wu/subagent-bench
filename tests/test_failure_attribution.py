from subagent_bench.grading import infer_failure_attribution
from subagent_bench.models import Task


def _task(target: str) -> Task:
    return Task(
        task_id="x",
        name="x",
        category="orchestration" if target == "C6a" else "execution",
        benchmark_target=target,
        task_type="T0",
        dimensions=[],
        grading_type="automated",
        timeout_seconds=1,
        workspace_files=[],
        prompt="",
        expected_behavior="",
        grading_criteria=[],
    )


def test_delegation_failure_is_identified() -> None:
    labels = infer_failure_attribution(
        _task("C6a"),
        {
            "delegates_when_needed": 0.0,
            "integration_quality": 1.0,
        },
    )
    assert "Delegation Failure" in labels


def test_execution_failure_is_identified() -> None:
    labels = infer_failure_attribution(
        _task("C6b"),
        {
            "tool_use_correctness": 0.0,
            "result_fidelity": 0.0,
        },
    )
    assert labels == ["Execution Failure"]


def test_integration_failure_is_identified() -> None:
    labels = infer_failure_attribution(
        _task("C6a"),
        {
            "delegates_when_needed": 1.0,
            "integration_quality": 0.0,
        },
    )
    assert "Integration Failure" in labels
