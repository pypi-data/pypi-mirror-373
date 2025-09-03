import asyncio
import os
from collections.abc import AsyncGenerator

import pytest

from amigo_sdk.errors import ConflictError, NotFoundError
from amigo_sdk.generated.model import (
    ConversationCreateConversationRequest,
    ConversationCreatedEvent,
    CreateConversationParametersQuery,
    ErrorEvent,
    GetConversationMessagesParametersQuery,
    GetConversationsParametersQuery,
    InteractionCompleteEvent,
    InteractWithConversationParametersQuery,
    NewMessageEvent,
)
from amigo_sdk.sdk_client import AmigoClient, AsyncAmigoClient

# Constants
SERVICE_ID = os.getenv("AMIGO_TEST_SERVICE_ID", "689b81e7afdaf934f4b48f81")


@pytest.fixture(scope="module", autouse=True)
async def pre_suite_cleanup() -> AsyncGenerator[None, None]:
    # Ensure env loaded and client can connect; verify service exists
    async with AsyncAmigoClient() as client:
        try:
            from amigo_sdk.generated.model import GetServicesParametersQuery

            services = await client.service.get_services(
                GetServicesParametersQuery(id=[SERVICE_ID])
            )
            service_ids = [
                getattr(s, "id", None) for s in getattr(services, "services", [])
            ]
            if service_ids and SERVICE_ID not in service_ids:
                pytest.skip(f"Service {SERVICE_ID} not found for this organization")
        except Exception:
            # If listing services fails, let tests surface the issue later
            pass

        # Finish any ongoing conversations for this service (best-effort)
        try:
            convs = await client.conversation.get_conversations(
                GetConversationsParametersQuery(
                    service_id=[SERVICE_ID],
                    is_finished=False,
                    limit=25,
                    sort_by=["-created_at"],
                )
            )
            for c in getattr(convs, "conversations", []) or []:
                try:
                    await client.conversation.finish_conversation(c.id)
                except Exception:
                    pass
        except Exception:
            pass

    # Allow eventual consistency to settle
    await asyncio.sleep(0.5)
    yield


@pytest.mark.integration
class TestConversationIntegration:
    conversation_id: str | None = None
    interaction_id: str | None = None

    async def test_create_conversation_streams_and_returns_ids(self):
        async with AsyncAmigoClient() as client:
            events = await client.conversation.create_conversation(
                body=ConversationCreateConversationRequest(
                    service_id=SERVICE_ID,
                    service_version_set_name="release",
                ),
                params=CreateConversationParametersQuery(response_format="text"),
            )

            saw_new_message = False

            async for resp in events:
                event = resp.root
                if isinstance(event, ErrorEvent):
                    pytest.fail(f"error event: {event.model_dump_json()}")
                if isinstance(event, ConversationCreatedEvent):
                    type(self).conversation_id = event.conversation_id
                    assert isinstance(type(self).conversation_id, str)
                elif isinstance(event, NewMessageEvent):
                    saw_new_message = True
                elif isinstance(event, InteractionCompleteEvent):
                    type(self).interaction_id = event.interaction_id
                    assert isinstance(type(self).interaction_id, str)
                    break

            assert type(self).conversation_id is not None
            assert type(self).interaction_id is not None
            assert saw_new_message is True

    async def test_recommend_responses_returns_suggestions(self):
        assert type(self).conversation_id is not None
        assert type(self).interaction_id is not None

        async with AsyncAmigoClient() as client:
            recs = await client.conversation.recommend_responses_for_interaction(
                type(self).conversation_id, type(self).interaction_id
            )

            assert recs is not None
            assert isinstance(getattr(recs, "recommended_responses", None), list)

    async def test_get_conversations_filter_by_id(self):
        assert type(self).conversation_id is not None

        async with AsyncAmigoClient() as client:
            resp = await client.conversation.get_conversations(
                GetConversationsParametersQuery(id=[type(self).conversation_id])
            )

            assert resp is not None
            ids = [c.id for c in getattr(resp, "conversations", [])]
            assert type(self).conversation_id in ids

    async def test_interact_with_conversation_text_streams(self):
        assert type(self).conversation_id is not None

        async with AsyncAmigoClient() as client:
            events = await client.conversation.interact_with_conversation(
                type(self).conversation_id,
                params=InteractWithConversationParametersQuery(
                    request_format="text", response_format="text"
                ),
                text_message="Hello, I'm sending a text message from the Python SDK asynchronously!",
            )

            saw_new_message = False
            saw_interaction_complete = False
            latest_interaction_id: str | None = None

            async for evt in events:
                e = evt.root
                if isinstance(e, ErrorEvent):
                    pytest.fail(f"error event: {e.model_dump_json()}")
                if isinstance(e, NewMessageEvent):
                    saw_new_message = True
                elif isinstance(e, InteractionCompleteEvent):
                    saw_interaction_complete = True
                    latest_interaction_id = e.interaction_id
                    break

            assert saw_new_message is True
            assert saw_interaction_complete is True
            if latest_interaction_id:
                type(self).interaction_id = latest_interaction_id

    async def test_get_conversation_messages_pagination(self):
        assert type(self).conversation_id is not None

        async with AsyncAmigoClient() as client:
            page1 = await client.conversation.get_conversation_messages(
                type(self).conversation_id,
                GetConversationMessagesParametersQuery(
                    limit=1, sort_by=["+created_at"]
                ),
            )
            assert page1 is not None
            assert isinstance(getattr(page1, "messages", None), list)
            assert len(page1.messages) == 1
            assert isinstance(page1.has_more, bool)

            if page1.has_more:
                assert page1.continuation_token is not None
                page2 = await client.conversation.get_conversation_messages(
                    type(self).conversation_id,
                    GetConversationMessagesParametersQuery(
                        limit=1,
                        continuation_token=page1.continuation_token,
                        sort_by=["+created_at"],
                    ),
                )
                assert page2 is not None
                assert isinstance(getattr(page2, "messages", None), list)
                assert len(page2.messages) == 1

    async def test_get_interaction_insights_returns_data(self):
        assert type(self).conversation_id is not None
        assert type(self).interaction_id is not None

        async with AsyncAmigoClient() as client:
            insights = await client.conversation.get_interaction_insights(
                type(self).conversation_id, type(self).interaction_id
            )
            assert insights is not None
            assert isinstance(getattr(insights, "current_state_name", None), str)

    async def test_finish_conversation_returns_acceptable_outcome(self):
        assert type(self).conversation_id is not None

        async with AsyncAmigoClient() as client:
            try:
                await client.conversation.finish_conversation(
                    type(self).conversation_id
                )
            except Exception as e:
                # Accept eventual-consistency errors
                assert isinstance(e, (ConflictError, NotFoundError))


