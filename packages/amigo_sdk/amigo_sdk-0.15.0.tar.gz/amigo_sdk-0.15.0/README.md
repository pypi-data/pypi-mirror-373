# Amigo Python SDK

[![Tests](https://github.com/amigo-ai/amigo-python-sdk/actions/workflows/test.yml/badge.svg)](https://github.com/amigo-ai/amigo-python-sdk/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/amigo-ai/amigo-python-sdk/graph/badge.svg?token=1A7KVPV9ZR)](https://codecov.io/gh/amigo-ai/amigo-python-sdk)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The official Python SDK for the Amigo API, providing a simple and intuitive interface to interact with Amigo's AI services.

## Installation

Install the SDK using pip:

```bash
pip install amigo_sdk
```

Or add it to your requirements.txt:

```txt
amigo_sdk
```

### API compatibility

This SDK auto-generates its types from the latest [Amigo OpenAPI schema](https://api.amigo.ai/v1/openapi.json). As a result, only the latest published SDK version is guaranteed to match the current API. If you pin to an older version, it may not include the newest endpoints or fields.

## Quick Start (sync)

```python
from amigo_sdk import AmigoClient
from amigo_sdk.models import GetConversationsParametersQuery

# Initialize and use the client synchronously
with AmigoClient(
    api_key="your-api-key",
    api_key_id="your-api-key-id",
    user_id="user-id",
    organization_id="your-organization-id",
) as client:
    conversations = client.conversation.get_conversations(
        GetConversationsParametersQuery(limit=10, sort_by=["-created_at"])
    )
    print("Conversations:", conversations)
```

## Quick Start (async)

```python
import asyncio

from amigo_sdk import AsyncAmigoClient
from amigo_sdk.models import GetConversationsParametersQuery


async def main():
    async with AsyncAmigoClient(
        api_key="your-api-key",
        api_key_id="your-api-key-id",
        user_id="user-id",
        organization_id="your-organization-id",
    ) as client:
        conversations = await client.conversation.get_conversations(
            GetConversationsParametersQuery(limit=10, sort_by=["-created_at"])
        )
        print("Conversations:", conversations)


asyncio.run(main())
```

## Examples

For more SDK usage examples see the [examples overview](examples/README.md). Direct links:

- **Conversation (sync)**: [examples/conversation/conversation.py](examples/conversation/conversation.py)
- **Conversation (async)**: [examples/conversation/conversation_async.py](examples/conversation/conversation_async.py)
- **User management (sync)**: [examples/user/user-management.py](examples/user/user-management.py)

## Configuration

The SDK requires the following configuration parameters:

| Parameter         | Type | Required | Description                                                    |
| ----------------- | ---- | -------- | -------------------------------------------------------------- |
| `api_key`         | str  | ✅       | API key from Amigo dashboard                                   |
| `api_key_id`      | str  | ✅       | API key ID from Amigo dashboard                                |
| `user_id`         | str  | ✅       | User ID on whose behalf the request is made                    |
| `organization_id` | str  | ✅       | Your organization ID                                           |
| `base_url`        | str  | ❌       | Base URL of the Amigo API (defaults to `https://api.amigo.ai`) |

### Environment Variables

You can also configure the SDK using environment variables:

```bash
export AMIGO_API_KEY="your-api-key"
export AMIGO_API_KEY_ID="your-api-key-id"
export AMIGO_USER_ID="user-id"
export AMIGO_ORGANIZATION_ID="your-organization-id"
export AMIGO_BASE_URL="https://api.amigo.ai"  # optional
```

Then initialize the client without parameters:

```python
from amigo_sdk import AmigoClient

# Automatically loads from environment variables
with AmigoClient() as client:
    ...
```

### Using .env Files

Create a `.env` file in your project root:

```env
AMIGO_API_KEY=your-api-key
AMIGO_API_KEY_ID=your-api-key-id
AMIGO_USER_ID=user-id
AMIGO_ORG_ID=your-organization-id
```

The SDK will automatically load these variables.

### Getting Your API Credentials

1. **API Key & API Key ID**: Generate these from your Amigo admin dashboard or programmatically using the API
2. **Organization ID**: Found in your Amigo dashboard URL or organization settings
3. **User ID**: The ID of the user you want to impersonate for API calls

For detailed instructions on generating API keys, see the [Authentication Guide](https://docs.amigo.ai/developer-guide).

## Available Resources

The SDK provides access to the following resources:

- **Organizations**: Get Organization info
- **Services**: Get available services
- **Conversation**: Manage conversations
- **User**: Manage users

## Generated types

The SDK ships with Pydantic models generated from the latest OpenAPI schema.

- **Importing types**: Import directly from `amigo_sdk.models`

  ```python
  from amigo_sdk.models import (
      GetConversationsParametersQuery,
      ConversationCreateConversationRequest,
      GetUsersParametersQuery,
  )
  ```

- **Using types when calling SDK functions**: Pass request/query models to resource methods.

  ```python
  from amigo_sdk import AmigoClient
  from amigo_sdk.models import GetConversationsParametersQuery

  with AmigoClient() as client:
     conversations = client.conversation.get_conversations(
         GetConversationsParametersQuery(limit=20, sort_by=["-created_at"])
     )
  ```

- **Parsing returned objects**: Responses are Pydantic models. Access fields directly or convert to dict/JSON.

  ```python
  # Access fields
  first = conversations.conversations[0]
  print(first.id, first.created_at)

  # Convert to plain dict for logging/serialization
  print(first.model_dump(mode="json"))
  ```

## Error Handling

The SDK provides typed error handling:

```python
from amigo_sdk import AmigoClient
from amigo_sdk.errors import (
    AuthenticationError,
    NotFoundError,
    BadRequestError,
    ValidationError,
)

try:
    with AmigoClient() as client:
        org = client.organization.get()
        print("Organization:", org)
except AuthenticationError as error:
    print("Authentication failed:", error)
except NotFoundError as error:
    print("Resource not found:", error)
except BadRequestError as error:
    print("Bad request:", error)
except ValidationError as error:
    print("Validation error:", error)
except Exception as error:
    print("Unexpected error:", error)
```

## Retries

The HTTP client includes sensible, configurable retries:

- **Defaults**:

  - max attempts: 3
  - backoff base: 0.25s (exponential with full jitter)
  - max delay per attempt: 30s
  - retry on status: {408, 429, 500, 502, 503, 504}
  - retry on methods: {"GET"}
  - special-case: POST is retried on 429 when `Retry-After` is present
  - 401 triggers a one-time token refresh and immediate retry

## Development

For detailed development setup, testing, and contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Documentation

- **Developer Guide**: [https://docs.amigo.ai/developer-guide](https://docs.amigo.ai/developer-guide)
- **API Reference**: [https://docs.amigo.ai/api-reference](https://docs.amigo.ai/api-reference)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions, issues, or feature requests, please visit our [GitHub repository](https://github.com/amigo-ai/amigo-python-sdk) or contact support through the Amigo dashboard.
