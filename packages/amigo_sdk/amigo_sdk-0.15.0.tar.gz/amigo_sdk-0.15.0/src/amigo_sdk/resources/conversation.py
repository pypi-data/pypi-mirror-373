import asyncio
import threading
from collections.abc import AsyncGenerator, Iterator
from datetime import datetime
from typing import Any, Literal

from pydantic import AnyUrl, BaseModel

from amigo_sdk.generated.model import (
    ConversationCreateConversationRequest,
    ConversationCreateConversationResponse,
    ConversationGenerateConversationStarterRequest,
    ConversationGenerateConversationStarterResponse,
    ConversationGetConversationMessagesResponse,
    ConversationGetConversationsResponse,
    ConversationGetInteractionInsightsResponse,
    ConversationInteractWithConversationResponse,
    ConversationRecommendResponsesForInteractionResponse,
    CreateConversationParametersQuery,
    Format,
    GetConversationMessagesParametersQuery,
    GetConversationsParametersQuery,
    InteractWithConversationParametersQuery,
)
from amigo_sdk.http_client import AmigoAsyncHttpClient, AmigoHttpClient


class GetMessageSourceResponse(BaseModel):
    """
    Response model for the `get_message_source` endpoint.
    TODO: Remove once the OpenAPI spec contains the correct response model for this endpoint.
    """

    url: AnyUrl
    expires_at: datetime
    content_type: Literal["audio/mpeg", "audio/wav"]


