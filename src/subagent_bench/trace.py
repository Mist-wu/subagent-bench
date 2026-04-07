from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

from subagent_bench.schema import validate_trace_bundle


def load_trace(trace_path: Path) -> Dict[str, Any]:
    raw = trace_path.read_text(encoding="utf-8").strip()
    if not raw:
        bundle = {"events": []}
        _ensure_valid(bundle, trace_path)
        return bundle

    if raw.startswith("{"):
        data = json.loads(raw)
        if isinstance(data, dict):
            data.setdefault("events", [])
            _ensure_valid(data, trace_path)
            return data

    bundle = {"events": [json.loads(line) for line in raw.splitlines() if line.strip()]}
    _ensure_valid(bundle, trace_path)
    return bundle


def events_of_type(events: Iterable[Dict[str, Any]], event_type: str) -> List[Dict[str, Any]]:
    return [event for event in events if event.get("type") == event_type]


def first_event_index(events: List[Dict[str, Any]], event_type: str, **fields: Any) -> int:
    for index, event in enumerate(events):
        if event.get("type") != event_type:
            continue
        if all(event.get(key) == value for key, value in fields.items()):
            return index
    return -1


def _ensure_valid(bundle: Dict[str, Any], trace_path: Path) -> None:
    errors = validate_trace_bundle(bundle)
    if errors:
        joined = "; ".join(errors)
        raise ValueError(f"Invalid trace {trace_path}: {joined}")
