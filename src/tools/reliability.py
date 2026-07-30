"""Heuristic reliability scoring for tool responses."""

from typing import Any, Dict, List, Optional
import json


def score_reliability(
    data: Any,
    expected_keys: Optional[List[str]] = None,
    expected_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Give a 0-100 reliability score based on simple, fast heuristics.

    Factors considered:
    - Presence of expected keys
    - Type consistency
    - Not empty / not just error
    - JSON serializable
    - Reasonable size
    """
    score = 100
    reasons: List[str] = []

    # 1. Must be serializable
    try:
        serialized = json.dumps(data, default=str)
        size = len(serialized)
    except Exception:
        return {
            "score": 0,
            "level": "unusable",
            "reasons": ["Data is not JSON serializable"],
            "recommendation": "Do not trust this tool output",
        }

    # 2. Size sanity
    if size > 100_000:
        score -= 30
        reasons.append("Response is very large (>100KB) – may overwhelm context")
    elif size < 5:
        score -= 40
        reasons.append("Response is almost empty")

    # 3. Expected type
    type_name = type(data).__name__
    if expected_type:
        if expected_type == "object" and not isinstance(data, dict):
            score -= 35
            reasons.append(f"Expected object but got {type_name}")
        elif expected_type == "array" and not isinstance(data, list):
            score -= 35
            reasons.append(f"Expected array but got {type_name}")
        elif expected_type == "string" and not isinstance(data, str):
            score -= 25
            reasons.append(f"Expected string but got {type_name}")

    # 4. Expected keys (for objects)
    if expected_keys and isinstance(data, dict):
        missing = [k for k in expected_keys if k not in data]
        if missing:
            penalty = min(40, 10 * len(missing))
            score -= penalty
            reasons.append(f"Missing expected keys: {missing}")

    # 5. Error-looking content
    if isinstance(data, dict):
        if data.get("error") or data.get("success") is False:
            score -= 20
            reasons.append("Response indicates an error or success=false")
        if "traceback" in str(data).lower() or "exception" in str(data).lower():
            score -= 25
            reasons.append("Looks like an exception traceback leaked")

    # Clamp
    score = max(0, min(100, score))

    if score >= 85:
        level = "high"
        recommendation = "Safe to use in reasoning"
    elif score >= 60:
        level = "medium"
        recommendation = "Use with caution – double-check critical fields"
    elif score >= 30:
        level = "low"
        recommendation = "Prefer to re-call the tool or ask for clarification"
    else:
        level = "unusable"
        recommendation = "Do not trust this output – treat as failed tool call"

    return {
        "score": score,
        "level": level,
        "reasons": reasons,
        "recommendation": recommendation,
        "size_bytes": size,
        "type": type_name,
    }
