"""Integration tests for AssistantService."""

import os
import uuid
from datetime import datetime

import pytest

from codemie_sdk import CodeMieClient
from codemie_sdk.models.assistant import (
    AssistantBase,
    Assistant,
    AssistantCreateRequest,
    AssistantUpdateRequest,
    AssistantEvaluationRequest,
    ToolKitDetails,
    ToolDetails,
    AssistantChatRequest,
    ChatMessage,
    ChatRole,
    BaseModelResponse,
)
from codemie_test_harness.tests import PROJECT, LANGFUSE_TRACES_ENABLED
from codemie_test_harness.tests.utils.base_utils import get_random_name


def test_get_tools(client: CodeMieClient):
    """Test successful retrieval of available tools."""
    # Get tools
    toolkits = client.assistants.get_tools()

    # Verify response structure
    assert isinstance(toolkits, list)
    assert len(toolkits) > 0

    # Verify toolkit structure
    toolkit = toolkits[0]
    assert isinstance(toolkit, ToolKitDetails)
    assert hasattr(toolkit, "toolkit")
    assert hasattr(toolkit, "tools")
    assert isinstance(toolkit.tools, list)

    # Verify tools have required fields
    if toolkit.tools:
        tool = toolkit.tools[0]
        assert isinstance(tool, ToolDetails)
        assert hasattr(tool, "name")
        assert hasattr(tool, "label")
        assert isinstance(tool.settings_config, bool)


def test_get_tools_invalid_token():
    """Test tools retrieval with invalid token."""
    with pytest.raises(Exception):
        invalid_client = CodeMieClient(
            auth_server_url=os.getenv("AUTH_SERVER_URL"),
            auth_client_id=os.getenv("AUTH_CLIENT_ID"),
            auth_client_secret=os.getenv("AUTH_CLIENT_SECRET"),
            auth_realm_name=os.getenv("AUTH_REALM_NAME"),
            codemie_api_domain=os.getenv("CODEMIE_API_DOMAIN"),
            verify_ssl=os.getenv("VERIFY_SSL").lower() == "true",
            username="invalid",
            password="invalid",
        )
        invalid_client.assistants.get_tools()


def test_list_assistants_minimal(client: CodeMieClient):
    """Test listing assistants with minimal response."""
    # Get list of assistants with minimal response (default)
    assistants = client.assistants.list()

    # Verify we got a list of assistants
    assert isinstance(assistants, list)
    assert len(assistants) > 0

    # Verify each assistant has the correct type and required fields
    for assistant in assistants:
        assert isinstance(assistant, AssistantBase)
        assert assistant.id
        assert assistant.name
        assert assistant.description


def test_list_assistants_full(client: CodeMieClient):
    """Test listing assistants with full response."""
    # Get list of assistants with full response
    assistants = client.assistants.list(minimal_response=False)

    # Verify we got a list of assistants
    assert isinstance(assistants, list)
    assert len(assistants) > 0

    # Verify each assistant has the correct type and required fields
    for assistant in assistants:
        assert isinstance(assistant, Assistant)
        assert assistant.id
        assert assistant.name
        assert assistant.description
        assert assistant.system_prompt is not None
        assert assistant.project is not None
        # disabled LLM verification for now because A2A assistants have None
        # assert assistant.llm_model_type is not None
        assert isinstance(assistant.shared, bool)
        assert isinstance(assistant.is_react, bool)
        assert isinstance(assistant.is_global, bool)
        assert assistant.created_date is not None
        assert assistant.creator is not None
        assert isinstance(assistant.user_abilities, list)

        # Verify nested structures
        assert isinstance(assistant.toolkits, list)
        assert isinstance(assistant.context, list)
        assert isinstance(assistant.system_prompt_history, list)
        assert isinstance(assistant.user_prompts, list)

        # Verify creator structure if present
        if assistant.created_by:
            assert assistant.created_by.user_id is not None
            assert assistant.created_by.username is not None
            assert assistant.created_by.name is not None

        # Verify date fields format
        assert isinstance(assistant.created_date, datetime)


