from __future__ import annotations

import json as jsonlib
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List


def delegate_events(trace: Iterable[Dict[str, Any]], workspace_path: str | None = None) -> List[Dict[str, Any]]:
    trace_list = list(trace)
    native = _native_delegate_events(trace_list)
    trace_bundle = load_delegation_trace(workspace_path)
    if trace_bundle:
        native = _merge_event_lists(native, list(trace_bundle.get("delegations", [])), "delegation_id")
    return native


def subagent_results(trace: Iterable[Dict[str, Any]], workspace_path: str | None = None) -> List[Dict[str, Any]]:
    trace_list = list(trace)
    native = _native_subagent_results(trace_list)
    trace_bundle = load_delegation_trace(workspace_path)
    if trace_bundle:
        native = _merge_event_lists(
            native,
            list(trace_bundle.get("subagent_results", [])),
            "delegation_id",
        )
    return native


def concurrent_delegate_events(trace: Iterable[Dict[str, Any]], workspace_path: str | None = None) -> List[Dict[str, Any]]:
    delegations = delegate_events(trace, workspace_path)
    results = subagent_results(trace, workspace_path)
    if not delegations:
        return []

    first_result_index = min(
        (int(result.get("__index__", 1_000_000_000)) for result in results),
        default=1_000_000_000,
    )
    return [
        event
        for event in delegations
        if int(event.get("__index__", 1_000_000_000)) < first_result_index
    ]


def replan_events(trace: Iterable[Dict[str, Any]], workspace_path: str | None = None) -> List[Dict[str, Any]]:
    trace_list = list(trace)
    native = _native_replan_events(trace_list)
    trace_bundle = load_delegation_trace(workspace_path)
    if trace_bundle:
        native = _merge_event_lists(native, list(trace_bundle.get("replans", [])), "reason")
    return native


def local_recovery_events(trace: Iterable[Dict[str, Any]], workspace_path: str | None = None) -> List[Dict[str, Any]]:
    trace_list = list(trace)
    native = _native_local_recovery_events(trace_list)
    trace_bundle = load_delegation_trace(workspace_path)
    if trace_bundle:
        native = _merge_event_lists(native, list(trace_bundle.get("local_recoveries", [])), "reason")
    return native


def verification_events(trace: Iterable[Dict[str, Any]], workspace_path: str | None = None) -> List[Dict[str, Any]]:
    trace_list = list(trace)
    native = _native_verification_events(trace_list)
    trace_bundle = load_delegation_trace(workspace_path)
    if trace_bundle:
        verifications = list(trace_bundle.get("verifications", []))
        if verifications:
            native = _merge_event_lists(native, verifications, "reason")
        verification_step = trace_bundle.get("verification_step")
        if isinstance(verification_step, dict):
            native = _merge_event_lists(native, [verification_step], "reason")
    return native


def load_delegation_trace(workspace_path: str | None) -> Dict[str, Any]:
    if not workspace_path:
        return {}
    trace_path = Path(workspace_path) / "delegation_trace.json"
    if not trace_path.exists():
        return {}
    try:
        payload = jsonlib.loads(trace_path.read_text(encoding="utf-8"))
    except jsonlib.JSONDecodeError:
        return {}
    if isinstance(payload, dict):
        return payload
    if isinstance(payload, list):
        if all(isinstance(item, dict) for item in payload):
            return {"delegations": payload}
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


