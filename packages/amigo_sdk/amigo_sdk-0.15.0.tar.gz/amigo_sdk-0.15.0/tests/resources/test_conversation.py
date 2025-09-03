import asyncio
import threading

import pytest

from amigo_sdk.config import AmigoConfig
from amigo_sdk.errors import BadRequestError, ConflictError, NotFoundError
from amigo_sdk.generated.model import (
    ConversationCreateConversationRequest,
    ConversationGenerateConversationStarterRequest,
    CreateConversationParametersQuery,
    Format,
    GetConversationMessagesParametersQuery,
    GetConversationsParametersQuery,
    InteractWithConversationParametersQuery,
)
from amigo_sdk.http_client import AmigoAsyncHttpClient, AmigoHttpClient
from amigo_sdk.resources.conversation import (
    AsyncConversationResource,
    ConversationResource,
)

from .helpers import (
    mock_http_request,
    mock_http_request_sync,
    mock_http_stream,
    mock_http_stream_sync,
)

# Readable 24-char hex service ids for tests
TEST_SERVICE_ID = "0123456789abcdef01234567"
TEST_SERVICE_ID_2 = "89abcdef0123456701234567"
TEST_INTERACTION_ID = "fedcba987654321001234567"


@pytest.fixture
def mock_config() -> AmigoConfig:
    return AmigoConfig(
        api_key="test-api-key",
        api_key_id="test-api-key-id",
        user_id="test-user-id",
        organization_id="org-1",
        base_url="https://api.example.com",
    )


@pytest.fixture
def conversation_resource(mock_config: AmigoConfig) -> AsyncConversationResource:
    http_client = AmigoAsyncHttpClient(mock_config)
    return AsyncConversationResource(http_client, mock_config.organization_id)