def test_list_assistants_with_filters(client: CodeMieClient):
    """Test listing assistants with filters."""
    # Get list of assistants with filters
    filters = {"project": PROJECT, "shared": False}
    assistants = client.assistants.list(minimal_response=False, filters=filters)

    # Verify we got a list of assistants
    assert isinstance(assistants, list)

    # Verify each assistant matches the filter criteria
    for assistant in assistants:
        assert assistant.project == PROJECT
        assert assistant.shared is False


def test_list_assistants_pagination(client: CodeMieClient):
    """Test assistant listing with pagination."""
    # Get first page with 5 items
    page_1 = client.assistants.list(page=0, per_page=5)
    assert len(page_1) <= 5

    # Get second page with 5 items
    page_2 = client.assistants.list(page=1, per_page=5)
    assert len(page_2) <= 5

    # Verify pages contain different assistants
    if page_2:  # Only if there are items on second page
        assert page_1[0].id != page_2[0].id


def test_list_assistants_scope(client: CodeMieClient):
    """Test assistant listing with different scopes."""
    # Test visible_to_user scope
    visible_assistants = client.assistants.list(scope="visible_to_user")
    assert isinstance(visible_assistants, list)

    # Test created_by_user scope
    created_assistants = client.assistants.list(scope="created_by_user")
    assert isinstance(created_assistants, list)


def test_get_assistant(client: CodeMieClient):
    """Test getting a specific assistant by ID."""
    # First, get a list of assistants to get a valid ID
    assistants = client.assistants.list()
    assert len(assistants) > 0
    test_assistant_id = assistants[0].id

    # Get the specific assistant
    assistant = client.assistants.get(test_assistant_id)

    # Verify the response type and essential fields
    assert isinstance(assistant, Assistant)
    assert assistant.id == test_assistant_id
    assert assistant.name is not None
    assert assistant.description is not None
    assert assistant.system_prompt is not None
    assert assistant.project is not None

    # Verify required structures
    assert isinstance(assistant.toolkits, list)
    assert isinstance(assistant.context, list)
    assert isinstance(assistant.system_prompt_history, list)
    assert isinstance(assistant.user_prompts, list)

    # Verify boolean fields
    assert isinstance(assistant.shared, bool)
    assert isinstance(assistant.is_react, bool)
    assert isinstance(assistant.is_global, bool)

    # Verify date fields
    assert isinstance(assistant.created_date, datetime)


@pytest.mark.skip(reason="Need to fix API to return 404")
def test_get_assistant_not_found(client: CodeMieClient):
    """Test getting a non-existent assistant."""
    with pytest.raises(Exception) as exc_info:
        client.assistants.get("1234")
    assert "Service Unavailable" in str(exc_info.value).lower() or "503" in str(
        exc_info.value
    )


