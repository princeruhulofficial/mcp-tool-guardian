"""Audit logging and simple suspicious-pattern detection."""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import re
import hashlib
import json


SUSPICIOUS_PATTERNS = [
    (re.compile(r"(?i)ignore (all|previous|above) (instructions|prompts)"), "prompt_injection"),
    (re.compile(r"(?i)you are (now|a) (DAN|jailbreak|unrestricted)"), "jailbreak_attempt"),
    (re.compile(r"(?i)exfiltrat|send (data|secrets) to"), "data_exfil_hint"),
    (re.compile(r"(?i)<script|javascript:|onerror="), "xss_style"),
    (re.compile(r"(?i)rm -rf|curl .*\| *sh|wget .*\| *bash"), "shell_injection"),
]


def detect_suspicious_patterns(
    text_or_data: Any,
) -> Dict[str, Any]:
    """
    Scan a tool description or output for common poisoning patterns.
    Pure local regex – no external calls.
    """
    if isinstance(text_or_data, (dict, list)):
        try:
            text = json.dumps(text_or_data, default=str)
        except Exception:
            text = str(text_or_data)
    else:
        text = str(text_or_data)

    findings: List[Dict[str, str]] = []
    for pattern, label in SUSPICIOUS_PATTERNS:
        if pattern.search(text):
            findings.append({
                "type": label,
                "snippet": pattern.search(text).group(0)[:80],
            })

    return {
        "suspicious": len(findings) > 0,
        "count": len(findings),
        "findings": findings,
        "recommendation": (
            "High caution – possible tool poisoning or injection"
            if findings else
            "No obvious suspicious patterns found"
        ),
    }


def create_audit_entry(
    action: str,
    tool_name: Optional[str] = None,
    result_summary: Optional[str] = None,
    reliability_score: Optional[int] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a simple, structured audit log entry.
    In a real deployment this would be written to a durable store.
    For this MCP we return the entry so the agent (or host) can persist it.
    """
    entry = {
        "id": hashlib.sha256(
            f"{action}{tool_name}{datetime.now(timezone.utc).isoformat()}".encode()
        ).hexdigest()[:16],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "tool_name": tool_name,
        "result_summary": (result_summary or "")[:500],
        "reliability_score": reliability_score,
        "extra": extra or {},
        "source": "mcp-tool-guardian",
    }
    return {
        "audit_entry": entry,
        "message": "Audit entry created. Persist this in your logging system for accountability.",
    }
