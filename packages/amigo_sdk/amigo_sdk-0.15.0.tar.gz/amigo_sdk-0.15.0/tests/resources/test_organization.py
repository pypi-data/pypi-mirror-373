import pytest

from amigo_sdk.config import AmigoConfig
from amigo_sdk.errors import NotFoundError
from amigo_sdk.generated.model import (
    OrganizationGetOrganizationResponse,
)
from amigo_sdk.http_client import AmigoAsyncHttpClient, AmigoHttpClient
from amigo_sdk.resources.organization import (
    AsyncOrganizationResource,
    OrganizationResource,
)

from .helpers import (
    create_organization_response_data,
    mock_http_request,
    mock_http_request_sync,
)


@pytest.fixture
def mock_config():
    return AmigoConfig(
        api_key="test-api-key",
        api_key_id="test-api-key-id",
        user_id="test-user-id",
        organization_id="test-org-123",
        base_url="https://api.example.com",
    )


@pytest.fixture
def organization_resource(mock_config) -> AsyncOrganizationResource:
    http_client = AmigoAsyncHttpClient(mock_config)
    return AsyncOrganizationResource(http_client, "test-org-123")


@pytest.mark.unit
class TestOrganizationResource:
    """Simple test suite for the Organization Resource."""

    @pytest.mark.asyncio
    async def test_get_organization_returns_expected_data(
        self, organization_resource: AsyncOrganizationResource
    ):
        """Test get method returns properly parsed organization data."""
        mock_data = create_organization_response_data()

        async with mock_http_request(mock_data):
            result = await organization_resource.get()

            assert isinstance(result, OrganizationGetOrganizationResponse)
            assert result.org_id == "test-org-123"
            assert result.org_name == "Test Organization"
            assert result.title == "Your AI Assistant Platform"
            assert len(result.onboarding_instructions) == 2

    @pytest.mark.asyncio
    async def test_get_nonexistent_organization_raises_not_found(
        self, organization_resource: AsyncOrganizationResource
    ) -> None:
        """Test get method raises NotFoundError for non-existent organization."""
        async with mock_http_request(
            '{"error": "Organization not found"}', status_code=404
        ):
            with pytest.raises(NotFoundError):
                await organization_resource.get()


@pytest.mark.unit
class TestOrganizationResourceSync:
    """Sync OrganizationResource tests mirroring async coverage."""

    def _resource(self, mock_config) -> OrganizationResource:
        http = AmigoHttpClient(mock_config)
        return OrganizationResource(http, mock_config.organization_id)

    def test_get_organization_returns_expected_data_sync(self, mock_config):
        res = self._resource(mock_config)
        mock_data = create_organization_response_data()
        with mock_http_request_sync(mock_data):
            result = res.get()
            assert isinstance(result, OrganizationGetOrganizationResponse)
            assert result.org_id == "test-org-123"
            assert result.org_name == "Test Organization"
            assert result.title == "Your AI Assistant Platform"
            assert len(result.onboarding_instructions) == 2

    def test_get_nonexistent_organization_raises_not_found_sync(self, mock_config):
        res = self._resource(mock_config)
        with mock_http_request_sync(
            '{"error": "Organization not found"}', status_code=404
        ):
            with pytest.raises(NotFoundError):
                res.get()
