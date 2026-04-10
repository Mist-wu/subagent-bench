import sys
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib_agent import (  # noqa: E402
    _extract_usage_from_transcripts,
    _normalize_native_subagent_worker_prompt,
    _resolve_live_task_prompt,
    _wait_for_transcript_settle,
)
from lib_tasks import Task  # noqa: E402


def test_live_execution_tasks_are_wrapped_for_native_subagents() -> None:
    task = Task(
        task_id="task_09",
        name="x",
        category="execution",
        grading_type="automated",
        timeout_seconds=30,
        workspace_files=[],
        prompt="You are a subagent. Search the repo and write a report.",
        expected_behavior="",
        grading_criteria=[],
        frontmatter={"benchmark_target": "C6b", "live_execution_mode": "native_subagent"},
    )

    prompt = _resolve_live_task_prompt(task)

    assert 'runtime: "subagent"' in prompt
    assert "You are the main agent for this benchmark task." in prompt
    assert "Search the repo and write a report." in prompt
    assert "You are a subagent. Search the repo and write a report." not in prompt


def test_native_subagent_worker_prompt_strips_legacy_role_prefix() -> None:
    prompt = _normalize_native_subagent_worker_prompt(
        "You are a subagent. Search the repo and write a report."
    )

    assert prompt == "Search the repo and write a report."


def test_usage_is_aggregated_across_parent_and_child_transcripts() -> None:
    transcripts = [
        [
            {
                "type": "message",
                "message": {
                    "role": "assistant",
                    "usage": {
                        "input": 10,
                        "output": 5,
                        "cacheRead": 1,
                        "cacheWrite": 0,
                        "totalTokens": 16,
                        "cost": {"total": 0.01},
                    },
                },
            }
        ],
        [
            {
                "type": "message",
                "message": {
                    "role": "assistant",
                    "usage": {
                        "input": 20,
                        "output": 8,
                        "cacheRead": 0,
                        "cacheWrite": 2,
                        "totalTokens": 30,
                        "cost": {"total": 0.02},
                    },
                },
            }
        ],
    ]

    usage = _extract_usage_from_transcripts(transcripts)

    assert usage["input_tokens"] == 30
    assert usage["output_tokens"] == 13
    assert usage["total_tokens"] == 46
    assert usage["cost_usd"] == 0.03
    assert usage["request_count"] == 2
    assert usage["session_count"] == 2


def test_async_settle_waits_for_child_transcript_updates(monkeypatch, tmp_path) -> None:
    import lib_agent

    main_path = tmp_path / "main.jsonl"
    child_path = tmp_path / "child.jsonl"
    main_path.write_text("main", encoding="utf-8")
    child_path.write_text("child", encoding="utf-8")

    class FakeClock:
        def __init__(self) -> None:
            self.now = 1000.0

        def time(self) -> float:
            return self.now

        def sleep(self, seconds: float) -> None:
            self.now += seconds

    clock = FakeClock()
    monkeypatch.setattr(lib_agent.time, "time", clock.time)
    monkeypatch.setattr(lib_agent.time, "sleep", clock.sleep)

    def fake_load_transcript(agent_id: str, session_id: str, started_at: float):
        return ([{"type": "message", "message": {"role": "assistant", "content": []}}], main_path)

    def fake_load_related(agent_id: str, started_at: float, primary_path):
        if clock.now < 1004.0:
            entries = [{"type": "message", "message": {"role": "assistant", "content": []}}]
            child_path.write_text("child-v1", encoding="utf-8")
        else:
            entries = [
                {"type": "message", "message": {"role": "assistant", "content": []}},
                {"type": "message", "message": {"role": "user", "content": []}},
            ]
            child_path.write_text("child-v2", encoding="utf-8")
        return [{"path": child_path, "entries": entries, "mtime": child_path.stat().st_mtime}]

    monkeypatch.setattr(lib_agent, "_load_transcript", fake_load_transcript)
    monkeypatch.setattr(lib_agent, "_load_related_transcripts", fake_load_related)

    transcript, transcript_path, related = _wait_for_transcript_settle(
        "agent-x",
        "session-x",
        999.0,
        main_path,
        quiet_seconds=4.0,
        max_wait_seconds=12.0,
    )

    assert transcript_path == main_path
    assert len(transcript) == 1
    assert len(related) == 1
    assert len(related[0]["entries"]) == 2
