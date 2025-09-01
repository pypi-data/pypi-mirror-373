import re
from typing import Any

DEFAULT_PATTERNS = [
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # US SSN (example)
]


def redact(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    redacted = value
    for pat in DEFAULT_PATTERNS:
        redacted = pat.sub("[REDACTED]", redacted)
    return redacted
