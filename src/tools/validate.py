"""Schema validation tool – pure local computation."""

from typing import Any, Dict, List, Optional
import jsonschema
from jsonschema import ValidationError


def validate_against_schema(
    data: Any,
    schema: Dict[str, Any],
    strict: bool = True,
) -> Dict[str, Any]:
    """
    Validate any data against a JSON Schema.

    Returns a clear report that an AI agent can understand.
    """
    result = {
        "valid": False,
        "errors": [],
        "message": "",
        "data_type": type(data).__name__,
    }

    if not isinstance(schema, dict):
        result["message"] = "Schema must be a JSON object (dict)."
        result["errors"].append("Invalid schema type")
        return result

    try:
        # Draft 2020-12 is modern; fall back gracefully
        validator_cls = jsonschema.Draft202012Validator
        validator = validator_cls(schema)
        errors: List[str] = []

        for error in sorted(validator.iter_errors(data), key=lambda e: e.path):
            path = ".".join(str(p) for p in error.path) or "(root)"
            errors.append(f"{path}: {error.message}")

        if errors:
            result["valid"] = False
            result["errors"] = errors
            result["message"] = f"Found {len(errors)} validation error(s)."
        else:
            result["valid"] = True
            result["message"] = "Data matches the schema perfectly."
            result["errors"] = []

    except Exception as e:
        result["valid"] = False
        result["errors"] = [str(e)]
        result["message"] = f"Validation failed with unexpected error: {e}"

    return result
