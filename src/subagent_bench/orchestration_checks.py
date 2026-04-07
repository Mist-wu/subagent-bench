from __future__ import annotations

import json as jsonlib
from pathlib import Path
from typing import Any, Dict, Iterable, List


def delegate_events(trace: Iterable[Dict[str, Any]], workspace_path: str | None = None) -> List[Dict[str, Any]]:
    trace_bundle = load_delegation_trace(workspace_path)
    if trace_bundle:
        return list(trace_bundle.get("delegations", []))
    events = [event for event in trace if event.get("type") == "delegate"]
    if events:
        return events

    parsed: List[Dict[str, Any]] = []
    for event in trace:
        if event.get("type") != "message":
            continue
        message = event.get("message", {})
        if message.get("role") != "assistant":
            continue
        for item in message.get("content", []):
            if item.get("type") != "toolCall" or item.get("name") != "sessions_spawn":
                continue
            args = item.get("arguments", {})
            parsed.append(
                {
                    "delegation_id": args.get("label") or args.get("task") or item.get("id"),
                    "assignee": args.get("runtime") or args.get("label") or "subagent",
                    "instruction": args.get("task", ""),
                    "inputs": [args.get("cwd")] if args.get("cwd") else [],
                    "success_criteria": "Subagent completes the requested delegated work.",
                    "output_path": _extract_output_path(args.get("task", "")),
                }
            )
    return parsed


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
        return jsonlib.loads(trace_path.read_text(encoding="utf-8"))
    except jsonlib.JSONDecodeError:
        return {}


def delegation_fields_present(event: Dict[str, Any]) -> bool:
    aliases = {
        "delegation_id": ["delegation_id", "id", "task", "label"],
        "assignee": ["assignee", "delegate", "runtime", "agent"],
        "instruction": ["instruction", "task", "goal", "prompt"],
        "inputs": ["inputs", "context_files", "artifacts", "workspace"],
        "success_criteria": ["success_criteria", "success", "done_when", "acceptance_criteria"],
        "output_path": ["output_path", "artifact", "destination", "target_file"],
    }
    for field_aliases in aliases.values():
        value = _first_present(event, field_aliases)
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


def transcript_has_tool_call(
    trace: Iterable[Dict[str, Any]],
    tool_name: str,
    argument_contains: str | None = None,
) -> bool:
    for event in trace:
        if event.get("type") == "tool_use" and event.get("tool") == tool_name:
            return True
        if event.get("type") != "message":
            continue
        message = event.get("message", {})
        for item in message.get("content", []):
            if item.get("type") != "toolCall" or item.get("name") != tool_name:
                continue
            if argument_contains and argument_contains not in jsonlib.dumps(item.get("arguments", {}), ensure_ascii=False):
                continue
            return True
    return False


def transcript_has_tool_result_error(
    trace: Iterable[Dict[str, Any]],
    tool_name: str | None = None,
    argument_contains: str | None = None,
) -> bool:
    matching_tool_call_ids: set[str] = set()
    if argument_contains:
        for event in trace:
            if event.get("type") != "message":
                continue
            message = event.get("message", {})
            if message.get("role") != "assistant":
                continue
            for item in message.get("content", []):
                if item.get("type") != "toolCall":
                    continue
                if tool_name and item.get("name") != tool_name:
                    continue
                args_text = jsonlib.dumps(item.get("arguments", {}), ensure_ascii=False)
                if argument_contains in args_text:
                    matching_tool_call_ids.add(item.get("id"))

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
        if matching_tool_call_ids and message.get("toolCallId") not in matching_tool_call_ids:
            continue
        details = message.get("details", {})
        if details.get("status") == "error":
            return True
    return False


def _first_present(event: Dict[str, Any], keys: List[str]) -> Any:
    for key in keys:
        value = event.get(key)
        if value is not None:
            return value
    return None


def _extract_output_path(instruction: str) -> str:
    for token in instruction.replace("`", " ").split():
        if "/" in token and "." in token:
            return token.strip(".,:;")
    return ""
