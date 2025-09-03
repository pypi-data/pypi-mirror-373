from amigo_sdk.generated.model import (
    OrganizationGetOrganizationResponse,
)
from amigo_sdk.http_client import AmigoAsyncHttpClient, AmigoHttpClient


class AsyncOrganizationResource:
    """Organization resource for Amigo API operations."""

    def __init__(self, http_client: AmigoAsyncHttpClient, organization_id: str) -> None:
        self._http = http_client
        self._organization_id = organization_id

    async def get(self) -> OrganizationGetOrganizationResponse:
        """
        Get the details of an organization.
        """
        response = await self._http.request(
            "GET", f"/v1/{self._organization_id}/organization/"
        )

        return OrganizationGetOrganizationResponse.model_validate_json(response.text)


class OrganizationResource:
    def __init__(self, http_client: AmigoHttpClient, organization_id: str) -> None:
        self._http = http_client
        self._organization_id = organization_id

    def get(self) -> OrganizationGetOrganizationResponse:
        response = self._http.request(
            "GET", f"/v1/{self._organization_id}/organization/"
        )
        return OrganizationGetOrganizationResponse.model_validate_json(response.text)
