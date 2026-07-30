"""Common JSON schemas and helpers used by Tool Guardian."""

from typing import Any, Dict

# Example schema that agents can reuse for common tool responses
COMMON_SUCCESS_SCHEMA = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "data": {},
        "error": {"type": ["string", "null"]},
        "timestamp": {"type": "string"},
    },
    "required": ["success"],
}

def is_json_serializable(obj: Any) -> bool:
    """Quick check whether an object can be safely turned into JSON."""
    try:
        import json
        json.dumps(obj)
        return True
    except (TypeError, ValueError, OverflowError):
        return False
