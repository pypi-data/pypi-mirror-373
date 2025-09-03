from typing import Any, Optional


class AmigoError(Exception):
    """
    Base class for Amigo API errors.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        response_body: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.response_body = response_body

    def __str__(self) -> str:
        parts = [super().__str__()]
        if self.status_code:
            parts.append(f"(HTTP {self.status_code})")
        if self.error_code:
            parts.append(f"[{self.error_code}]")
        return " ".join(parts)


# ---- 4xx client errors ------------------------------------------------------
class BadRequestError(AmigoError):  # 400
    pass


class AuthenticationError(AmigoError):  # 401
    pass


class PermissionError(AmigoError):  # 403
    pass


class NotFoundError(AmigoError):  # 404
    pass


class ConflictError(AmigoError):  # 409
    pass


class RateLimitError(AmigoError):  # 429
    pass


# ---- Validation / semantic errors ------------------------------------------
class ValidationError(BadRequestError):  # 422 or 400 with `errors` list
    def __init__(self, *args, field_errors: Optional[dict[str, str]] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_errors = field_errors or {}


# ---- 5xx server errors ------------------------------------------------------
class ServerError(AmigoError):  # 500
    pass


class ServiceUnavailableError(ServerError):  # 503 / maintenance
    pass


# ---- Internal SDK issues ----------------------------------------------------
class SDKInternalError(AmigoError):
    """JSON decoding failure, Pydantic model mismatch, etc."""


# ---- Status code mapping ----------------------------------------------------
def get_error_class_for_status_code(status_code: int) -> type[AmigoError]:
    """Map HTTP status codes to appropriate AmigoError classes."""
    error_map = {
        400: BadRequestError,
        401: AuthenticationError,
        403: PermissionError,
        404: NotFoundError,
        409: ConflictError,
        422: ValidationError,
        429: RateLimitError,
        500: ServerError,
        503: ServiceUnavailableError,
    }

    # Default to appropriate base class for status code ranges
    if status_code in error_map:
        return error_map[status_code]
    elif 400 <= status_code < 500:
        return BadRequestError
    elif 500 <= status_code < 600:
        return ServerError
    else:
        return AmigoError


def raise_for_status(response, message: str = None) -> None:
    """
    Raise an appropriate AmigoError for non-2xx status codes.

    Args:
        response: httpx.Response object
        message: Optional custom error message
    """
    if response.is_success:
        return

    status_code = response.status_code
    error_class = get_error_class_for_status_code(status_code)

    # Try to extract error details from response
    error_code = None
    response_body = None

    try:
        response_body = response.json()
        # Try to extract error code if it exists in response
        if isinstance(response_body, dict):
            error_code = response_body.get("error_code") or response_body.get("code")
    except Exception:
        # If JSON parsing fails, use text content
        try:
            response_body = response.text
        except Exception:
            response_body = None

    # Use provided message or generate default
    if not message:
        message = f"HTTP {status_code} error"
        if isinstance(response_body, dict):
            # Prefer common API error fields, including FastAPI's "detail"
            for key in ("message", "error", "detail"):
                api_message = response_body.get(key)
                if api_message:
                    message = str(api_message)
                    break
        elif isinstance(response_body, str) and response_body.strip():
            # If the server returned a plain-text or JSON string body, surface it
            message = response_body.strip()

    # Handle ValidationError special case for field errors
    if error_class == ValidationError and isinstance(response_body, dict):
        field_errors = response_body.get("errors") or response_body.get("field_errors")
        raise error_class(
            message,
            status_code=status_code,
            error_code=error_code,
            response_body=response_body,
            field_errors=field_errors,
        )
    else:
        raise error_class(
            message,
            status_code=status_code,
            error_code=error_code,
            response_body=response_body,
        )