def _native_delegate_events(trace: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    structured = [
        {
            **dict(event),
            "__index__": event.get("__index__", index),
        }
        for index, event in enumerate(trace)
        if event.get("type") == "delegate"
    ]
    if structured:
        return structured

    tool_results = _sessions_spawn_tool_results(trace)
    parsed: List[Dict[str, Any]] = []
    for index, event in enumerate(trace):
        if event.get("type") != "message":
            continue
        message = event.get("message", {})
        if message.get("role") != "assistant":
            continue
        for item in _message_items(message):
            if item.get("type") != "toolCall" or item.get("name") != "sessions_spawn":
                continue
            args = item.get("arguments", {})
            tool_result = tool_results.get(str(item.get("id", "")), {})
            parsed.append(
                {
                    "type": "delegate",
                    "delegation_id": args.get("label") or args.get("task") or item.get("id"),
                    "assignee": args.get("agentId") or args.get("runtime") or args.get("label") or "subagent",
                    "instruction": args.get("task", ""),
                    "inputs": [args.get("cwd")] if args.get("cwd") else [],
                    "success_criteria": "Subagent completes the requested delegated work.",
                    "output_path": _extract_output_path(args.get("task", "")),
                    "runtime": args.get("runtime"),
                    "mode": args.get("mode"),
                    "child_session_key": tool_result.get("childSessionKey"),
                    "run_id": tool_result.get("runId"),
                    "status": tool_result.get("status"),
                    "__index__": index,
                }
            )
    return parsed


def _native_subagent_results(trace: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    structured = [
        {
            **dict(event),
            "__index__": event.get("__index__", index),
        }
        for index, event in enumerate(trace)
        if event.get("type") == "subagent_result"
    ]
    parsed = structured[:]
    for index, event in enumerate(trace):
        for internal_event in _iter_internal_task_completion_events(event):
            parsed.append(
                {
                    "type": "subagent_result",
                    "delegation_id": internal_event.get("taskLabel")
                    or internal_event.get("childSessionKey")
                    or internal_event.get("childSessionId")
                    or f"completion-{index}",
                    "status": _normalize_subagent_status(
                        internal_event.get("status"),
                        internal_event.get("statusLabel"),
                    ),
                    "summary": internal_event.get("result", ""),
                    "child_session_key": internal_event.get("childSessionKey"),
                    "child_session_id": internal_event.get("childSessionId"),
                    "announce_type": internal_event.get("announceType"),
                    "__index__": index,
                }
            )
    return _dedupe_results(parsed)


def _native_replan_events(trace: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    structured = [
        {
            **dict(event),
            "__index__": event.get("__index__", index),
        }
        for index, event in enumerate(trace)
        if event.get("type") == "replan"
    ]
    if structured:
        return structured

    delegations = delegate_events(trace)
    results = subagent_results(trace)
    replans: List[Dict[str, Any]] = []
    for result in results:
        if result.get("status") != "failed":
            continue
        result_index = int(result.get("__index__", -1))
        later_delegation = next(
            (
                event
                for event in delegations
                if int(event.get("__index__", -1)) > result_index
            ),
            None,
        )
        if later_delegation is not None:
            replans.append(
                {
                    "type": "replan",
                    "reason": "A failed subagent completion was followed by a new delegation.",
                    "failed_delegation_id": result.get("delegation_id"),
                    "recovery_mode": "delegate",
                    "recovery_delegation_id": later_delegation.get("delegation_id"),
                    "__index__": later_delegation.get("__index__", result_index),
                }
            )
            continue

        local_recovery = _first_local_recovery_after_failure(trace, result_index)
        if local_recovery is None:
            continue
        replans.append(
            {
                "type": "replan",
                "reason": "A failed subagent completion was followed by a local recovery path in the main session.",
                "failed_delegation_id": result.get("delegation_id"),
                "recovery_mode": "local",
                "source": local_recovery.get("source", "local"),
                "__index__": local_recovery.get("__index__", result_index),
            }
        )
    return replans


def _native_local_recovery_events(trace: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    results = subagent_results(trace)
    recoveries: List[Dict[str, Any]] = []
    for result in results:
        if result.get("status") != "failed":
            continue
        result_index = int(result.get("__index__", -1))
        recovery = _first_local_recovery_after_failure(trace, result_index)
        if recovery is None:
            continue
        recoveries.append(
            {
                "type": "local_recovery",
                "reason": "A failed delegated step was followed by local main-session execution.",
                "failed_delegation_id": result.get("delegation_id"),
                "source": recovery.get("source", "local"),
                "__index__": recovery.get("__index__", result_index),
            }
        )
    return recoveries


def _native_verification_events(trace: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    structured = [
        {
            **dict(event),
            "__index__": event.get("__index__", index),
        }
        for index, event in enumerate(trace)
        if event.get("type") == "verification"
    ]
    if structured:
        return structured

    results = subagent_results(trace)
    if len(results) < 2:
        return []

    result_texts = [
        str(result.get("summary", "")).strip().lower()
        for result in results
        if str(result.get("summary", "")).strip()
    ]
    if len(set(result_texts)) < 2:
        return []

    last_result_index = max(int(result.get("__index__", -1)) for result in results)
    for index, event in enumerate(trace):
        if index <= last_result_index:
            continue
        if event.get("type") == "tool_use":
            return [
                {
                    "type": "verification",
                    "source": event.get("tool", "tool"),
                    "reason": "A follow-up tool call ran after conflicting subagent results.",
                    "__index__": index,
                }
            ]
        if event.get("type") != "message":
            continue
        message = event.get("message", {})
        if message.get("role") != "assistant":
            continue
        for item in _message_items(message):
            if item.get("type") != "toolCall":
                continue
            return [
                {
                    "type": "verification",
                    "source": item.get("name", "tool"),
                    "reason": "A follow-up tool call ran after conflicting subagent results.",
                    "__index__": index,
                }
            ]
    return []


def _sessions_spawn_tool_results(trace: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    indexed: Dict[str, Dict[str, Any]] = {}
    for event in trace:
        if event.get("type") != "message":
            continue
        message = event.get("message", {})
        if message.get("role") != "toolResult" or message.get("toolName") != "sessions_spawn":
            continue
        tool_call_id = str(message.get("toolCallId", "")).strip()
        if not tool_call_id:
            continue
        details = message.get("details", {})
        if isinstance(details, dict):
            indexed[tool_call_id] = details
    return indexed


def _first_local_recovery_after_failure(
    trace: List[Dict[str, Any]],
    failed_result_index: int,
) -> Dict[str, Any] | None:
    for index in range(failed_result_index + 1, len(trace)):
        event = trace[index]
        if event.get("session_source") == "child":
            continue
        if event.get("type") == "delegate":
            return None
        if event.get("type") == "tool_use":
            return {"source": event.get("tool", "tool"), "__index__": index}
        if event.get("type") == "artifact_written":
            return {"source": "artifact_written", "__index__": index}
        if event.get("type") != "message":
            continue
        message = event.get("message", {})
        if message.get("role") != "assistant":
            continue
        for item in _message_items(message):
            if item.get("type") != "toolCall":
                continue
            if item.get("name") == "sessions_spawn":
                return None
            return {"source": item.get("name", "tool"), "__index__": index}
    return None


def _message_items(message: Dict[str, Any]) -> List[Dict[str, Any]]:
    content = message.get("content", [])
    if isinstance(content, list):
        return [item for item in content if isinstance(item, dict)]
    return []


def _iter_internal_task_completion_events(event: Dict[str, Any]) -> List[Dict[str, Any]]:
    parsed: List[Dict[str, Any]] = []
    for candidate in _internal_events_from_event(event):
        if candidate.get("type") == "task_completion":
            parsed.append(candidate)
    if parsed:
        return parsed

    text = _event_text_content(event)
    if not text:
        return []

    blocks = re.findall(
        r"\[Internal task completion event\](.*?)(?=\n---\n|\Z)",
        text,
        flags=re.DOTALL,
    )
    parsed_blocks: List[Dict[str, Any]] = []
    for block in blocks:
        result_match = re.search(
            r"<<<BEGIN_UNTRUSTED_CHILD_RESULT>>>\n(.*?)\n<<<END_UNTRUSTED_CHILD_RESULT>>>",
            block,
            flags=re.DOTALL,
        )
        parsed_blocks.append(
            {
                "type": "task_completion",
                "childSessionKey": _extract_prefixed_line(block, "session_key:"),
                "childSessionId": _extract_prefixed_line(block, "session_id:"),
                "announceType": _extract_prefixed_line(block, "type:"),
                "taskLabel": _extract_prefixed_line(block, "task:"),
                "statusLabel": _extract_prefixed_line(block, "status:"),
                "status": _extract_prefixed_line(block, "status:"),
                "result": result_match.group(1).strip() if result_match else "",
            }
        )
    return parsed_blocks


def _internal_events_from_event(event: Dict[str, Any]) -> List[Dict[str, Any]]:
    candidates = []
    message = event.get("message", {})
    if isinstance(message, dict):
        candidates.append(message.get("internalEvents"))
    candidates.append(event.get("internalEvents"))

    parsed: List[Dict[str, Any]] = []
    for candidate in candidates:
        if not isinstance(candidate, list):
            continue
        for item in candidate:
            if isinstance(item, dict):
                parsed.append(item)
    return parsed


def _event_text_content(event: Dict[str, Any]) -> str:
    if event.get("type") != "message":
        return ""
    message = event.get("message", {})
    content = message.get("content", [])
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts: List[str] = []
    for item in content:
        if isinstance(item, str):
            parts.append(item)
            continue
        if not isinstance(item, dict):
            continue
        if item.get("type") == "text" and isinstance(item.get("text"), str):
            parts.append(item["text"])
    return "\n".join(part for part in parts if part.strip())


def _extract_prefixed_line(block: str, prefix: str) -> str:
    for line in block.splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return ""


def _normalize_subagent_status(status: Any, status_label: Any) -> str:
    raw = str(status or "").strip().lower()
    label = str(status_label or "").strip().lower()
    if raw in {"ok", "success"} or "completed successfully" in label:
        return "success"
    if raw in {"timeout", "error", "failed"} or "timed out" in label or "failed" in label:
        return "failed"
    return raw or "unknown"


def _merge_event_lists(
    primary: List[Dict[str, Any]],
    secondary: List[Dict[str, Any]],
    identity_key: str,
) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for event in [*primary, *secondary]:
        event_id = str(event.get(identity_key) or jsonlib.dumps(event, sort_keys=True, ensure_ascii=False))
        if event_id in seen:
            continue
        seen.add(event_id)
        merged.append(event)
    return merged


def _dedupe_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    deduped: List[Dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for result in results:
        key = (
            str(result.get("delegation_id", "")),
            str(result.get("status", "")),
            str(result.get("summary", "")),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(result)
    return deduped