@pytest.mark.unit
class TestAsyncConversationResourceUnit:
    @pytest.mark.asyncio
    async def test_create_conversation_streams_events_and_yields_ids(
        self, conversation_resource: AsyncConversationResource
    ) -> None:
        async with mock_http_stream(
            [
                {"type": "conversation-created", "conversation_id": "c-1"},
                {
                    "type": "new-message",
                    "message": "hello",
                    "transcript_alignment": [],
                    "message_metadata": [],
                    "stop": True,
                    "sequence_number": 0,
                    "message_id": "m-1",
                },
                {
                    "type": "interaction-complete",
                    "interaction_id": "i-1",
                    "message_id": "m-1",
                    "full_message": "",
                    "conversation_completed": False,
                },
            ]
        ):
            events = await conversation_resource.create_conversation(
                ConversationCreateConversationRequest(
                    service_id=TEST_SERVICE_ID,
                    service_version_set_name="release",
                ),
                CreateConversationParametersQuery(response_format=Format.text),
            )

            saw_new_message = False
            conversation_id = None
            interaction_id = None
            async for resp in events:
                event = resp.root
                if getattr(event, "type", None) == "conversation-created":
                    conversation_id = event.conversation_id
                elif getattr(event, "type", None) == "new-message":
                    saw_new_message = True
                elif getattr(event, "type", None) == "interaction-complete":
                    interaction_id = event.interaction_id
                    break

            assert conversation_id == "c-1"
            assert interaction_id == "i-1"
            assert saw_new_message is True

    @pytest.mark.asyncio
    async def test_create_conversation_sends_body_and_query(
        self, conversation_resource: AsyncConversationResource
    ) -> None:
        body = ConversationCreateConversationRequest(
            service_id=TEST_SERVICE_ID, service_version_set_name="release"
        )
        params = CreateConversationParametersQuery(response_format=Format.text)

        async with mock_http_stream(
            [
                {
                    "type": "interaction-complete",
                    "interaction_id": "i",
                    "message_id": "m",
                    "full_message": "",
                    "conversation_completed": False,
                }
            ]
        ) as tracker:
            events = await conversation_resource.create_conversation(body, params)
            async for _ in events:
                break
            call = tracker["last_call"]
            assert call["method"] == "POST"
            assert call["url"].endswith("/v1/org-1/conversation/")
            assert call["json"]["service_id"] == TEST_SERVICE_ID
            assert call["params"]["response_format"] == "text"

    @pytest.mark.asyncio
    async def test_create_conversation_supports_abort(
        self, conversation_resource: AsyncConversationResource
    ) -> None:
        abort = asyncio.Event()
        abort.set()
        async with mock_http_stream([]):
            events = await conversation_resource.create_conversation(
                ConversationCreateConversationRequest(service_id=TEST_SERVICE_ID),
                CreateConversationParametersQuery(response_format=Format.text),
                abort_event=abort,
            )
            async for _ in events:
                pytest.fail("should not yield when aborted")

    @pytest.mark.asyncio
    async def test_create_conversation_raises_on_non_2xx(
        self, conversation_resource: AsyncConversationResource
    ) -> None:
        async with mock_http_stream([], status_code=400):
            events = await conversation_resource.create_conversation(
                ConversationCreateConversationRequest(service_id=TEST_SERVICE_ID),
                CreateConversationParametersQuery(response_format=Format.text),
            )
            with pytest.raises(BadRequestError):
                async for _ in events:
                    pass

    @pytest.mark.asyncio
    async def test_interact_with_conversation_text_streams_ndjson(
        self, conversation_resource: AsyncConversationResource
    ) -> None:
        async with mock_http_stream(
            [
                {
                    "type": "new-message",
                    "message": "ok",
                    "message_metadata": [],
                    "transcript_alignment": [],
                    "stop": True,
                    "sequence_number": 0,
                    "message_id": "m-2",
                },
                {
                    "type": "interaction-complete",
                    "interaction_id": "i-2",
                    "message_id": "m-2",
                    "full_message": "",
                    "conversation_completed": False,
                },
            ]
        ) as tracker:
            events = await conversation_resource.interact_with_conversation(
                TEST_INTERACTION_ID,
                InteractWithConversationParametersQuery(
                    request_format=Format.text, response_format=Format.text
                ),
                text_message="hello",
            )
            async for _ in events:
                break
            call = tracker["last_call"]
            assert call["url"].endswith(
                f"/v1/org-1/conversation/{TEST_INTERACTION_ID}/interact"
            )
            assert call["params"]["request_format"] == "text"
            assert call["files"]["recorded_message"][2].startswith("text/plain")

            saw_complete = False
            async for resp in events:
                outer = resp.root
                inner = getattr(outer, "root", outer)
                if getattr(inner, "type", None) == "interaction-complete":
                    saw_complete = True
                    break
            assert saw_complete is True

    @pytest.mark.asyncio
    async def test_interact_with_conversation_voice_streaming(
        self, conversation_resource: AsyncConversationResource
    ) -> None:
        audio = b"\x00\x01\x02"
        async with mock_http_stream(
            [
                {
                    "type": "interaction-complete",
                    "interaction_id": "i-3",
                    "message_id": "m-3",
                    "full_message": "",
                    "conversation_completed": False,
                }
            ]
        ) as tracker:
            events = await conversation_resource.interact_with_conversation(
                TEST_INTERACTION_ID,
                InteractWithConversationParametersQuery(
                    request_format=Format.voice, response_format=Format.text
                ),
                audio_bytes=audio,
                audio_content_type="audio/wav",
            )
            async for _ in events:
                break
            call = tracker["last_call"]
            assert call["content"] == audio
            assert call["headers"]["Content-Type"] == "audio/wav"

    @pytest.mark.asyncio
    async def test_interact_with_conversation_supports_abort(
        self, conversation_resource: AsyncConversationResource
    ) -> None:
        abort = asyncio.Event()
        abort.set()
        async with mock_http_stream([]):
            events = await conversation_resource.interact_with_conversation(
                "conv-x",
                InteractWithConversationParametersQuery(
                    request_format=Format.text, response_format=Format.text
                ),
                text_message="hi",
                abort_event=abort,
            )
            async for _ in events:
                pytest.fail("should not yield when aborted")

    @pytest.mark.asyncio
    async def test_interact_with_conversation_raises_on_non_2xx(
        self, conversation_resource: AsyncConversationResource
    ) -> None:
        async with mock_http_stream([], status_code=400):
            events = await conversation_resource.interact_with_conversation(
                "conv-err",
                InteractWithConversationParametersQuery(
                    request_format=Format.text, response_format=Format.text
                ),
                text_message="hi",
            )
            with pytest.raises(BadRequestError):
                async for _ in events:
                    pass

    @pytest.mark.asyncio
    async def test_get_conversations_returns_data_and_passes_query_params(
        self, conversation_resource: AsyncConversationResource
    ) -> None:
        params = GetConversationsParametersQuery(
            service_id=[TEST_SERVICE_ID, TEST_SERVICE_ID_2],
            is_finished=False,
            limit=10,
            continuation_token=5,
            sort_by=["-created_at"],
        )
        async with mock_http_request(
            {"conversations": [], "has_more": False, "continuation_token": None}
        ):
            data = await conversation_resource.get_conversations(params)
            assert data.has_more is False

    @pytest.mark.asyncio
    async def test_get_conversations_raises_not_found(
        self, conversation_resource: AsyncConversationResource
    ) -> None:
        async with mock_http_request("{}", status_code=404):
            with pytest.raises(NotFoundError):
                await conversation_resource.get_conversations(
                    GetConversationsParametersQuery()
                )

    @pytest.mark.asyncio
    async def test_get_conversation_messages_returns_and_pagination(
        self, conversation_resource: AsyncConversationResource
    ) -> None:
        async with mock_http_request(
            {
                "messages": [
                    {
                        "id": "m1",
                        "interaction_id": TEST_INTERACTION_ID,
                        "timestamp": "2024-01-01T00:00:00Z",
                        "created_at": "2024-01-01T00:00:00Z",
                        "sender": "Agent",
                        "message": "Hello",
                        "format": "text",
                        "message_type": "agent-message",
                        "message_metadata": [],
                    }
                ],
                "has_more": False,
                "continuation_token": None,
            }
        ):
            page1 = await conversation_resource.get_conversation_messages(
                "conv-3",
                GetConversationMessagesParametersQuery(
                    limit=1, continuation_token=7, sort_by=["+created_at"]
                ),
            )
            assert len(page1.messages) == 1

    @pytest.mark.asyncio
    async def test_get_conversation_messages_raises_not_found(
        self, conversation_resource: AsyncConversationResource
    ) -> None:
        async with mock_http_request("{}", status_code=404):
            with pytest.raises(NotFoundError):
                await conversation_resource.get_conversation_messages(
                    "missing", GetConversationMessagesParametersQuery()
                )

    @pytest.mark.asyncio
    async def test_finish_conversation_returns_void_on_204(
        self, conversation_resource: AsyncConversationResource
    ) -> None:
        async with mock_http_request("{}", status_code=204):
            await conversation_resource.finish_conversation("conv-4")

    @pytest.mark.asyncio
    async def test_finish_conversation_raises_conflict_on_409(
        self, conversation_resource: AsyncConversationResource
    ) -> None:
        async with mock_http_request("{}", status_code=409):
            with pytest.raises(ConflictError):
                await conversation_resource.finish_conversation("conv-6")

    @pytest.mark.asyncio
    async def test_finish_conversation_raises_not_found_on_404(
        self, conversation_resource: AsyncConversationResource
    ) -> None:
        async with mock_http_request("{}", status_code=404):
            with pytest.raises(NotFoundError):
                await conversation_resource.finish_conversation("missing")

    @pytest.mark.asyncio
    async def test_recommend_responses_returns_data(
        self, conversation_resource: AsyncConversationResource
    ) -> None:
        async with mock_http_request({"recommended_responses": ["hello"]}):
            data = await conversation_resource.recommend_responses_for_interaction(
                "conv-7", "int-1"
            )
            assert isinstance(data.recommended_responses, list)

    @pytest.mark.asyncio
    async def test_recommend_responses_raises_not_found(
        self, conversation_resource: AsyncConversationResource
    ) -> None:
        async with mock_http_request("{}", status_code=404):
            with pytest.raises(NotFoundError):
                await conversation_resource.recommend_responses_for_interaction(
                    "conv-7", "missing"
                )

    @pytest.mark.asyncio
    async def test_get_interaction_insights_returns_data(
        self, conversation_resource: AsyncConversationResource
    ) -> None:
        async with mock_http_request(
            {
                "current_state_name": "Talking",
                "current_state_action": "",
                "current_state_objective": "",
                "state_transition_logs": [],
                "working_memory": [],
                "reflections": [],
                "triggered_dynamic_behavior_set_version_info": None,
            }
        ):
            data = await conversation_resource.get_interaction_insights(
                "conv-8", "int-2"
            )
            assert isinstance(data.current_state_name, str)

    @pytest.mark.asyncio
    async def test_get_interaction_insights_raises_not_found(
        self, conversation_resource: AsyncConversationResource
    ) -> None:
        async with mock_http_request("{}", status_code=404):
            with pytest.raises(NotFoundError):
                await conversation_resource.get_interaction_insights(
                    "conv-8", "missing"
                )

    @pytest.mark.asyncio
    async def test_get_message_source_returns_data(
        self, conversation_resource: AsyncConversationResource
    ) -> None:
        async with mock_http_request(
            {
                "url": "https://example.com/file.wav",
                "expires_at": "2030-01-01T00:00:00Z",
                "content_type": "audio/wav",
            }
        ):
            data = await conversation_resource.get_message_source("conv-9", "msg-1")
            assert str(data.url).startswith("https://")

    @pytest.mark.asyncio
    async def test_get_message_source_raises_not_found(
        self, conversation_resource: AsyncConversationResource
    ) -> None:
        async with mock_http_request("{}", status_code=404):
            with pytest.raises(NotFoundError):
                await conversation_resource.get_message_source("conv-9", "missing")

    @pytest.mark.asyncio
    async def test_generate_conversation_starters_returns_data(
        self, conversation_resource: AsyncConversationResource
    ) -> None:
        async with mock_http_request(
            {"prompts": [{"prompt": "Hi there", "facets": ["greeting"]}]}
        ):
            data = await conversation_resource.generate_conversation_starters(
                ConversationGenerateConversationStarterRequest(
                    service_id=TEST_SERVICE_ID,
                    service_version_set_name="release",
                    facets=["greeting"],
                    min_count=1,
                    max_count=1,
                    generation_instructions="say hi",
                )
            )
            assert len(data.prompts) >= 1

    @pytest.mark.asyncio
    async def test_generate_conversation_starters_raises_on_non_2xx(
        self, conversation_resource: AsyncConversationResource
    ) -> None:
        async with mock_http_request("{}", status_code=400):
            with pytest.raises(BadRequestError):
                await conversation_resource.generate_conversation_starters(
                    ConversationGenerateConversationStarterRequest(
                        service_id=TEST_SERVICE_ID,
                        service_version_set_name="release",
                        facets=["x"],
                        min_count=1,
                        max_count=1,
                        generation_instructions="x",
                    )
                )