def test_get_assistant_by_slug(client: CodeMieClient, default_llm):
    """Test getting an assistant by slug."""
    # Step 1: Get available toolkits and tools for assistant creation
    toolkits = client.assistants.get_tools()
    assert len(toolkits) > 0, "At least one toolkit is required for testing"

    first_toolkit = toolkits[0]
    assert len(first_toolkit.tools) > 0, "No tools in the first toolkit"
    first_tool = first_toolkit.tools[0]

    # Step 2: Create assistant with a specific slug
    assistant_project = PROJECT
    test_slug = get_random_name()
    assistant_name = get_random_name()

    create_request = AssistantCreateRequest(
        name=assistant_name,
        slug=test_slug,  # Set specific slug for testing
        description="Test assistant for slug retrieval",
        system_prompt="You are a helpful test assistant",
        llm_model_type=default_llm.base_name,
        project=assistant_project,
        toolkits=[
            ToolKitDetails(
                toolkit=first_toolkit.toolkit, tools=[ToolDetails(name=first_tool.name)]
            )
        ],
    )

    # Create the assistant
    created = client.assistants.create(create_request)
    assert created is not None, "Failed to create test assistant"

    try:
        # Step 3: Get assistant by slug
        retrieved = client.assistants.get_by_slug(test_slug)

        # Step 4: Verify retrieved assistant
        assert retrieved is not None, "Retrieved assistant is None"
        assert isinstance(retrieved, Assistant), "Retrieved object is not an Assistant"
        assert retrieved.slug == test_slug, "Retrieved assistant has incorrect slug"
        assert retrieved.name == assistant_name, (
            "Retrieved assistant has incorrect name"
        )
        assert retrieved.description == "Test assistant for slug retrieval"
        assert retrieved.project == assistant_project

        # Verify required structures
        assert isinstance(retrieved.toolkits, list)
        assert len(retrieved.toolkits) > 0
        assert retrieved.toolkits[0].toolkit == first_toolkit.toolkit
        assert retrieved.toolkits[0].tools[0].name == first_tool.name

        # Verify other fields
        assert isinstance(retrieved.created_date, datetime)
        assert isinstance(retrieved.shared, bool)
        assert isinstance(retrieved.is_react, bool)
        assert retrieved.system_prompt is not None

    finally:
        # Step 5: Clean up - delete created assistant
        try:
            client.assistants.delete(retrieved.id)

            # Verify deletion - try to get by slug should fail
            with pytest.raises(Exception) as exc_info:
                client.assistants.get_by_slug(test_slug)
            assert (
                "404" in str(exc_info.value)
                or "not found" in str(exc_info.value).lower()
            )

        except Exception as e:
            pytest.fail(f"Failed to clean up assistant: {str(e)}")


def test_get_assistant_by_slug_not_found(client: CodeMieClient):
    """Test getting a non-existent assistant by slug."""
    with pytest.raises(Exception) as exc_info:
        client.assistants.get_by_slug("non-existent-assistant-slug")
    assert "404" in str(exc_info.value) or "not found" in str(exc_info.value).lower()


def test_assistant_lifecycle(client: CodeMieClient, default_llm):
    """Test full assistant lifecycle: get tools, create, update, and delete assistant."""
    # Step 1: Get available toolkits and tools
    toolkits = client.assistants.get_tools()
    assert len(toolkits) >= 2, "At least two toolkits are required for testing"

    # Get first toolkit and its first tool for initial creation
    first_toolkit = toolkits[0]
    assert len(first_toolkit.tools) > 0, "No tools in the first toolkit"
    first_tool = first_toolkit.tools[0]

    # Get second toolkit and its tool for update
    second_toolkit = toolkits[1]
    assert len(second_toolkit.tools) > 0, "No tools in the second toolkit"
    second_tool = second_toolkit.tools[0]

    # Step 2: Create assistant with first toolkit/tool
    assistant_project = PROJECT
    assistant_name = get_random_name()
    request = AssistantCreateRequest(
        name=assistant_name,
        slug=assistant_name,
        description="Integration test assistant",
        system_prompt="You are a helpful integration test assistant",
        llm_model_type=default_llm.base_name,
        project=assistant_project,
        toolkits=[
            ToolKitDetails(
                toolkit=first_toolkit.toolkit, tools=[ToolDetails(name=first_tool.name)]
            )
        ],
    )

    # Create assistant
    created = client.assistants.create(request)
    assert created is not None

    # Step 3: Verify assistant exists in the list
    filters = {"project": assistant_project, "shared": False}
    assistants = client.assistants.list(minimal_response=True, filters=filters)
    found_assistant = next((a for a in assistants if a.name == assistant_name), None)
    assert found_assistant is not None, (
        f"Created assistant '{assistant_name}' not found in list"
    )

    # Step 4: Update the assistant with second toolkit/tool
    updated_name = f"{assistant_name} Updated"
    update_request = AssistantUpdateRequest(
        name=updated_name,
        description=f"{updated_name} description",
        system_prompt="You are an updated integration test assistant",
        llm_model_type=default_llm.base_name,
        toolkits=[
            ToolKitDetails(
                toolkit=second_toolkit.toolkit,
                tools=[ToolDetails(name=second_tool.name)],
            )
        ],
        project=assistant_project,
        is_react=True,
        shared=False,
    )

    updated = client.assistants.update(found_assistant.id, update_request)
    assert updated is not None

    # Verify update in the list
    assistants_after_update = client.assistants.list(
        minimal_response=False, filters=filters
    )
    found_updated = next(
        (a for a in assistants_after_update if a.id == found_assistant.id), None
    )
    assert found_updated is not None
    assert found_updated.name == f"{assistant_name} Updated"
    assert found_updated.description == f"{updated_name} description"
    assert (
        found_updated.system_prompt == "You are an updated integration test assistant"
    )
    assert found_updated.llm_model_type == default_llm.base_name
    assert found_updated.toolkits[0].toolkit == second_toolkit.toolkit
    assert found_updated.toolkits[0].tools[0].name == second_tool.name

    # Step 5: Clean up - delete created assistant
    try:
        client.assistants.delete(found_updated.id)

        # Verify deletion
        assistants_after = client.assistants.list(
            minimal_response=False, filters=filters
        )
        assert not any(
            a.name == f"{assistant_name} Updated" for a in assistants_after
        ), f"Assistant '{assistant_name} Updated' still exists after deletion"
    except Exception as e:
        pytest.fail(f"Failed to clean up assistant: {str(e)}")


