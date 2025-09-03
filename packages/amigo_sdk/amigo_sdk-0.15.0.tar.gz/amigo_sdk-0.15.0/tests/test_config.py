import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from amigo_sdk.config import AmigoConfig


@pytest.mark.unit
class TestAmigoConfig:
    """Test suite for AmigoConfig class."""

    def test_config_from_kwargs(self):
        """Test that config is loaded from keyword arguments."""
        config = AmigoConfig(
            api_key="test_api_key",
            api_key_id="test_api_key_id",
            user_id="test_user_id",
            organization_id="test_org_id",
            base_url="https://test.api.com",
        )

        assert config.api_key == "test_api_key"
        assert config.api_key_id == "test_api_key_id"
        assert config.user_id == "test_user_id"
        assert config.organization_id == "test_org_id"
        assert config.base_url == "https://test.api.com"

    def test_config_from_env_vars(self):
        """Test that config is loaded correctly from environment variables."""
        env_vars = {
            "AMIGO_API_KEY": "env_api_key",
            "AMIGO_API_KEY_ID": "env_api_key_id",
            "AMIGO_USER_ID": "env_user_id",
            "AMIGO_ORGANIZATION_ID": "env_org_id",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = AmigoConfig()

            assert config.api_key == "env_api_key"
            assert config.api_key_id == "env_api_key_id"
            assert config.user_id == "env_user_id"
            assert config.organization_id == "env_org_id"

    def test_config_from_env_file(self):
        """Test that config is loaded correctly from .env file."""
        env_content = "AMIGO_API_KEY=dotenv_key\nAMIGO_API_KEY_ID=dotenv_key_id\nAMIGO_USER_ID=dotenv_user\nAMIGO_ORGANIZATION_ID=dotenv_org"

        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            env_file.write_text(env_content)

            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                with patch.dict(os.environ, {}, clear=True):
                    config = AmigoConfig()

                    assert config.api_key == "dotenv_key"
                    assert config.api_key_id == "dotenv_key_id"
                    assert config.user_id == "dotenv_user"
                    assert config.organization_id == "dotenv_org"
            finally:
                os.chdir(original_cwd)

    def test_kwargs_override_env(self):
        """Test that keyword arguments take precedence over environment variables."""
        with patch.dict(
            os.environ,
            {
                "AMIGO_API_KEY": "env_key",
                "AMIGO_API_KEY_ID": "env_key_id",
                "AMIGO_USER_ID": "env_user",
                "AMIGO_ORGANIZATION_ID": "env_org",
            },
            clear=True,
        ):
            config = AmigoConfig(
                api_key="kwargs_key",  # Should override env
                api_key_id="kwargs_key_id",  # Should override env
                # user_id and organization_id should come from env
            )

            assert config.api_key == "kwargs_key"
            assert config.api_key_id == "kwargs_key_id"
            assert config.user_id == "env_user"
            assert config.organization_id == "env_org"

    def test_missing_config_raises_error(self):
        """Test that missing required config fields raise validation error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)  # Avoid loading existing .env
                with patch.dict(os.environ, {}, clear=True):
                    with pytest.raises(ValidationError) as exc_info:
                        AmigoConfig()

                    error_str = str(exc_info.value)
                    assert "api_key" in error_str
                    assert "api_key_id" in error_str
                    assert "user_id" in error_str
                    assert "organization_id" in error_str
            finally:
                os.chdir(original_cwd)

    def test_partial_missing_config_raises_error(self):
        """Test that partially missing config raises error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)  # Avoid loading existing .env
                with patch.dict(os.environ, {}, clear=True):
                    with pytest.raises(ValidationError):
                        AmigoConfig(
                            api_key="key", api_key_id="key_id"
                        )  # Missing user_id, organization_id
            finally:
                os.chdir(original_cwd)

    def test_config_is_immutable(self):
        """Test that config object is immutable after creation."""
        config = AmigoConfig(
            api_key="key", api_key_id="key_id", user_id="user", organization_id="org"
        )

        with pytest.raises(ValidationError):
            config.api_key = "new_key"
