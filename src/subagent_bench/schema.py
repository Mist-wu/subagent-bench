from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple


REQUIRED_FIELDS_BY_EVENT = {
    "delegate": ["delegation_id", "assignee", "instruction", "inputs", "success_criteria", "output_path"],
    "subagent_result": ["delegation_id", "status"],
    "replan": ["reason"],
    "verification": ["source", "reason"],
    "artifact_written": ["path"],
    "assistant_message": ["agent", "content"],
}


def validate_trace_bundle(bundle: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    events = bundle.get("events")
    if not isinstance(events, list):
        return ["Trace bundle must contain an 'events' list."]

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            errors.append(f"Event {index} is not an object.")
            continue
        event_type = event.get("type")
        if not isinstance(event_type, str) or not event_type:
            errors.append(f"Event {index} is missing a string 'type'.")
            continue
        for field in REQUIRED_FIELDS_BY_EVENT.get(event_type, []):
            if field not in event:
                errors.append(f"Event {index} ({event_type}) is missing '{field}'.")

    judge_result = bundle.get("judge_result")
    if judge_result is not None:
        if not isinstance(judge_result, dict):
            errors.append("judge_result must be an object when present.")
        elif "score" not in judge_result:
            errors.append("judge_result must contain 'score'.")

    return errors


def summarize_trace_types(events: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for event in events:
        event_type = str(event.get("type", "unknown"))
        counts[event_type] = counts.get(event_type, 0) + 1
    return counts
