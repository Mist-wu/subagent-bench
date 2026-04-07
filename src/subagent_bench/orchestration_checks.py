from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


def delegate_events(trace: Iterable[Dict[str, Any]], workspace_path: str | None = None) -> List[Dict[str, Any]]:
    trace_bundle = load_delegation_trace(workspace_path)
    if trace_bundle:
        return list(trace_bundle.get("delegations", []))
    return [event for event in trace if event.get("type") == "delegate"]


def subagent_results(trace: Iterable[Dict[str, Any]], workspace_path: str | None = None) -> List[Dict[str, Any]]:
    trace_bundle = load_delegation_trace(workspace_path)
    if trace_bundle:
        return list(trace_bundle.get("subagent_results", []))
    return [event for event in trace if event.get("type") == "subagent_result"]


def replan_events(trace: Iterable[Dict[str, Any]], workspace_path: str | None = None) -> List[Dict[str, Any]]:
    trace_bundle = load_delegation_trace(workspace_path)
    if trace_bundle:
        return list(trace_bundle.get("replans", []))
    return [event for event in trace if event.get("type") == "replan"]


def verification_events(trace: Iterable[Dict[str, Any]], workspace_path: str | None = None) -> List[Dict[str, Any]]:
    trace_bundle = load_delegation_trace(workspace_path)
    if trace_bundle:
        return list(trace_bundle.get("verifications", []))
    return [event for event in trace if event.get("type") == "verification"]


def load_delegation_trace(workspace_path: str | None) -> Dict[str, Any]:
    if not workspace_path:
        return {}
    trace_path = Path(workspace_path) / "delegation_trace.json"
    if not trace_path.exists():
        return {}
    try:
        return json.loads(trace_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


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


def transcript_has_tool_call(trace: Iterable[Dict[str, Any]], tool_name: str) -> bool:
    for event in trace:
        if event.get("type") == "tool_use" and event.get("tool") == tool_name:
            return True
        if event.get("type") != "message":
            continue
        message = event.get("message", {})
        for item in message.get("content", []):
            if item.get("type") == "toolCall" and item.get("name") == tool_name:
                return True
    return False


def transcript_has_tool_result_error(trace: Iterable[Dict[str, Any]], tool_name: str | None = None) -> bool:
    for event in trace:
        if event.get("type") == "tool_result":
            if event.get("status") == "error" and (tool_name is None or event.get("tool") == tool_name):
                return True
        if event.get("type") != "message":
            continue
        message = event.get("message", {})
        if message.get("role") != "toolResult":
            continue
        if tool_name and message.get("toolName") != tool_name:
            continue
        details = message.get("details", {})
        if details.get("status") == "error":
            return True
    return False
