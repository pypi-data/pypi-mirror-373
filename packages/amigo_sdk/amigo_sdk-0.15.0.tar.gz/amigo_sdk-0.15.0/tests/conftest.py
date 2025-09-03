import pytest
from dotenv import load_dotenv

# Load environment variables from .env file for testing
load_dotenv()

# Configure pytest-asyncio to automatically handle async tests
pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session")
def anyio_backend():
    """Configure the async backend for pytest-asyncio."""
    return "asyncio"


# Set asyncio mode to auto to automatically handle async test functions
def pytest_configure(config):
    """Configure pytest for async testing."""
    config.option.asyncio_mode = "auto"
