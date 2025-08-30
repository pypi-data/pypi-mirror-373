"""
HTTP logging utilities for ClickUp client.

Provides toggleable request/response logging via httpx event hooks.
Writes JSON lines to a configurable file with header redaction and body size caps.

Configuration (env vars):
- CLICKUP_HTTP_LOG: "1" to enable, otherwise disabled
- CLICKUP_HTTP_LOG_FILE: output path (default: toolkits/clickup/logs/http.jsonl)
- CLICKUP_HTTP_LOG_MAX_BODY: max bytes to record from bodies (default: 2048)
- CLICKUP_HTTP_LOG_REDACT: comma-separated header names to redact
"""

from __future__ import annotations

import contextlib
import json
import logging
import os
import time
from collections.abc import Callable
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

import httpx

# Default log file lives alongside this module, avoiding CWD-dependent paths
_DEFAULT_LOG_PATH = Path(__file__).resolve().parent / "http.jsonl"
_DEFAULT_MAX_BODY = 2048
_DEFAULT_REDACT = {
    "authorization",
    "set-cookie",
    "cookie",
    "x-api-key",
    "proxy-authorization",
}

_logger: logging.Logger | None = None


def _ensure_logger() -> logging.Logger:
    """Initialize and return the module logger.

    Creates a rotating file logger that writes one JSON record per line to the
    path specified by CLICKUP_HTTP_LOG_FILE (or the default path).

    Returns:
        logging.Logger: Configured logger instance for HTTP logging.
    """
    global _logger
    if _logger is not None:
        return _logger

    log_path = Path(os.getenv("CLICKUP_HTTP_LOG_FILE", str(_DEFAULT_LOG_PATH)))
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("arcade_clickup.http")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=3)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
    _logger = logger
    return logger


def _should_log() -> bool:
    """Determine if HTTP logging is enabled.

    Reads CLICKUP_HTTP_LOG from the environment and treats "1", "true", or
    "True" as enabled.

    Returns:
        bool: True if logging is enabled, otherwise False.
    """
    return os.getenv("CLICKUP_HTTP_LOG", "0") in {"1", "true", "True"}


def _max_body_bytes() -> int:
    """Get the maximum number of bytes to record from request/response bodies.

    Controlled by CLICKUP_HTTP_LOG_MAX_BODY; falls back to a safe default on
    invalid values.

    Returns:
        int: Maximum number of bytes to capture.
    """
    try:
        return int(os.getenv("CLICKUP_HTTP_LOG_MAX_BODY", str(_DEFAULT_MAX_BODY)))
    except Exception:
        return _DEFAULT_MAX_BODY


def _redaction_set() -> set[str]:
    """Build the set of lowercase header names to redact.

    Controlled by CLICKUP_HTTP_LOG_REDACT; if unset, uses a safe default set.

    Returns:
        set[str]: Header names to redact (lowercase).
    """
    raw = os.getenv("CLICKUP_HTTP_LOG_REDACT")
    if not raw:
        return set(_DEFAULT_REDACT)
    return {h.strip().lower() for h in raw.split(",") if h.strip()}


def _redact_headers(headers: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of headers with sensitive fields redacted.

    Args:
        headers: Mapping of header names to values.

    Returns:
        Dict[str, Any]: New headers dictionary with sensitive fields replaced
        by "<redacted>".
    """
    redact = _redaction_set()
    redacted: dict[str, Any] = {}
    for k, v in headers.items():
        if k.lower() in redact:
            redacted[k] = "<redacted>"
        else:
            redacted[k] = v
    return redacted


def _truncate_body(body: bytes | None) -> str | None:
    """Return a UTF-8 preview of a body capped to the configured size.

    Args:
        body: Raw body bytes or None.

    Returns:
        str | None: Text preview with an ellipsis note if truncated, or None
        if there was no body.
    """
    if body is None:
        return None
    limit = _max_body_bytes()
    data = body[:limit]
    try:
        text = data.decode("utf-8", errors="replace")
    except Exception:
        text = "<binary>"
    if len(body) > limit:
        return text + f"\n<…truncated {len(body) - limit} bytes>"
    return text


def _log_json(record: dict[str, Any]) -> None:
    """Write one JSONL record.

    Args:
        record: Arbitrary JSON-serializable data to log as a single line.
    """
    with contextlib.suppress(Exception):
        _ensure_logger().info(json.dumps(record, ensure_ascii=False))


def get_http_event_hooks_if_enabled() -> dict[str, list[Callable]] | None:
    """Return httpx event hooks for request/response logging if enabled.

    When CLICKUP_HTTP_LOG is enabled, returns a dict with "request" and
    "response" hook callables. Otherwise returns None.

    Returns:
        dict[str, list[Callable]] | None: Event hooks for httpx or None if
        logging is disabled.
    """
    if not _should_log():
        return None

    async def on_request(request: httpx.Request) -> None:
        body_bytes = request.content if isinstance(request.content, bytes | bytearray) else None
        _log_json({
            "ts": time.time(),
            "type": "request",
            "method": request.method,
            "url": str(request.url),
            "headers": _redact_headers(dict(request.headers)),
            "body_preview": _truncate_body(body_bytes),
        })

    async def on_response(response: httpx.Response) -> None:
        with contextlib.suppress(Exception):
            await response.aread()
        body_bytes = response.content
        elapsed_ms = None
        try:
            if response.elapsed is not None:
                elapsed_ms = int(response.elapsed.total_seconds() * 1000)
        except Exception:
            elapsed_ms = None
        _log_json({
            "ts": time.time(),
            "type": "response",
            "method": response.request.method if response.request else None,
            "url": str(response.request.url) if response.request else None,
            "status": response.status_code,
            "elapsed_ms": elapsed_ms,
            "headers": _redact_headers(dict(response.headers)),
            "body_preview": _truncate_body(body_bytes),
        })

    return {"request": [on_request], "response": [on_response]}
