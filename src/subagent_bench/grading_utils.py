from __future__ import annotations

import re
from typing import Any, Mapping


def extract_python_code(section: str) -> str:
    match = re.search(r"```python\s*(.*?)```", section, re.DOTALL)
    if match:
        return match.group(1).strip()
    return section.strip()


def normalize_numeric_scores(
    scores: Mapping[str, Any],
    *,
    skip_prefixes: tuple[str, ...] = (),
) -> dict[str, float]:
    normalized: dict[str, float] = {}
    for key, value in scores.items():
        key_str = str(key)
        if skip_prefixes and any(key_str.startswith(prefix) for prefix in skip_prefixes):
            continue
        try:
            normalized[key_str] = float(value)
        except (TypeError, ValueError):
            continue
    return normalized


def weighted_average(
    scores: Mapping[str, Any],
    weights: Mapping[str, float] | None = None,
    *,
    skip_prefixes: tuple[str, ...] = ("__",),
) -> float:
    numeric_scores = normalize_numeric_scores(scores, skip_prefixes=skip_prefixes)
    if not numeric_scores:
        return 0.0

    if not weights:
        return sum(numeric_scores.values()) / len(numeric_scores)

    total_weight = 0.0
    weighted_sum = 0.0
    for key, value in numeric_scores.items():
        weight = float(weights.get(key, 1.0))
        if weight <= 0:
            continue
        total_weight += weight
        weighted_sum += value * weight
    if total_weight <= 0:
        return sum(numeric_scores.values()) / len(numeric_scores)
    return weighted_sum / total_weight