def test_assistant_chat(client: CodeMieClient, default_llm):
    """Test full assistant lifecycle with chat functionality."""
    # Step 1: Get available toolkits and tools
    toolkits = client.assistants.get_tools()
    assert len(toolkits) > 0, "At least one toolkit is required for testing"

    # Get first toolkit and its first tool
    first_toolkit = toolkits[0]
    assert len(first_toolkit.tools) > 0, "No tools in the first toolkit"
    first_tool = first_toolkit.tools[0]

    # Step 2: Create assistant
    assistant_project = PROJECT
    assistant_name = get_random_name()
    request = AssistantCreateRequest(
        name=assistant_name,
        slug=assistant_name,
        description="Integration test assistant for chat",
        system_prompt="You are a helpful integration test assistant. Always respond with 'Test response: ' prefix.",
        llm_model_type=default_llm.base_name,
        project=assistant_project,
        toolkits=[
            ToolKitDetails(
                toolkit=first_toolkit.toolkit, tools=[ToolDetails(name=first_tool.name)]
            )
        ],
    )

    # Create assistant
    created = client.assistants.create(request)
    assert created is not None

    # Step 3: Find assistant in the list
    filters = {"project": assistant_project, "shared": False}
    assistants = client.assistants.list(minimal_response=True, filters=filters)
    found_assistant = next((a for a in assistants if a.name == assistant_name), None)
    assert found_assistant is not None, (
        f"Created assistant '{assistant_name}' not found in list"
    )

    try:
        # Step 4: Test chat functionality
        chat_request = AssistantChatRequest(
            text="Hello, this is a test message",
            conversation_id=str(uuid.uuid4()),
            history=[
                ChatMessage(role=ChatRole.USER, message="Hi there"),
                ChatMessage(
                    role=ChatRole.ASSISTANT, message="Hello! How can I help you?"
                ),
            ],
            stream=False,
            metadata={"langfuse_traces_enabled": LANGFUSE_TRACES_ENABLED},
        )

        # Send chat request
        response = client.assistants.chat(
            assistant_id=found_assistant.id, request=chat_request
        )

        # Verify response
        assert response is not None
        assert isinstance(response, BaseModelResponse)
        assert response.generated is not None
        assert response.generated.startswith("Test response:")
        assert response.time_elapsed is not None
        assert response.tokens_used is None

        # Test streaming chat
        stream_request = AssistantChatRequest(
            text="Hello, this is a streaming test",
            conversation_id=str(uuid.uuid4()),
            stream=True,
            metadata={"langfuse_traces_enabled": LANGFUSE_TRACES_ENABLED},
        )

        # Send streaming chat request
        stream_response = client.assistants.chat(
            assistant_id=found_assistant.id, request=stream_request
        )

        # Verify streaming response
        received_chunks = []
        for chunk in stream_response:
            assert chunk is not None
            received_chunks.append(chunk)
        assert len(received_chunks) > 0
    finally:
        # Clean up - delete created assistant
        try:
            client.assistants.delete(found_assistant.id)

            # Verify deletion
            assistants_after = client.assistants.list(
                minimal_response=False, filters=filters
            )
            assert not any(a.name == assistant_name for a in assistants_after), (
                f"Assistant '{assistant_name}' still exists after deletion"
            )
        except Exception as e:
            pytest.fail(f"Failed to clean up assistant: {str(e)}")


