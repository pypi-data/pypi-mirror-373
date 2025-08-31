import logging
from typing import Any

from requests import Response

LOG = logging.getLogger(__name__)


def _truncate(text: str) -> str:
    """Truncate a string to 1024 chars."""
    if len(text) > 1024:
        return f"{text[:1024]}...({len(text) - 1024} truncated)"
    else:
        return text


def log_responses(response: Response, **kwargs: Any) -> Response:
    """A requests hook that logs errors."""
    if response.status_code >= 400:
        try:
            response_text = _truncate(response.text)
        except Exception:
            response_text = "N/A"
        LOG.warning(
            "[%s] %s: %s",
            response.status_code,
            response.url,
            response_text,
            extra={
                "headers": dict(response.headers),
                "url": response.url,
                "status_code": response.status_code,
            },
        )
    return response