@pytest.mark.unit
class TestConversationResourceSync:
    """Sync ConversationResource tests mirroring async coverage."""

    def _resource(self, cfg: AmigoConfig) -> ConversationResource:
        http = AmigoHttpClient(cfg)
        return ConversationResource(http, cfg.organization_id)

    def test_create_conversation_streams_events_and_yields_ids_sync(
        self, mock_config: AmigoConfig
    ) -> None:
        conv = self._resource(mock_config)
        with mock_http_stream_sync(
            [
                {"type": "conversation-created", "conversation_id": "c-1"},
                {
                    "type": "new-message",
                    "message": "hello",
                    "transcript_alignment": [],
                    "message_metadata": [],
                    "stop": True,
                    "sequence_number": 0,
                    "message_id": "m-1",
                },
                {
                    "type": "interaction-complete",
                    "interaction_id": "i-1",
                    "message_id": "m-1",
                    "full_message": "",
                    "conversation_completed": False,
                },
            ]
        ):
            events = conv.create_conversation(
                ConversationCreateConversationRequest(
                    service_id=TEST_SERVICE_ID,
                    service_version_set_name="release",
                ),
                CreateConversationParametersQuery(response_format=Format.text),
            )

            saw_new_message = False
            conversation_id = None
            interaction_id = None
            for resp in events:
                event = resp.root
                if getattr(event, "type", None) == "conversation-created":
                    conversation_id = event.conversation_id
                elif getattr(event, "type", None) == "new-message":
                    saw_new_message = True
                elif getattr(event, "type", None) == "interaction-complete":
                    interaction_id = event.interaction_id
                    break

            assert conversation_id == "c-1"
            assert interaction_id == "i-1"
            assert saw_new_message is True

    def test_create_conversation_sends_body_and_query_sync(
        self, mock_config: AmigoConfig
    ) -> None:
        conv = self._resource(mock_config)
        body = ConversationCreateConversationRequest(
            service_id=TEST_SERVICE_ID, service_version_set_name="release"
        )
        params = CreateConversationParametersQuery(response_format=Format.text)

        with mock_http_stream_sync(
            [
                {
                    "type": "interaction-complete",
                    "interaction_id": "i",
                    "message_id": "m",
                    "full_message": "",
                    "conversation_completed": False,
                }
            ]
        ) as tracker:
            events = conv.create_conversation(body, params)
            next(events)
            call = tracker["last_call"]
            assert call["method"] == "POST"
            assert call["url"].endswith("/v1/org-1/conversation/")
            assert call["json"]["service_id"] == TEST_SERVICE_ID
            assert call["params"]["response_format"] == "text"

    def test_create_conversation_supports_abort_sync(
        self, mock_config: AmigoConfig
    ) -> None:
        conv = self._resource(mock_config)
        abort_event = threading.Event()
        abort_event.set()
        with mock_http_stream_sync([]):
            events = conv.create_conversation(
                ConversationCreateConversationRequest(service_id=TEST_SERVICE_ID),
                CreateConversationParametersQuery(response_format=Format.text),
                abort_event=abort_event,
            )
            for _ in events:
                pytest.fail("should not yield when aborted")

    def test_create_conversation_raises_on_non_2xx_sync(
        self, mock_config: AmigoConfig
    ) -> None:
        conv = self._resource(mock_config)
        with mock_http_stream_sync([], status_code=400):
            events = conv.create_conversation(
                ConversationCreateConversationRequest(service_id=TEST_SERVICE_ID),
                CreateConversationParametersQuery(response_format=Format.text),
            )
            with pytest.raises(BadRequestError):
                list(events)

    def test_interact_with_conversation_text_streams_ndjson_sync(
        self, mock_config: AmigoConfig
    ) -> None:
        conv = self._resource(mock_config)
        with mock_http_stream_sync(
            [
                {
                    "type": "new-message",
                    "message": "ok",
                    "message_metadata": [],
                    "transcript_alignment": [],
                    "stop": True,
                    "sequence_number": 0,
                    "message_id": "m-2",
                },
                {
                    "type": "interaction-complete",
                    "interaction_id": "i-2",
                    "message_id": "m-2",
                    "full_message": "",
                    "conversation_completed": False,
                },
            ]
        ) as tracker:
            events = conv.interact_with_conversation(
                TEST_INTERACTION_ID,
                InteractWithConversationParametersQuery(
                    request_format=Format.text, response_format=Format.text
                ),
                text_message="hello",
            )
            next(events)
            call = tracker["last_call"]
            assert call["url"].endswith(
                f"/v1/org-1/conversation/{TEST_INTERACTION_ID}/interact"
            )
            assert call["params"]["request_format"] == "text"
            assert call["files"]["recorded_message"][2].startswith("text/plain")

            saw_complete = False
            for resp in events:
                outer = resp.root
                inner = getattr(outer, "root", outer)
                if getattr(inner, "type", None) == "interaction-complete":
                    saw_complete = True
                    break
            assert saw_complete is True

    def test_interact_with_conversation_voice_streaming_sync(
        self, mock_config: AmigoConfig
    ) -> None:
        conv = self._resource(mock_config)
        audio = b"\x00\x01\x02"
        with mock_http_stream_sync(
            [
                {
                    "type": "interaction-complete",
                    "interaction_id": "i-3",
                    "message_id": "m-3",
                    "full_message": "",
                    "conversation_completed": False,
                }
            ]
        ) as tracker:
            events = conv.interact_with_conversation(
                TEST_INTERACTION_ID,
                InteractWithConversationParametersQuery(
                    request_format=Format.voice, response_format=Format.text
                ),
                audio_bytes=audio,
                audio_content_type="audio/wav",
            )
            next(events)
            call = tracker["last_call"]
            assert call["content"] == audio
            assert call["headers"]["Content-Type"] == "audio/wav"

    def test_interact_with_conversation_supports_abort_sync(
        self, mock_config: AmigoConfig
    ) -> None:
        conv = self._resource(mock_config)
        abort_event = threading.Event()
        abort_event.set()
        with mock_http_stream_sync([]):
            events = conv.interact_with_conversation(
                "conv-x",
                InteractWithConversationParametersQuery(
                    request_format=Format.text, response_format=Format.text
                ),
                text_message="hi",
                abort_event=abort_event,
            )
            for _ in events:
                pytest.fail("should not yield when aborted")

    def test_interact_with_conversation_raises_on_non_2xx_sync(
        self, mock_config: AmigoConfig
    ) -> None:
        conv = self._resource(mock_config)
        with mock_http_stream_sync([], status_code=400):
            events = conv.interact_with_conversation(
                "conv-err",
                InteractWithConversationParametersQuery(
                    request_format=Format.text, response_format=Format.text
                ),
                text_message="hi",
            )
            with pytest.raises(BadRequestError):
                list(events)

    def test_get_conversations_returns_data_and_passes_query_params_sync(
        self, mock_config: AmigoConfig
    ) -> None:
        conv = self._resource(mock_config)
        params = GetConversationsParametersQuery(
            service_id=[TEST_SERVICE_ID, TEST_SERVICE_ID_2],
            is_finished=False,
            limit=10,
            continuation_token=5,
            sort_by=["-created_at"],
        )
        with mock_http_request_sync(
            {"conversations": [], "has_more": False, "continuation_token": None}
        ):
            data = conv.get_conversations(params)
            assert data.has_more is False

    def test_get_conversations_raises_not_found_sync(
        self, mock_config: AmigoConfig
    ) -> None:
        conv = self._resource(mock_config)
        with mock_http_request_sync("{}", status_code=404):
            with pytest.raises(NotFoundError):
                conv.get_conversations(GetConversationsParametersQuery())

    def test_get_conversation_messages_returns_and_pagination_sync(
        self, mock_config: AmigoConfig
    ) -> None:
        conv = self._resource(mock_config)
        with mock_http_request_sync(
            {
                "messages": [
                    {
                        "id": "m1",
                        "interaction_id": TEST_INTERACTION_ID,
                        "timestamp": "2024-01-01T00:00:00Z",
                        "created_at": "2024-01-01T00:00:00Z",
                        "sender": "Agent",
                        "message": "Hello",
                        "format": "text",
                        "message_type": "agent-message",
                        "message_metadata": [],
                    }
                ],
                "has_more": False,
                "continuation_token": None,
            }
        ):
            page1 = conv.get_conversation_messages(
                "conv-3",
                GetConversationMessagesParametersQuery(
                    limit=1, continuation_token=7, sort_by=["+created_at"]
                ),
            )
            assert len(page1.messages) == 1

    def test_get_conversation_messages_raises_not_found_sync(
        self, mock_config: AmigoConfig
    ) -> None:
        conv = self._resource(mock_config)
        with mock_http_request_sync("{}", status_code=404):
            with pytest.raises(NotFoundError):
                conv.get_conversation_messages(
                    "missing", GetConversationMessagesParametersQuery()
                )

    def test_finish_conversation_returns_void_on_204_sync(
        self, mock_config: AmigoConfig
    ) -> None:
        conv = self._resource(mock_config)
        with mock_http_request_sync("{}", status_code=204):
            assert conv.finish_conversation("conv-4") is None

    def test_finish_conversation_raises_conflict_on_409_sync(
        self, mock_config: AmigoConfig
    ) -> None:
        conv = self._resource(mock_config)
        with mock_http_request_sync("{}", status_code=409):
            with pytest.raises(ConflictError):
                conv.finish_conversation("conv-6")

    def test_finish_conversation_raises_not_found_on_404_sync(
        self, mock_config: AmigoConfig
    ) -> None:
        conv = self._resource(mock_config)
        with mock_http_request_sync("{}", status_code=404):
            with pytest.raises(NotFoundError):
                conv.finish_conversation("missing")

    def test_recommend_responses_returns_data_sync(
        self, mock_config: AmigoConfig
    ) -> None:
        conv = self._resource(mock_config)
        with mock_http_request_sync({"recommended_responses": ["hello"]}):
            data = conv.recommend_responses_for_interaction("conv-7", "int-1")
            assert isinstance(data.recommended_responses, list)

    def test_recommend_responses_raises_not_found_sync(
        self, mock_config: AmigoConfig
    ) -> None:
        conv = self._resource(mock_config)
        with mock_http_request_sync("{}", status_code=404):
            with pytest.raises(NotFoundError):
                conv.recommend_responses_for_interaction("conv-7", "missing")

    def test_get_interaction_insights_returns_data_sync(
        self, mock_config: AmigoConfig
    ) -> None:
        conv = self._resource(mock_config)
        with mock_http_request_sync(
            {
                "current_state_name": "Talking",
                "current_state_action": "",
                "current_state_objective": "",
                "state_transition_logs": [],
                "working_memory": [],
                "reflections": [],
                "triggered_dynamic_behavior_set_version_info": None,
            }
        ):
            data = conv.get_interaction_insights("conv-8", "int-2")
            assert isinstance(data.current_state_name, str)

    def test_get_interaction_insights_raises_not_found_sync(
        self, mock_config: AmigoConfig
    ) -> None:
        conv = self._resource(mock_config)
        with mock_http_request_sync("{}", status_code=404):
            with pytest.raises(NotFoundError):
                conv.get_interaction_insights("conv-8", "missing")

    def test_get_message_source_returns_data_sync(
        self, mock_config: AmigoConfig
    ) -> None:
        conv = self._resource(mock_config)
        with mock_http_request_sync(
            {
                "url": "https://example.com/file.wav",
                "expires_at": "2030-01-01T00:00:00Z",
                "content_type": "audio/wav",
            }
        ):
            data = conv.get_message_source("conv-9", "msg-1")
            assert str(data.url).startswith("https://")

    def test_get_message_source_raises_not_found_sync(
        self, mock_config: AmigoConfig
    ) -> None:
        conv = self._resource(mock_config)
        with mock_http_request_sync("{}", status_code=404):
            with pytest.raises(NotFoundError):
                conv.get_message_source("conv-9", "missing")

    def test_generate_conversation_starters_returns_data_sync(
        self, mock_config: AmigoConfig
    ) -> None:
        conv = self._resource(mock_config)
        with mock_http_request_sync(
            {"prompts": [{"prompt": "Hi there", "facets": ["greeting"]}]}
        ):
            data = conv.generate_conversation_starters(
                ConversationGenerateConversationStarterRequest(
                    service_id=TEST_SERVICE_ID,
                    service_version_set_name="release",
                    facets=["greeting"],
                    min_count=1,
                    max_count=1,
                    generation_instructions="say hi",
                )
            )
            assert len(data.prompts) >= 1

    def test_generate_conversation_starters_raises_on_non_2xx_sync(
        self, mock_config: AmigoConfig
    ) -> None:
        conv = self._resource(mock_config)
        with mock_http_request_sync("{}", status_code=400):
            with pytest.raises(BadRequestError):
                conv.generate_conversation_starters(
                    ConversationGenerateConversationStarterRequest(
                        service_id=TEST_SERVICE_ID,
                        service_version_set_name="release",
                        facets=["x"],
                        min_count=1,
                        max_count=1,
                        generation_instructions="x",
                    )
                )
