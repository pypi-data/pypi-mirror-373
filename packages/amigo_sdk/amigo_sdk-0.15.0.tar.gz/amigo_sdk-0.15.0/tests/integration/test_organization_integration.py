import os

import pytest

from amigo_sdk.config import AmigoConfig
from amigo_sdk.errors import AuthenticationError
from amigo_sdk.generated.model import (
    OrganizationGetOrganizationResponse,
    ServiceGetServicesResponse,
)
from amigo_sdk.sdk_client import AmigoClient, AsyncAmigoClient


@pytest.fixture
def required_env_vars():
    """Check that required environment variables are set."""
    required_vars = [
        "AMIGO_API_KEY",
        "AMIGO_API_KEY_ID",
        "AMIGO_USER_ID",
        "AMIGO_ORGANIZATION_ID",
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        pytest.fail(
            f"Integration tests require environment variables to be set.\n"
            f"Missing: {', '.join(missing_vars)}\n\n"
            f"Please set these environment variables or create a .env file in the project root:\n"
            f"AMIGO_API_KEY=your-api-key\n"
            f"AMIGO_API_KEY_ID=your-api-key-id\n"
            f"AMIGO_USER_ID=your-user-id\n"
            f"AMIGO_ORGANIZATION_ID=your-organization-id\n"
            f"AMIGO_BASE_URL=https://your-api-base-url (optional)"
        )

    return {var: os.getenv(var) for var in required_vars}


@pytest.mark.integration
class TestOrganizationIntegration:
    agent_id: str | None = None
    """Integration tests for Amigo API.

    These tests make actual API calls to the Amigo service.
    Required environment variables: AMIGO_API_KEY, AMIGO_API_KEY_ID,
    AMIGO_USER_ID, AMIGO_ORGANIZATION_ID, AMIGO_BASE_URL (optional).

    Create a .env file in the project root or set environment variables directly.
    Tests will fail if required variables are missing.
    """

    async def test_get_services(self):
        """Test getting services."""
        async with AsyncAmigoClient() as client:
            services = await client.service.get_services()

            assert services is not None
            assert isinstance(services, ServiceGetServicesResponse)

    async def test_get_organization(self):
        """Test getting organization details using environment variables for config."""

        # Create client using environment variables
        async with AsyncAmigoClient() as client:
            # Get organization details
            organization = await client.organization.get()

            # Verify we got a valid response
            assert organization is not None

            # Verify response is the correct pydantic model type
            assert isinstance(organization, OrganizationGetOrganizationResponse)

            # Verify model can serialize (proves it's valid)
            assert organization.model_dump_json() is not None

            # Verify organization has a title field
            assert hasattr(organization, "title"), (
                "Organization should have a title field"
            )
            assert organization.title is not None, (
                "Organization title should not be None"
            )

    async def test_invalid_credentials_raises_authentication_error(self):
        """Test that invalid credentials raise appropriate authentication errors."""

        # Fail if we don't have valid credentials to test with
        if not os.getenv("AMIGO_API_KEY"):
            pytest.fail(
                "Cannot test authentication error handling without valid credentials.\n"
                "Please set AMIGO_API_KEY environment variable."
            )

        # Create client with invalid API key
        with pytest.raises(AuthenticationError):
            async with AsyncAmigoClient(
                api_key="invalid_key",
            ) as client:
                await client.organization.get()

    async def test_client_config_property(self, required_env_vars):
        """Test that the client config property works correctly."""

        async with AsyncAmigoClient() as client:
            config = client.config

            # Verify config contains expected values
            assert config.api_key == required_env_vars["AMIGO_API_KEY"]
            assert config.api_key_id == required_env_vars["AMIGO_API_KEY_ID"]
            assert config.user_id == required_env_vars["AMIGO_USER_ID"]
            assert config.organization_id == required_env_vars["AMIGO_ORGANIZATION_ID"]
            assert config.base_url == os.getenv(
                "AMIGO_BASE_URL", "https://api.amigo.ai"
            )

    def test_config_creation(self, required_env_vars):
        """Test that AmigoConfig can be created from environment variables."""
        # This should work now with the fixed field aliases
        config = AmigoConfig()

        # Verify config contains expected values
        assert config.api_key == required_env_vars["AMIGO_API_KEY"]
        assert config.api_key_id == required_env_vars["AMIGO_API_KEY_ID"]
        assert config.user_id == required_env_vars["AMIGO_USER_ID"]
        assert config.organization_id == required_env_vars["AMIGO_ORGANIZATION_ID"]


@pytest.mark.integration
class TestOrganizationIntegrationSync:
    def test_get_services(self):
        with AmigoClient() as client:
            services = client.service.get_services()

            assert services is not None
            assert isinstance(services, ServiceGetServicesResponse)

    def test_get_organization(self):
        with AmigoClient() as client:
            organization = client.organization.get()

            assert organization is not None
            assert isinstance(organization, OrganizationGetOrganizationResponse)
            assert organization.model_dump_json() is not None
            assert hasattr(organization, "title")
            assert organization.title is not None

    def test_invalid_credentials_raises_authentication_error(self):
        if not os.getenv("AMIGO_API_KEY"):
            pytest.fail(
                "Cannot test authentication error handling without valid credentials.\n"
                "Please set AMIGO_API_KEY environment variable."
            )

        with pytest.raises(AuthenticationError):
            with AmigoClient(api_key="invalid_key") as client:
                client.organization.get()

    def test_client_config_property(self, required_env_vars):
        with AmigoClient() as client:
            config = client.config

            assert config.api_key == required_env_vars["AMIGO_API_KEY"]
            assert config.api_key_id == required_env_vars["AMIGO_API_KEY_ID"]
            assert config.user_id == required_env_vars["AMIGO_USER_ID"]
            assert config.organization_id == required_env_vars["AMIGO_ORGANIZATION_ID"]
            assert config.base_url == os.getenv(
                "AMIGO_BASE_URL", "https://api.amigo.ai"
            )

    def test_config_creation(self, required_env_vars):
        config = AmigoConfig()

        assert config.api_key == required_env_vars["AMIGO_API_KEY"]
        assert config.api_key_id == required_env_vars["AMIGO_API_KEY_ID"]
        assert config.user_id == required_env_vars["AMIGO_USER_ID"]
        assert config.organization_id == required_env_vars["AMIGO_ORGANIZATION_ID"]
