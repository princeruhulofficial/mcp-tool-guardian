"""Sanitize tool outputs to reduce injection and secret leakage risk."""

from typing import Any, Dict, List, Union
import re
import json


# Simple patterns that often appear in poisoned or leaking tool responses
SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password|bearer)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),          # OpenAI style
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),         # GitHub PAT
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), # Slack
]

INJECTION_HINTS = [
    re.compile(r"(?i)ignore (previous|all) instructions"),
    re.compile(r"(?i)you are now"),
    re.compile(r"(?i)system prompt"),
    re.compile(r"(?i)<script"),
]


def _mask_secrets(text: str) -> str:
    for pat in SECRET_PATTERNS:
        text = pat.sub("[REDACTED_SECRET]", text)
    return text


def _clean_string(value: str) -> str:
    cleaned = _mask_secrets(value)
    # Remove control characters except common whitespace
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", cleaned)
    return cleaned


def sanitize_tool_output(
    data: Any,
    max_string_length: int = 4000,
    redact_secrets: bool = True,
) -> Dict[str, Any]:
    """
    Recursively clean a tool response.

    Returns:
        {
          "cleaned": ...,
          "redactions": number of secrets masked,
          "warnings": list of notes
        }
    """
    warnings: List[str] = []
    redaction_count = 0

    def _walk(obj: Any) -> Any:
        nonlocal redaction_count
        if isinstance(obj, str):
            original = obj
            cleaned = _clean_string(obj) if redact_secrets else obj
            if len(cleaned) > max_string_length:
                cleaned = cleaned[:max_string_length] + "...[TRUNCATED]"
                warnings.append("String truncated because it was too long")
            if cleaned != original:
                redaction_count += 1
            # Check injection-like content
            for pat in INJECTION_HINTS:
                if pat.search(cleaned):
                    warnings.append("Possible prompt-injection style text detected")
                    break
            return cleaned
        elif isinstance(obj, dict):
            return {str(k): _walk(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [_walk(item) for item in obj]
        elif isinstance(obj, (int, float, bool)) or obj is None:
            return obj
        else:
            # Fallback: turn unknown types into safe string
            warnings.append(f"Converted non-JSON-safe type {type(obj).__name__} to string")
            return str(obj)[:max_string_length]

    cleaned = _walk(data)

    return {
        "cleaned": cleaned,
        "redactions": redaction_count,
        "warnings": warnings,
        "safe_for_llm": len(warnings) == 0 and redaction_count == 0,
    }
