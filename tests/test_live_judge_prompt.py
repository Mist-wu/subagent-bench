import sys
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import lib_grading  # noqa: E402
from lib_grading import _build_compact_judge_prompt, _build_judge_prompt, grade_task  # noqa: E402
from lib_tasks import Task  # noqa: E402


def _task() -> Task:
    return Task(
        task_id="task_x",
        name="x",
        category="orchestration",
        grading_type="hybrid",
        timeout_seconds=30,
        workspace_files=[],
        prompt="Do a delegated task.",
        expected_behavior="Use native transcript evidence if available.",
        grading_criteria=["Behavior is clearly evidenced."],
        llm_judge_rubric="Criterion A",
        frontmatter={"benchmark_target": "C6a"},
    )


def test_judge_prompt_prefers_native_transcript_evidence() -> None:
    prompt = _build_judge_prompt(_task(), "Tool: sessions_spawn(...)", "Criterion A")

    assert "Prefer native transcript/runtime evidence first." in prompt
    assert "do not deduct points for a missing `delegation_trace.json`" in prompt
    assert "only a compatibility fallback" in prompt


def test_compact_judge_prompt_preserves_native_first_policy() -> None:
    prompt = _build_compact_judge_prompt(_task(), "Tool: sessions_spawn(...)", "Criterion A")

    assert "prefer native transcript/runtime evidence first" in prompt
    assert "Do not penalize missing `delegation_trace.json`" in prompt
    assert "only as a fallback" in prompt


def test_llm_judge_prefers_combined_trace_over_main_transcript(monkeypatch, tmp_path) -> None:
    captured: dict[str, str] = {}

    def fake_call_judge_api(*, prompt: str, model: str, timeout_seconds: float):
        captured["prompt"] = prompt
        return {
            "status": "success",
            "text": '{"scores":{"Execution Quality":1.0},"total":1.0,"notes":""}',
        }

    monkeypatch.setattr(lib_grading, "call_judge_api", fake_call_judge_api)

    task = Task(
        task_id="task_x",
        name="x",
        category="execution",
        grading_type="llm_judge",
        timeout_seconds=30,
        workspace_files=[],
        prompt="Use a real subagent.",
        expected_behavior="Subagent completion should be visible in the combined trace.",
        grading_criteria=["Execution Quality"],
        llm_judge_rubric="Execution Quality",
        frontmatter={"benchmark_target": "C6b"},
    )

    result = grade_task(
        task=task,
        execution_result={
            "status": "success",
            "transcript": [],
            "trace": [
                {
                    "type": "message",
                    "message": {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "toolCall",
                                "name": "sessions_spawn",
                                "arguments": {"task": "leaf work"},
                            }
                        ],
                    },
                }
            ],
            "workspace": str(tmp_path),
        },
        skill_dir=tmp_path,
        judge_model="openai/fake-judge",
        judge_backend="api",
    )

    assert "sessions_spawn" in captured["prompt"]
    assert result.score == 1.0
