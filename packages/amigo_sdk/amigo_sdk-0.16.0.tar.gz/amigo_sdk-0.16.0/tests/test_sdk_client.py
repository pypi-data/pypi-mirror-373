import os
import tempfile
from unittest.mock import patch

import pytest

from amigo_sdk.config import AmigoConfig
from amigo_sdk.sdk_client import AmigoClient, AsyncAmigoClient


@pytest.fixture
def mock_config():
    return AmigoConfig(
        api_key="test-api-key",
        api_key_id="test-api-key-id",
        user_id="test-user-id",
        organization_id="test-org-id",
        base_url="https://api.example.com",
    )


@pytest.mark.unit
class TestAsyncAmigoClient:
    """Simple test suite for AmigoClient."""

    def test_client_initialization_with_config(self, mock_config):
        """Test client initializes with pre-configured AmigoConfig."""
        client = AsyncAmigoClient(config=mock_config)
        assert client.config == mock_config
        assert client._cfg == mock_config

    def test_client_initialization_with_kwargs(self):
        """Test client initializes with individual kwargs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)  # Avoid loading existing .env
                with patch.dict(os.environ, {}, clear=True):
                    client = AsyncAmigoClient(
                        api_key="test-api-key",
                        api_key_id="test-api-key-id",
                        user_id="test-user-id",
                        organization_id="test-org-id",
                    )
                    assert client.config.api_key == "test-api-key"
                    assert client.config.organization_id == "test-org-id"
            finally:
                os.chdir(original_cwd)

    def test_missing_config_raises_error(self):
        """Test missing config raises ValueError."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)  # Avoid loading existing .env
                with patch.dict(os.environ, {}, clear=True):
                    with pytest.raises(ValueError):
                        AsyncAmigoClient(
                            api_key="only-api-key"
                        )  # Missing required fields
            finally:
                os.chdir(original_cwd)

    def test_resources_are_accessible(self, mock_config):
        """Test organization and service resources are accessible."""
        client = AsyncAmigoClient(config=mock_config)

        # Should have resources (basic smoke test)
        assert client.organization is not None
        assert client.service is not None
        assert hasattr(client.organization, "_http")
        assert hasattr(client.service, "_http")

    @pytest.mark.asyncio
    async def test_async_context_manager(self, mock_config):
        """Test client works as async context manager."""
        async with AsyncAmigoClient(config=mock_config) as client:
            assert isinstance(client, AsyncAmigoClient)
            assert client.config == mock_config


@pytest.mark.unit
class TestAmigoClientSync:
    """Parity tests for the synchronous SDK client."""

    def test_client_initialization_with_config_sync(self, mock_config):
        client = AmigoClient(config=mock_config)
        assert client.config == mock_config
        assert client._cfg == mock_config

    def test_client_initialization_with_kwargs_sync(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                with patch.dict(os.environ, {}, clear=True):
                    client = AmigoClient(
                        api_key="test-api-key",
                        api_key_id="test-api-key-id",
                        user_id="test-user-id",
                        organization_id="test-org-id",
                    )
                    assert client.config.api_key == "test-api-key"
                    assert client.config.organization_id == "test-org-id"
            finally:
                os.chdir(original_cwd)

    def test_missing_config_raises_error_sync(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                with patch.dict(os.environ, {}, clear=True):
                    with pytest.raises(ValueError):
                        AmigoClient(api_key="only-api-key")
            finally:
                os.chdir(original_cwd)

    def test_resources_are_accessible_sync(self, mock_config):
        client = AmigoClient(config=mock_config)
        assert client.organization is not None
        assert client.service is not None
        assert hasattr(client.organization, "_http")
        assert hasattr(client.service, "_http")

    def test_context_manager_sync(self, mock_config):
        with AmigoClient(config=mock_config) as client:
            assert isinstance(client, AmigoClient)