@pytest.mark.integration
class TestConversationIntegrationSync:
    conversation_id: str | None = None
    interaction_id: str | None = None

    def test_create_conversation_streams_and_returns_ids(self):
        with AmigoClient() as client:
            events = client.conversation.create_conversation(
                body=ConversationCreateConversationRequest(
                    service_id=SERVICE_ID,
                    service_version_set_name="release",
                ),
                params=CreateConversationParametersQuery(response_format="text"),
            )

            saw_new_message = False

            for resp in events:
                event = resp.root
                if isinstance(event, ErrorEvent):
                    pytest.fail(f"error event: {event.model_dump_json()}")
                if isinstance(event, ConversationCreatedEvent):
                    type(self).conversation_id = event.conversation_id
                    assert isinstance(type(self).conversation_id, str)
                elif isinstance(event, NewMessageEvent):
                    saw_new_message = True
                elif isinstance(event, InteractionCompleteEvent):
                    type(self).interaction_id = event.interaction_id
                    assert isinstance(type(self).interaction_id, str)
                    break

            assert type(self).conversation_id is not None
            assert type(self).interaction_id is not None
            assert saw_new_message is True

    def test_recommend_responses_returns_suggestions(self):
        assert type(self).conversation_id is not None
        assert type(self).interaction_id is not None

        with AmigoClient() as client:
            recs = client.conversation.recommend_responses_for_interaction(
                type(self).conversation_id, type(self).interaction_id
            )

            assert recs is not None
            assert isinstance(getattr(recs, "recommended_responses", None), list)

    def test_get_conversations_filter_by_id(self):
        assert type(self).conversation_id is not None

        with AmigoClient() as client:
            resp = client.conversation.get_conversations(
                GetConversationsParametersQuery(id=[type(self).conversation_id])
            )

            assert resp is not None
            ids = [c.id for c in getattr(resp, "conversations", [])]
            assert type(self).conversation_id in ids

    def test_interact_with_conversation_text_streams(self):
        assert type(self).conversation_id is not None

        with AmigoClient() as client:
            events = client.conversation.interact_with_conversation(
                type(self).conversation_id,
                params=InteractWithConversationParametersQuery(
                    request_format="text", response_format="text"
                ),
                text_message="Hello, I'm sending a text message from the Python SDK synchronously!",
            )

            saw_new_message = False
            saw_interaction_complete = False
            latest_interaction_id: str | None = None

            for evt in events:
                e = evt.root
                if isinstance(e, ErrorEvent):
                    pytest.fail(f"error event: {e.model_dump_json()}")
                if isinstance(e, NewMessageEvent):
                    saw_new_message = True
                elif isinstance(e, InteractionCompleteEvent):
                    saw_interaction_complete = True
                    latest_interaction_id = e.interaction_id
                    break

            assert saw_new_message is True
            assert saw_interaction_complete is True
            if latest_interaction_id:
                type(self).interaction_id = latest_interaction_id

    def test_get_conversation_messages_pagination(self):
        assert type(self).conversation_id is not None

        with AmigoClient() as client:
            page1 = client.conversation.get_conversation_messages(
                type(self).conversation_id,
                GetConversationMessagesParametersQuery(
                    limit=1, sort_by=["+created_at"]
                ),
            )
            assert page1 is not None
            assert isinstance(getattr(page1, "messages", None), list)
            assert len(page1.messages) == 1
            assert isinstance(page1.has_more, bool)

            if page1.has_more:
                assert page1.continuation_token is not None
                page2 = client.conversation.get_conversation_messages(
                    type(self).conversation_id,
                    GetConversationMessagesParametersQuery(
                        limit=1,
                        continuation_token=page1.continuation_token,
                        sort_by=["+created_at"],
                    ),
                )
                assert page2 is not None
                assert isinstance(getattr(page2, "messages", None), list)
                assert len(page2.messages) == 1

    def test_get_interaction_insights_returns_data(self):
        assert type(self).conversation_id is not None
        assert type(self).interaction_id is not None

        with AmigoClient() as client:
            insights = client.conversation.get_interaction_insights(
                type(self).conversation_id, type(self).interaction_id
            )
            assert insights is not None
            assert isinstance(getattr(insights, "current_state_name", None), str)

    def test_finish_conversation_returns_acceptable_outcome(self):
        assert type(self).conversation_id is not None

        with AmigoClient() as client:
            try:
                client.conversation.finish_conversation(type(self).conversation_id)
            except Exception as e:
                assert isinstance(e, (ConflictError, NotFoundError))
