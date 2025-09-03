import httpx

from amigo_sdk.config import AmigoConfig
from amigo_sdk.errors import AuthenticationError
from amigo_sdk.generated.model import UserSignInWithApiKeyResponse


def _signin_url_headers(cfg: AmigoConfig) -> tuple[str, dict[str, str]]:
    url = f"{cfg.base_url}/v1/{cfg.organization_id}/user/signin_with_api_key"
    headers = {
        "x-api-key": cfg.api_key,
        "x-api-key-id": cfg.api_key_id,
        "x-user-id": cfg.user_id,
    }
    return url, headers


def _parse_signin_response_text(
    response: httpx.Response,
) -> UserSignInWithApiKeyResponse:
    try:
        return UserSignInWithApiKeyResponse.model_validate_json(response.text)
    except Exception as e:
        raise AuthenticationError(f"Invalid response format: {e}") from e


def sign_in_with_api_key(cfg: AmigoConfig) -> UserSignInWithApiKeyResponse:
    """Sign in with API key (sync)."""
    url, headers = _signin_url_headers(cfg)
    with httpx.Client() as client:
        try:
            response = client.post(url, headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise AuthenticationError(f"Sign in with API key failed: {e}") from e
        return _parse_signin_response_text(response)


async def sign_in_with_api_key_async(cfg: AmigoConfig) -> UserSignInWithApiKeyResponse:
    """Sign in with API key (async)."""
    url, headers = _signin_url_headers(cfg)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise AuthenticationError(f"Sign in with API key failed: {e}") from e
        return _parse_signin_response_text(response)