class AsyncConversationResource:
    """Conversation resource for Amigo API operations."""

    def __init__(self, http_client: AmigoAsyncHttpClient, organization_id: str) -> None:
        self._http = http_client
        self._organization_id = organization_id

    async def create_conversation(
        self,
        body: ConversationCreateConversationRequest,
        params: CreateConversationParametersQuery,
        abort_event: asyncio.Event | None = None,
    ) -> "AsyncGenerator[ConversationCreateConversationResponse, None]":
        """Create a new conversation and stream NDJSON events.

        Returns an async generator yielding `ConversationCreateConversationResponse` events.
        """

        async def _generator():
            async for line in self._http.stream_lines(
                "POST",
                f"/v1/{self._organization_id}/conversation/",
                params=params.model_dump(mode="json", exclude_none=True),
                json=body.model_dump(mode="json", exclude_none=True),
                headers={"Accept": "application/x-ndjson"},
                abort_event=abort_event,
            ):
                # Each line is a JSON object representing a discriminated union event
                yield ConversationCreateConversationResponse.model_validate_json(line)

        return _generator()

    async def interact_with_conversation(
        self,
        conversation_id: str,
        params: InteractWithConversationParametersQuery,
        abort_event: asyncio.Event | None = None,
        *,
        text_message: str | None = None,
        audio_bytes: bytes | None = None,
        audio_content_type: Literal["audio/mpeg", "audio/wav"] | None = None,
    ) -> "AsyncGenerator[ConversationInteractWithConversationResponse, None]":
        """Interact with a conversation and stream NDJSON events.

        Returns an async generator yielding `ConversationInteractWithConversationResponse` events.
        """

        async def _generator():
            request_kwargs: dict[str, Any] = {
                "params": params.model_dump(mode="json", exclude_none=True),
                "abort_event": abort_event,
                "headers": {"Accept": "application/x-ndjson"},
            }
            # Route based on requested format
            req_format = getattr(params, "request_format", None)
            if req_format == Format.text:
                if text_message is None:
                    raise ValueError(
                        "text_message is required when request_format is 'text'"
                    )
                text_bytes = text_message.encode("utf-8")
                request_kwargs["files"] = {
                    "recorded_message": (
                        "message.txt",
                        text_bytes,
                        "text/plain; charset=utf-8",
                    )
                }
            elif req_format == Format.voice:
                if audio_bytes is None or audio_content_type is None:
                    raise ValueError(
                        "audio_bytes and audio_content_type are required when request_format is 'voice'"
                    )
                # Send raw bytes with appropriate content type
                request_kwargs["content"] = audio_bytes
                request_kwargs.setdefault("headers", {})
                request_kwargs["headers"]["Content-Type"] = audio_content_type
            else:
                raise ValueError("Unsupported or missing request_format in params")

            async for line in self._http.stream_lines(
                "POST",
                f"/v1/{self._organization_id}/conversation/{conversation_id}/interact",
                **request_kwargs,
            ):
                # Each line is a JSON object representing a discriminated union event
                yield ConversationInteractWithConversationResponse.model_validate_json(
                    line
                )

        return _generator()

    async def finish_conversation(self, conversation_id: str) -> None:
        """Finish a conversation."""
        await self._http.request(
            "POST",
            f"/v1/{self._organization_id}/conversation/{conversation_id}/finish/",
        )

    async def get_conversations(
        self, params: GetConversationsParametersQuery
    ) -> ConversationGetConversationsResponse:
        """Get conversations."""
        response = await self._http.request(
            "GET",
            f"/v1/{self._organization_id}/conversation/",
            params=params.model_dump(mode="json", exclude_none=True),
        )
        return ConversationGetConversationsResponse.model_validate_json(response.text)

    async def get_conversation_messages(
        self, conversation_id: str, params: GetConversationMessagesParametersQuery
    ) -> ConversationGetConversationMessagesResponse:
        """Get conversation messages."""
        response = await self._http.request(
            "GET",
            f"/v1/{self._organization_id}/conversation/{conversation_id}/messages/",
            params=params.model_dump(
                mode="json", exclude_none=True, exclude_defaults=True
            ),
        )
        return ConversationGetConversationMessagesResponse.model_validate_json(
            response.text
        )

    async def recommend_responses_for_interaction(
        self, conversation_id: str, interaction_id: str
    ) -> ConversationRecommendResponsesForInteractionResponse:
        """Recommend responses for an interaction."""
        response = await self._http.request(
            "GET",
            f"/v1/{self._organization_id}/conversation/{conversation_id}/interaction/{interaction_id}/recommend_responses",
        )
        return ConversationRecommendResponsesForInteractionResponse.model_validate_json(
            response.text
        )

    async def get_interaction_insights(
        self, conversation_id: str, interaction_id: str
    ) -> ConversationGetInteractionInsightsResponse:
        """Get insights for an interaction."""
        response = await self._http.request(
            "GET",
            f"/v1/{self._organization_id}/conversation/{conversation_id}/interaction/{interaction_id}/insights",
        )
        return ConversationGetInteractionInsightsResponse.model_validate_json(
            response.text
        )

    async def get_message_source(
        self, conversation_id: str, message_id: str
    ) -> GetMessageSourceResponse:
        """Get the source of a message."""
        response = await self._http.request(
            "GET",
            f"/v1/{self._organization_id}/conversation/{conversation_id}/messages/{message_id}/source",
        )
        return GetMessageSourceResponse.model_validate_json(response.text)

    async def generate_conversation_starters(
        self, body: ConversationGenerateConversationStarterRequest
    ) -> ConversationGenerateConversationStarterResponse:
        """Generate conversation starters."""
        response = await self._http.request(
            "POST",
            f"/v1/{self._organization_id}/conversation/conversation_starter",
            json=body.model_dump(mode="json", exclude_none=True),
        )
        return ConversationGenerateConversationStarterResponse.model_validate_json(
            response.text
        )


