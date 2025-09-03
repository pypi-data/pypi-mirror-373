from pydantic import Field
from pydantic_settings import BaseSettings


class AmigoConfig(BaseSettings):
    """
    Configuration for the Amigo API client.

    Can be configured via three methods (in order of precedence):
    1. Constructor parameters (highest precedence)
    2. Environment variables with AMIGO_ prefix
    3. .env file in the current working directory (lowest precedence)

    Environment variables:
    - AMIGO_API_KEY
    - AMIGO_API_KEY_ID
    - AMIGO_USER_ID
    - AMIGO_BASE_URL
    - AMIGO_ORGANIZATION_ID

    Example .env file:
    ```
    AMIGO_API_KEY=your_api_key_here
    AMIGO_API_KEY_ID=your_api_key_id_here
    AMIGO_USER_ID=your_user_id_here
    AMIGO_ORGANIZATION_ID=your_org_id_here
    AMIGO_BASE_URL=https://api.amigo.ai
    ```
    """

    api_key: str = Field(..., description="API key for authentication")
    api_key_id: str = Field(..., description="API key ID for authentication")
    user_id: str = Field(..., description="User ID for API requests")
    organization_id: str = Field(..., description="Organization ID for API requests")
    base_url: str = Field(
        default="https://api.amigo.ai",
        description="Base URL for the Amigo API",
    )

    model_config = {
        "env_prefix": "AMIGO_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "validate_assignment": True,
        "frozen": True,
        "extra": "ignore",  # Ignore extra fields in .env file
    }
