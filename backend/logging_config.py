"""
Structured JSON logging with per-request correlation ID.
Correction #14: JSON logs, redacting sensitive fields.
"""

import logging
import json
import re
import uuid
from contextvars import ContextVar

# Per-request correlation ID stored in a context variable.
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")

# Patterns for sensitive data redaction.
_SENSITIVE_PATTERNS = re.compile(
    r"(password|token|secret|api_key|GEMINI_API_KEY|authorization|hashed_password)",
    re.IGNORECASE,
)


class JsonFormatter(logging.Formatter):
    """Emit structured JSON log lines with correlation ID."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": correlation_id_var.get(""),
        }
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)
        # Redact sensitive values from the message
        log_entry["message"] = _redact(log_entry["message"])
        return json.dumps(log_entry, default=str)


def _redact(text: str) -> str:
    """Replace values adjacent to sensitive keys with '[REDACTED]'."""
    # Redact patterns like key=value or "key": "value"
    text = re.sub(
        r'("?(?:password|token|secret|api_key|GEMINI_API_KEY|authorization|hashed_password)"?\s*[:=]\s*)"?[^",}\s]+"?',
        r"\1[REDACTED]",
        text,
        flags=re.IGNORECASE,
    )
    return text


def new_correlation_id() -> str:
    """Generate and set a new correlation ID for the current request context."""
    cid = str(uuid.uuid4())[:8]
    correlation_id_var.set(cid)
    return cid


def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logger with JSON formatter."""
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)
    # Quieten noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger."""
    return logging.getLogger(name)