def test_get_prebuilt_assistants(client: CodeMieClient):
    """Test getting prebuilt assistants and verification by slug."""
    # Step 1: Get list of prebuilt assistants
    prebuilt_assistants = client.assistants.get_prebuilt()

    # Verify we have prebuilt assistants
    assert isinstance(prebuilt_assistants, list)
    assert len(prebuilt_assistants) > 0, "No prebuilt assistants found"

    # Step 2: Get first assistant and its slug
    first_assistant = prebuilt_assistants[0]
    assert first_assistant.slug is not None, "Prebuilt assistant has no slug"

    # Step 3: Get the same assistant by slug
    assistant_by_slug = client.assistants.get_prebuilt_by_slug(first_assistant.slug)

    # Step 4: Compare assistants
    assert assistant_by_slug is not None, "Failed to get assistant by slug"
    assert assistant_by_slug.id == first_assistant.id, "Assistant IDs don't match"
    assert assistant_by_slug.slug == first_assistant.slug, "Assistant slugs don't match"
    assert assistant_by_slug.name == first_assistant.name, "Assistant names don't match"
    assert assistant_by_slug.description == first_assistant.description, (
        "Assistant descriptions don't match"
    )
    assert assistant_by_slug.system_prompt == first_assistant.system_prompt, (
        "Assistant system prompts don't match"
    )

    # Compare toolkits
    assert len(assistant_by_slug.toolkits) == len(first_assistant.toolkits), (
        "Different number of toolkits"
    )
    for toolkit1, toolkit2 in zip(assistant_by_slug.toolkits, first_assistant.toolkits):
        assert toolkit1.toolkit == toolkit2.toolkit, "Toolkit names don't match"
        assert len(toolkit1.tools) == len(toolkit2.tools), (
            f"Different number of tools in toolkit {toolkit1.toolkit}"
        )
        for tool1, tool2 in zip(toolkit1.tools, toolkit2.tools):
            assert tool1.name == tool2.name, (
                f"Tool names don't match in toolkit {toolkit1.toolkit}"
            )


def test_assistant_evaluate(client: CodeMieClient):
    evaluation_request = AssistantEvaluationRequest(
        dataset_id="codemie-faq-basic", experiment_name=f"Eval {uuid.uuid4()}"
    )

    # Execute evaluation with minimal request
    result = client.assistants.evaluate(
        "05959338-06de-477d-9cc3-08369f858057", evaluation_request
    )

    # Verify response structure
    assert result is not None
    assert isinstance(result, dict)
    print(result)


def test_assistant_evaluate_not_found(client: CodeMieClient):
    """Test assistant evaluation with non-existent assistant."""
    evaluation_request = AssistantEvaluationRequest(
        dataset_id="test-dataset-999", experiment_name="Error Test"
    )

    # Test with non-existent assistant ID
    with pytest.raises(Exception) as exc_info:
        client.assistants.evaluate("non-existent-assistant-id", evaluation_request)

    # Verify it's a proper error response
    assert exc_info.value is not None
