from typing import Optional

from amigo_sdk.generated.model import (
    GetUsersParametersQuery,
    UserCreateInvitedUserRequest,
    UserCreateInvitedUserResponse,
    UserGetUsersResponse,
    UserUpdateUserInfoRequest,
)
from amigo_sdk.http_client import AmigoAsyncHttpClient, AmigoHttpClient


class AsyncUserResource:
    """User resource for Amigo API operations."""

    def __init__(self, http_client: AmigoAsyncHttpClient, organization_id: str) -> None:
        self._http = http_client
        self._organization_id = organization_id

    async def get_users(
        self, params: Optional[GetUsersParametersQuery] = None
    ) -> UserGetUsersResponse:
        """Get a list of users in the organization."""
        response = await self._http.request(
            "GET",
            f"/v1/{self._organization_id}/user/",
            params=params.model_dump(mode="json", exclude_none=True)
            if params
            else None,
        )
        return UserGetUsersResponse.model_validate_json(response.text)

    async def create_user(
        self, body: UserCreateInvitedUserRequest
    ) -> UserCreateInvitedUserResponse:
        """Create (invite) a new user to the organization."""
        response = await self._http.request(
            "POST",
            f"/v1/{self._organization_id}/user/invite",
            json=body.model_dump(mode="json", exclude_none=True),
        )
        return UserCreateInvitedUserResponse.model_validate_json(response.text)

    async def delete_user(self, user_id: str) -> None:
        """Delete a user by ID. Returns None on success (e.g., 204)."""
        await self._http.request(
            "DELETE",
            f"/v1/{self._organization_id}/user/{user_id}",
        )

    async def update_user(self, user_id: str, body: UserUpdateUserInfoRequest) -> None:
        """Update user information. Returns None on success (e.g., 204)."""
        await self._http.request(
            "POST",
            f"/v1/{self._organization_id}/user/{user_id}/user",
            json=body.model_dump(mode="json", exclude_none=True),
        )


class UserResource:
    """User resource (synchronous)."""

    def __init__(self, http_client: AmigoHttpClient, organization_id: str) -> None:
        self._http = http_client
        self._organization_id = organization_id

    def get_users(
        self, params: Optional[GetUsersParametersQuery] = None
    ) -> UserGetUsersResponse:
        response = self._http.request(
            "GET",
            f"/v1/{self._organization_id}/user/",
            params=params.model_dump(mode="json", exclude_none=True)
            if params
            else None,
        )
        return UserGetUsersResponse.model_validate_json(response.text)

    def create_user(
        self, body: UserCreateInvitedUserRequest
    ) -> UserCreateInvitedUserResponse:
        response = self._http.request(
            "POST",
            f"/v1/{self._organization_id}/user/invite",
            json=body.model_dump(mode="json", exclude_none=True),
        )
        return UserCreateInvitedUserResponse.model_validate_json(response.text)

    def delete_user(self, user_id: str) -> None:
        self._http.request("DELETE", f"/v1/{self._organization_id}/user/{user_id}")

    def update_user(self, user_id: str, body: UserUpdateUserInfoRequest) -> None:
        self._http.request(
            "POST",
            f"/v1/{self._organization_id}/user/{user_id}/user",
            json=body.model_dump(mode="json", exclude_none=True),
        )
