"""Shared test helpers for resource tests."""

from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

from amigo_sdk.generated.model import (
    OrganizationGetOrganizationResponse,
    ServiceGetServicesResponse,
    ServiceInstance,
)


@asynccontextmanager
async def mock_http_request(mock_response_data, status_code=200):
    """
    Context manager that mocks HTTP requests with auth token handling.

    Args:
        mock_response_data: The data to return in the response (can be JSON string or Pydantic object)
        status_code: HTTP status code to return (default: 200)
    """
    # Create mock response
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.is_success = status_code < 400

    # Convert payload to JSON string for response.text
    if hasattr(mock_response_data, "model_dump_json"):
        mock_response.text = mock_response_data.model_dump_json()
    elif isinstance(mock_response_data, str):
        mock_response.text = mock_response_data
    else:
        import json as _json

        mock_response.text = _json.dumps(mock_response_data)

    # Create fresh auth token
    fresh_token = Mock(
        id_token="test-bearer-token",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    with (
        patch(
            "amigo_sdk.http_client.sign_in_with_api_key_async", return_value=fresh_token
        ),
        patch("httpx.AsyncClient.request", return_value=mock_response),
    ):
        yield mock_response


@asynccontextmanager
async def mock_http_stream(lines, status_code: int = 200):
    """Mock httpx.AsyncClient.stream for NDJSON endpoints.

    lines: list of dicts or JSON strings that will be yielded line-by-line.
    status_code: HTTP status code to expose on the stream response.
    """
    # Normalize to JSON strings
    json_lines = []
    for item in lines:
        if hasattr(item, "model_dump_json"):
            json_lines.append(item.model_dump_json())
        elif isinstance(item, str):
            json_lines.append(item)
        else:
            import json as _json

            json_lines.append(_json.dumps(item))

    class _MockStreamResponse:
        def __init__(self, status_code: int, lines: list[str]):
            self.status_code = status_code
            self._lines = lines

        async def aiter_lines(self):
            for ln in self._lines:
                yield ln

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    # Track last call data for assertions
    tracker = {"last_call": None}

    def _mock_stream(self, method, url, **kwargs):  # noqa: ANN001
        tracker["last_call"] = {"method": method, "url": url, **kwargs}
        return _MockStreamResponse(status_code, json_lines)

    # Create fresh auth token
    fresh_token = Mock(
        id_token="test-bearer-token",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    with (
        patch(
            "amigo_sdk.http_client.sign_in_with_api_key_async", return_value=fresh_token
        ),
        patch("httpx.AsyncClient.stream", _mock_stream),
    ):
        yield tracker


@asynccontextmanager
async def mock_http_stream_sequence(sequence):
    """Mock httpx.AsyncClient.stream for a sequence of responses.

    sequence: list of tuples (status_code: int, lines: list[str|dict|pydantic]).
    Yields a tracker dict with 'last_call' and 'call_count'.
    """

    def _normalize_lines(items):
        out = []
        for item in items:
            if hasattr(item, "model_dump_json"):
                out.append(item.model_dump_json())
            elif isinstance(item, str):
                out.append(item)
            else:
                import json as _json

                out.append(_json.dumps(item))
        return out

    class _MockStreamResponse:
        def __init__(self, status_code: int, lines: list[str]):
            self.status_code = status_code
            self._lines = lines

        async def aiter_lines(self):
            for ln in self._lines:
                yield ln

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    idx = {"i": 0}
    tracker = {"last_call": None, "call_count": 0}

    def _mock_stream(self, method, url, **kwargs):  # noqa: ANN001
        tracker["last_call"] = {"method": method, "url": url, **kwargs}
        tracker["call_count"] += 1
        i = idx["i"]
        if i >= len(sequence):
            i = len(sequence) - 1
        status_code, lines = sequence[i]
        idx["i"] += 1
        return _MockStreamResponse(status_code, _normalize_lines(lines))

    fresh_token = Mock(
        id_token="test-bearer-token",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    with (
        patch(
            "amigo_sdk.http_client.sign_in_with_api_key_async", return_value=fresh_token
        ),
        patch("httpx.AsyncClient.stream", _mock_stream),
    ):
        yield tracker


# ------------------------- Sync helpers ---------------------------------------


@contextmanager
def mock_http_request_sync(mock_response_data, status_code=200):
    """Mock httpx.Client.request for sync flows and token acquisition.

    Returns a context manager yielding the mock response object.
    """
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.is_success = status_code < 400

    if hasattr(mock_response_data, "model_dump_json"):
        mock_response.text = mock_response_data.model_dump_json()
    elif isinstance(mock_response_data, str):
        mock_response.text = mock_response_data
    else:
        import json as _json

        mock_response.text = _json.dumps(mock_response_data)

    fresh_token = Mock(
        id_token="test-bearer-token",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    with (
        patch("amigo_sdk.http_client.sign_in_with_api_key", return_value=fresh_token),
        patch("httpx.Client.request", return_value=mock_response),
    ):
        yield mock_response


@contextmanager
def mock_http_stream_sync(lines, status_code: int = 200):
    """Mock httpx.Client.stream for NDJSON sync endpoints.

    lines: list of dicts or JSON strings yielded line-by-line by iter_lines().
    Returns a tracker dict capturing call details.
    """
    json_lines = []
    for item in lines:
        if hasattr(item, "model_dump_json"):
            json_lines.append(item.model_dump_json())
        elif isinstance(item, str):
            json_lines.append(item)
        else:
            import json as _json

            json_lines.append(_json.dumps(item))

    class _MockStreamResponse:
        def __init__(self, status_code: int, lines: list[str]):
            self.status_code = status_code
            self._lines = lines

        def iter_lines(self):
            yield from self._lines

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    tracker = {"last_call": None}

    def _mock_stream(self, method, url, **kwargs):  # noqa: ANN001
        tracker["last_call"] = {"method": method, "url": url, **kwargs}
        return _MockStreamResponse(status_code, json_lines)

    fresh_token = Mock(
        id_token="test-bearer-token",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    with (
        patch("amigo_sdk.http_client.sign_in_with_api_key", return_value=fresh_token),
        patch("httpx.Client.stream", _mock_stream),
    ):
        yield tracker


@contextmanager
def mock_http_stream_sequence_sync(sequence):
    """Mock httpx.Client.stream for a sequence of responses (sync).

    sequence: list of tuples (status_code: int, lines: list[str|dict|pydantic]).
    Yields a tracker dict with 'last_call' and 'call_count'.
    """

    def _normalize_lines(items):
        out = []
        for item in items:
            if hasattr(item, "model_dump_json"):
                out.append(item.model_dump_json())
            elif isinstance(item, str):
                out.append(item)
            else:
                import json as _json

                out.append(_json.dumps(item))
        return out

    class _MockStreamResponse:
        def __init__(self, status_code: int, lines: list[str]):
            self.status_code = status_code
            self._lines = lines

        def iter_lines(self):
            yield from self._lines

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    idx = {"i": 0}
    tracker = {"last_call": None, "call_count": 0}

    def _mock_stream(self, method, url, **kwargs):  # noqa: ANN001
        tracker["last_call"] = {"method": method, "url": url, **kwargs}
        tracker["call_count"] += 1
        i = idx["i"]
        if i >= len(sequence):
            i = len(sequence) - 1
        status_code, lines = sequence[i]
        idx["i"] += 1
        return _MockStreamResponse(status_code, _normalize_lines(lines))

    fresh_token = Mock(
        id_token="test-bearer-token",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    with (
        patch("amigo_sdk.http_client.sign_in_with_api_key", return_value=fresh_token),
        patch("httpx.Client.stream", _mock_stream),
    ):
        yield tracker


def create_organization_response_data() -> OrganizationGetOrganizationResponse:
    """Create mock data matching OrganizationGetOrganizationResponse schema."""
    return OrganizationGetOrganizationResponse(
        org_id="test-org-123",
        org_name="Test Organization",
        title="Your AI Assistant Platform",
        main_description="Build and deploy AI assistants for your organization",
        sub_description="Streamline workflows with intelligent automation",
        onboarding_instructions=[
            "Welcome to our platform!",
            "Let's get you started with your first assistant.",
        ],
        default_user_preferences=None,
    )


def create_services_response_data() -> ServiceGetServicesResponse:
    """Create mock data matching ServiceGetServicesResponse schema."""
    return ServiceGetServicesResponse(
        services=[
            ServiceInstance(
                id="service-1",
                name="Customer Support Bot",
                description="AI assistant for customer inquiries",
                version_sets={},
                is_active=True,
                service_hierarchical_state_machine_id="hsm-1",
                agent_id="agent-1",
                tags=[
                    {"key": "support", "value": "customer-support"},
                    {"key": "customer", "value": "external"},
                ],
            ),
            ServiceInstance(
                id="service-2",
                name="Sales Assistant",
                description="AI assistant for sales support",
                version_sets={},
                is_active=True,
                service_hierarchical_state_machine_id="hsm-2",
                agent_id="agent-2",
                tags=[{"key": "sales", "value": "internal"}],
            ),
        ],
        has_more=False,
        continuation_token=None,
        filter_values=None,
    )