class ConversationResource:
    """Conversation resource for synchronous operations."""

    def __init__(self, http_client: AmigoHttpClient, organization_id: str) -> None:
        self._http = http_client
        self._organization_id = organization_id

    def create_conversation(
        self,
        body: ConversationCreateConversationRequest,
        params: CreateConversationParametersQuery,
        abort_event: threading.Event | None = None,
    ) -> Iterator[ConversationCreateConversationResponse]:
        def _iter():
            for line in self._http.stream_lines(
                "POST",
                f"/v1/{self._organization_id}/conversation/",
                params=params.model_dump(mode="json", exclude_none=True),
                json=body.model_dump(mode="json", exclude_none=True),
                headers={"Accept": "application/x-ndjson"},
                abort_event=abort_event,
            ):
                yield ConversationCreateConversationResponse.model_validate_json(line)

        return _iter()

    def interact_with_conversation(
        self,
        conversation_id: str,
        params: InteractWithConversationParametersQuery,
        abort_event: threading.Event | None = None,
        *,
        text_message: str | None = None,
        audio_bytes: bytes | None = None,
        audio_content_type: Literal["audio/mpeg", "audio/wav"] | None = None,
    ) -> Iterator[ConversationInteractWithConversationResponse]:
        def _iter():
            request_kwargs: dict[str, Any] = {
                "params": params.model_dump(mode="json", exclude_none=True),
                "headers": {"Accept": "application/x-ndjson"},
                "abort_event": abort_event,
            }
            req_format = getattr(params, "request_format", None)
            if req_format == Format.text:
                if text_message is None:
                    raise ValueError(
                        "text_message is required when request_format is 'text'"
                    )
                text_bytes = text_message.encode("utf-8")
                request_kwargs["files"] = {
                    "recorded_message": (
                        "message.txt",
                        text_bytes,
                        "text/plain; charset=utf-8",
                    )
                }
            elif req_format == Format.voice:
                if audio_bytes is None or audio_content_type is None:
                    raise ValueError(
                        "audio_bytes and audio_content_type are required when request_format is 'voice'"
                    )
                request_kwargs["content"] = audio_bytes
                request_kwargs.setdefault("headers", {})
                request_kwargs["headers"]["Content-Type"] = audio_content_type
            else:
                raise ValueError("Unsupported or missing request_format in params")

            for line in self._http.stream_lines(
                "POST",
                f"/v1/{self._organization_id}/conversation/{conversation_id}/interact",
                **request_kwargs,
            ):
                yield ConversationInteractWithConversationResponse.model_validate_json(
                    line
                )

        return _iter()

    def finish_conversation(self, conversation_id: str) -> None:
        self._http.request(
            "POST",
            f"/v1/{self._organization_id}/conversation/{conversation_id}/finish/",
        )

    def get_conversations(
        self, params: GetConversationsParametersQuery
    ) -> ConversationGetConversationsResponse:
        response = self._http.request(
            "GET",
            f"/v1/{self._organization_id}/conversation/",
            params=params.model_dump(mode="json", exclude_none=True),
        )
        return ConversationGetConversationsResponse.model_validate_json(response.text)

    def get_conversation_messages(
        self, conversation_id: str, params: GetConversationMessagesParametersQuery
    ) -> ConversationGetConversationMessagesResponse:
        response = self._http.request(
            "GET",
            f"/v1/{self._organization_id}/conversation/{conversation_id}/messages/",
            params=params.model_dump(
                mode="json", exclude_none=True, exclude_defaults=True
            ),
        )
        return ConversationGetConversationMessagesResponse.model_validate_json(
            response.text
        )

    def recommend_responses_for_interaction(
        self, conversation_id: str, interaction_id: str
    ) -> ConversationRecommendResponsesForInteractionResponse:
        response = self._http.request(
            "GET",
            f"/v1/{self._organization_id}/conversation/{conversation_id}/interaction/{interaction_id}/recommend_responses",
        )
        return ConversationRecommendResponsesForInteractionResponse.model_validate_json(
            response.text
        )

    def get_interaction_insights(
        self, conversation_id: str, interaction_id: str
    ) -> ConversationGetInteractionInsightsResponse:
        response = self._http.request(
            "GET",
            f"/v1/{self._organization_id}/conversation/{conversation_id}/interaction/{interaction_id}/insights",
        )
        return ConversationGetInteractionInsightsResponse.model_validate_json(
            response.text
        )

    def get_message_source(
        self, conversation_id: str, message_id: str
    ) -> GetMessageSourceResponse:
        response = self._http.request(
            "GET",
            f"/v1/{self._organization_id}/conversation/{conversation_id}/messages/{message_id}/source",
        )
        return GetMessageSourceResponse.model_validate_json(response.text)

    def generate_conversation_starters(
        self, body: ConversationGenerateConversationStarterRequest
    ) -> ConversationGenerateConversationStarterResponse:
        response = self._http.request(
            "POST",
            f"/v1/{self._organization_id}/conversation/conversation_starter",
            json=body.model_dump(mode="json", exclude_none=True),
        )
        return ConversationGenerateConversationStarterResponse.model_validate_json(
            response.text
        )
