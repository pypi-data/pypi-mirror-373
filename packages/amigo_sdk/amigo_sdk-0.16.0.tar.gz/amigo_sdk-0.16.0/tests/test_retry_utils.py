import datetime as dt
import random
from email.utils import format_datetime

import pytest

from amigo_sdk._retry_utils import (
    DEFAULT_RETRYABLE_STATUS,
    compute_retry_delay_seconds,
    is_retryable_response,
    parse_retry_after_seconds,
)


@pytest.mark.unit
class TestRetryUtils:
    def test_parse_retry_after_seconds_numeric(self):
        assert parse_retry_after_seconds("1.5") == pytest.approx(1.5, rel=1e-3)

    def test_parse_retry_after_seconds_http_date(self):
        future_dt = dt.datetime.now(dt.UTC) + dt.timedelta(seconds=2)
        http_date = format_datetime(future_dt)
        sec = parse_retry_after_seconds(http_date)
        assert sec is not None and sec >= 0

    def test_parse_retry_after_seconds_none_and_empty(self):
        assert parse_retry_after_seconds(None) is None
        assert parse_retry_after_seconds("") is None

    def test_parse_retry_after_seconds_invalid(self):
        assert parse_retry_after_seconds("not-a-date") is None

    def test_parse_retry_after_seconds_negative_numeric_clamped(self):
        assert parse_retry_after_seconds("-10") == 0.0

    def test_parse_retry_after_seconds_http_date_past_clamped(self):
        past_dt = dt.datetime.now(dt.UTC) - dt.timedelta(seconds=5)
        http_date = format_datetime(past_dt)
        assert parse_retry_after_seconds(http_date) == 0.0

    def test_parse_retry_after_seconds_http_date_without_tz(self):
        # Construct RFC 2822 date string without timezone to exercise tzinfo None path
        future_naive = dt.datetime.utcnow() + dt.timedelta(seconds=2)
        http_date = future_naive.strftime("%a, %d %b %Y %H:%M:%S")
        sec = parse_retry_after_seconds(http_date)
        assert sec is not None and sec >= 0

    def test_is_retryable_response_policy_get_and_post_429_with_header(self):
        methods = {"GET"}
        statuses = DEFAULT_RETRYABLE_STATUS
        assert is_retryable_response("GET", 500, {}, methods, statuses) is True
        assert (
            is_retryable_response("POST", 429, {"Retry-After": "1"}, methods, statuses)
            is True
        )
        assert is_retryable_response("POST", 429, {}, methods, statuses) is False

    def test_compute_retry_delay_honors_retry_after_and_clamps(self):
        d = compute_retry_delay_seconds(1, 0.25, 0.5, "5.0")
        assert d == 0.5

    def test_is_retryable_response_case_insensitive_and_exclusions(self):
        methods = {"GET"}
        statuses = DEFAULT_RETRYABLE_STATUS
        assert is_retryable_response("get", 500, {}, methods, statuses) is True
        assert (
            is_retryable_response("POST", 500, {"Retry-After": "1"}, methods, statuses)
            is False
        )
        assert is_retryable_response("GET", 418, {}, methods, statuses) is False

    def test_compute_retry_delay_jitter_window_and_clamp(self, monkeypatch):
        # Patch random.uniform to return the upper bound for determinism
        monkeypatch.setattr(random, "uniform", lambda a, b: b)
        # attempt 1 -> window = 0.25
        d1 = compute_retry_delay_seconds(1, 0.25, 10.0, None)
        assert d1 == pytest.approx(0.25, rel=1e-6)
        # attempt 3 -> raw window = 1.0, clamped to max 0.5
        d2 = compute_retry_delay_seconds(3, 0.25, 0.5, None)
        assert d2 == pytest.approx(0.5, rel=1e-6)

    def test_compute_retry_delay_retry_after_edge_cases_zero(self):
        assert compute_retry_delay_seconds(1, 0.25, 10.0, "-3") == 0.0
        past_dt = dt.datetime.now(dt.UTC) - dt.timedelta(seconds=10)
        http_date = format_datetime(past_dt)
        assert compute_retry_delay_seconds(1, 0.25, 10.0, http_date) == 0.0
