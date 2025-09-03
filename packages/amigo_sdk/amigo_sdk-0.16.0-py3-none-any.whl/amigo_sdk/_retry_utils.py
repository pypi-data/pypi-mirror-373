import datetime as dt
import random
from email.utils import parsedate_to_datetime
from typing import Optional

DEFAULT_RETRYABLE_STATUS: set[int] = {429, 500, 502, 503, 504}


def parse_retry_after_seconds(retry_after: Optional[str]) -> float | None:
    """Parse Retry-After header into seconds.

    Supports both numeric seconds and HTTP-date formats. Returns None when
    header is missing or invalid.
    """
    if not retry_after:
        return None
    # Numeric seconds
    try:
        seconds = float(retry_after)
        return max(0.0, seconds)
    except Exception:
        pass
    # HTTP-date format
    try:
        target_dt = parsedate_to_datetime(retry_after)
        if target_dt is None:
            return None
        if target_dt.tzinfo is None:
            target_dt = target_dt.replace(tzinfo=dt.UTC)
        now = dt.datetime.now(dt.UTC)
        delta_seconds = (target_dt - now).total_seconds()
        return max(0.0, delta_seconds)
    except Exception:
        return None


def is_retryable_response(
    method: str,
    status_code: int,
    headers: dict,
    retry_on_methods: set[str],
    retry_on_status: set[int],
) -> bool:
    """Determine if the response is retryable under our policy.

    Special case: allow POST retry only on 429 when Retry-After is present.
    """
    method_upper = method.upper()
    if method_upper == "POST" and status_code == 429 and headers.get("Retry-After"):
        return True
    return method_upper in retry_on_methods and status_code in retry_on_status


def compute_retry_delay_seconds(
    attempt: int,
    backoff_base: float,
    max_delay_seconds: float,
    retry_after_header: Optional[str],
) -> float:
    """Compute delay for a given retry attempt.

    If Retry-After is present, honor it (clamped by max). Otherwise, use
    exponential backoff with full jitter.
    """
    ra_seconds = parse_retry_after_seconds(retry_after_header)
    if ra_seconds is not None:
        return min(max_delay_seconds, ra_seconds)
    window = backoff_base * (2 ** (attempt - 1))
    window = min(window, max_delay_seconds)
    return random.uniform(0.0, window)
