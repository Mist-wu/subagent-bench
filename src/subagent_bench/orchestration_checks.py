from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List


def delegate_events(trace: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [event for event in trace if event.get("type") == "delegate"]


def subagent_results(trace: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [event for event in trace if event.get("type") == "subagent_result"]


def replan_events(trace: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [event for event in trace if event.get("type") == "replan"]


def delegation_fields_present(event: Dict[str, Any]) -> bool:
    required = ["delegation_id", "assignee", "instruction", "inputs", "success_criteria", "output_path"]
    for field in required:
        value = event.get(field)
        if value is None:
            return False
        if isinstance(value, str) and not value.strip():
            return False
        if isinstance(value, list) and not value:
            return False
    return True


def artifact_exists(workspace_path: str, relative_path: str) -> bool:
    return (Path(workspace_path) / relative_path).exists()


def artifact_contains(workspace_path: str, relative_path: str, needles: List[str]) -> bool:
    artifact = Path(workspace_path) / relative_path
    if not artifact.exists():
        return False
    content = artifact.read_text(encoding="utf-8").lower()
    return all(needle.lower() in content for needle in needles)
