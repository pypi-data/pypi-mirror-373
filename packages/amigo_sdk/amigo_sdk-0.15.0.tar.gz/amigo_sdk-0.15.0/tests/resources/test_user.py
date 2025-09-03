import pytest

from amigo_sdk.config import AmigoConfig
from amigo_sdk.errors import NotFoundError, ValidationError
from amigo_sdk.generated.model import (
    GetUsersParametersQuery,
    UserCreateInvitedUserRequest,
    UserCreateInvitedUserResponse,
    UserGetUsersResponse,
    UserUpdateUserInfoRequest,
)
from amigo_sdk.http_client import AmigoAsyncHttpClient, AmigoHttpClient
from amigo_sdk.resources.user import AsyncUserResource, UserResource

from .helpers import mock_http_request, mock_http_request_sync


@pytest.fixture
def mock_config():
    return AmigoConfig(
        api_key="test-api-key",
        api_key_id="test-api-key-id",
        user_id="test-user-id",
        organization_id="test-org",
        base_url="https://api.example.com",
    )


@pytest.fixture
def user_resource(mock_config):
    http_client = AmigoAsyncHttpClient(mock_config)
    return AsyncUserResource(http_client, mock_config.organization_id)


@pytest.mark.unit
class TestUserResource:
    @pytest.mark.asyncio
    async def test_get_users_returns_data_and_supports_query(self, user_resource):
        mock_response = UserGetUsersResponse(
            users=[], has_more=False, continuation_token=None
        )

        async with mock_http_request(mock_response):
            params = GetUsersParametersQuery(
                user_id=["u-1", "u-2"],
                email=["a@example.com"],
                is_verified=True,
                limit=10,
                continuation_token=5,
                sort_by=["+created_at", "-created_at"],
            )

            result = await user_resource.get_users(params)

            assert isinstance(result, UserGetUsersResponse)
            assert result.has_more is False
            assert result.continuation_token is None

    @pytest.mark.asyncio
    async def test_get_users_not_found_raises(self, user_resource):
        async with mock_http_request("{}", status_code=404):
            with pytest.raises(NotFoundError):
                await user_resource.get_users()

    @pytest.mark.asyncio
    async def test_create_user_sends_body_and_returns_response(self, user_resource):
        body = UserCreateInvitedUserRequest(
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
            role_name="admin",
        )
        mock_response = UserCreateInvitedUserResponse(user_id="u-100", verify_link=None)

        async with mock_http_request(mock_response):
            result = await user_resource.create_user(body)
            assert isinstance(result, UserCreateInvitedUserResponse)
            assert result.user_id == "u-100"

    @pytest.mark.asyncio
    async def test_create_user_validation_error_raises(self, user_resource):
        body = UserCreateInvitedUserRequest(
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
            role_name="admin",
        )

        async with mock_http_request({"detail": "bad"}, status_code=422):
            with pytest.raises(ValidationError):
                await user_resource.create_user(body)

    @pytest.mark.asyncio
    async def test_delete_user_returns_none(self, user_resource):
        async with mock_http_request("", status_code=204):
            result = await user_resource.delete_user("u-1")
            assert result is None

    @pytest.mark.asyncio
    async def test_delete_user_not_found_raises(self, user_resource):
        async with mock_http_request("{}", status_code=404):
            with pytest.raises(NotFoundError):
                await user_resource.delete_user("missing")

    @pytest.mark.asyncio
    async def test_update_user_returns_none(self, user_resource):
        body = UserUpdateUserInfoRequest(
            first_name="Grace", last_name="Hopper", preferred_language={}, timezone={}
        )

        async with mock_http_request("", status_code=204):
            result = await user_resource.update_user("u-1", body)
            assert result is None

    @pytest.mark.asyncio
    async def test_update_user_validation_error_raises(self, user_resource):
        body = UserUpdateUserInfoRequest(
            first_name="X", last_name="Y", preferred_language=None, timezone=None
        )

        async with mock_http_request({"detail": "bad"}, status_code=422):
            with pytest.raises(ValidationError):
                await user_resource.update_user("u-1", body)


@pytest.mark.unit
class TestUserResourceSync:
    """Sync UserResource tests mirroring async coverage."""

    def _resource(self, mock_config) -> UserResource:
        http = AmigoHttpClient(mock_config)
        return UserResource(http, mock_config.organization_id)

    def test_get_users_returns_data_and_supports_query_sync(self, mock_config):
        res = self._resource(mock_config)
        mock_response = UserGetUsersResponse(
            users=[], has_more=False, continuation_token=None
        )
        with mock_http_request_sync(mock_response):
            params = GetUsersParametersQuery(
                user_id=["u-1", "u-2"],
                email=["a@example.com"],
                is_verified=True,
                limit=10,
                continuation_token=5,
                sort_by=["+created_at", "-created_at"],
            )
            result = res.get_users(params)
            assert isinstance(result, UserGetUsersResponse)
            assert result.has_more is False
            assert result.continuation_token is None

    def test_get_users_not_found_raises_sync(self, mock_config):
        res = self._resource(mock_config)
        with mock_http_request_sync("{}", status_code=404):
            with pytest.raises(NotFoundError):
                res.get_users()

    def test_create_user_sends_body_and_returns_response_sync(self, mock_config):
        res = self._resource(mock_config)
        body = UserCreateInvitedUserRequest(
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
            role_name="admin",
        )
        mock_response = UserCreateInvitedUserResponse(user_id="u-100", verify_link=None)
        with mock_http_request_sync(mock_response):
            result = res.create_user(body)
            assert isinstance(result, UserCreateInvitedUserResponse)
            assert result.user_id == "u-100"

    def test_create_user_validation_error_raises_sync(self, mock_config):
        res = self._resource(mock_config)
        body = UserCreateInvitedUserRequest(
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
            role_name="admin",
        )
        with mock_http_request_sync({"detail": "bad"}, status_code=422):
            with pytest.raises(ValidationError):
                res.create_user(body)

    def test_delete_user_returns_none_sync(self, mock_config):
        res = self._resource(mock_config)
        with mock_http_request_sync("", status_code=204):
            result = res.delete_user("u-1")
            assert result is None

    def test_delete_user_not_found_raises_sync(self, mock_config):
        res = self._resource(mock_config)
        with mock_http_request_sync("{}", status_code=404):
            with pytest.raises(NotFoundError):
                res.delete_user("missing")

    def test_update_user_returns_none_sync(self, mock_config):
        res = self._resource(mock_config)
        body = UserUpdateUserInfoRequest(
            first_name="Grace", last_name="Hopper", preferred_language={}, timezone={}
        )
        with mock_http_request_sync("", status_code=204):
            result = res.update_user("u-1", body)
            assert result is None

    def test_update_user_validation_error_raises_sync(self, mock_config):
        res = self._resource(mock_config)
        body = UserUpdateUserInfoRequest(
            first_name="X", last_name="Y", preferred_language=None, timezone=None
        )
        with mock_http_request_sync({"detail": "bad"}, status_code=422):
            with pytest.raises(ValidationError):
                res.update_user("u-1", body)
