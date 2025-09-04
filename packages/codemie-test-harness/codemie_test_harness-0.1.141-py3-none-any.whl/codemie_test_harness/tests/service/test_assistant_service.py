import os
import uuid
from datetime import datetime

import pytest
from codemie_sdk.models.assistant import (
    AssistantBase,
    Assistant,
    AssistantUpdateRequest,
    AssistantEvaluationRequest,
    ToolKitDetails,
    ToolDetails,
    ChatMessage,
    ChatRole,
    BaseModelResponse,
)
from hamcrest import (
    assert_that,
    has_property,
    has_item,
    greater_than,
    is_not,
    all_of,
    instance_of,
    has_length,
    equal_to,
    starts_with,
    is_,
    any_of,
    contains_string,
    greater_than_or_equal_to,
    less_than_or_equal_to,
)

from codemie_test_harness.tests import PROJECT
from codemie_test_harness.tests.utils.base_utils import get_random_name


def validate_assistant_full_response(assistant):
    assert_that(
        assistant,
        all_of(
            instance_of(Assistant),
            has_property("system_prompt"),
            has_property("project"),
            has_property("name"),
            has_property("description"),
            has_property("shared", instance_of(bool)),
            has_property("is_react", instance_of(bool)),
            has_property("is_global", instance_of(bool)),
            has_property("system_prompt_history", instance_of(list)),
            has_property("user_prompts", instance_of(list)),
            has_property("context", instance_of(list)),
            has_property("toolkits", instance_of(list)),
        ),
    )


@pytest.mark.regression
def test_get_tools(assistant_utils):
    toolkits = assistant_utils.get_assistant_tools()

    assert_that(toolkits, instance_of(list))
    assert_that(toolkits, has_length(greater_than(0)))

    toolkit = toolkits[0]
    assert_that(
        toolkit,
        all_of(
            instance_of(ToolKitDetails),
            has_property("toolkit"),
            has_property("tools", instance_of(list)),
        ),
    )

    if toolkit.tools:
        tool = toolkit.tools[0]
        assert_that(
            tool,
            all_of(
                instance_of(ToolDetails),
                has_property("name"),
                has_property("label"),
                has_property("settings_config", instance_of(bool)),
            ),
        )


def test_list_assistants_minimal_response(assistant_utils):
    assistants = assistant_utils.get_assistants()
    assert_that(assistants, all_of(instance_of(list), has_length(greater_than(0))))

    for assistant in assistants:
        assert_that(
            assistant,
            all_of(
                instance_of(AssistantBase),
                has_property("id"),
                has_property("name"),
                has_property("description"),
            ),
        )


def test_list_assistants_full_response(assistant_utils):
    assistants = assistant_utils.get_assistants(minimal_response=False)
    assert_that(assistants, all_of(instance_of(list), has_length(greater_than(0))))

    for assistant in assistants:
        assert_that(
            assistant,
            all_of(
                instance_of(Assistant),
                has_property("id"),
                has_property("llm_model_type"),
                has_property("creator"),
                has_property("user_abilities", instance_of(list)),
                has_property("created_date", instance_of(datetime)),
            ),
            "Assistant should have valid core properties",
        )

        validate_assistant_full_response(assistant)

        if assistant.created_by:
            assert_that(
                assistant.created_by,
                all_of(
                    has_property("user_id", is_not(None)),
                    has_property("username", is_not(None)),
                    has_property("name", is_not(None)),
                ),
                "created_by should have valid properties when present",
            )


def test_list_assistants_with_filters(assistant_utils):
    filters = {"project": PROJECT, "shared": False}
    assistants = assistant_utils.get_assistants(minimal_response=False, filters=filters)

    assert_that(assistants, instance_of(list))

    for assistant in assistants:
        assert_that(assistant.project, equal_to(PROJECT))
        assert_that(assistant.shared, is_(False))


def test_list_assistants_with_pagination(assistant_utils):
    # Get first page with 5 items
    page_1 = assistant_utils.get_assistants(page=0, per_page=5)
    assert_that(len(page_1), less_than_or_equal_to(5))

    # Get second page with 5 items
    page_2 = assistant_utils.get_assistants(page=1, per_page=5)
    assert_that(len(page_2), less_than_or_equal_to(5))

    # Verify pages contain different assistants
    if page_2:  # Only if there are items on second page
        assert_that(page_1[0].id, is_not(page_2[0].id))


def test_list_assistants_with_different_scopes(assistant_utils):
    visible_assistants = assistant_utils.get_assistants(scope="visible_to_user")
    assert_that(visible_assistants, instance_of(list))

    created_assistants = assistant_utils.get_assistants(scope="created_by_user")
    assert_that(created_assistants, instance_of(list))


def test_get_assistant_by_id(assistant_utils):
    assistants = assistant_utils.get_assistants()
    assert_that(assistants, has_length(greater_than(0)))
    test_assistant_id = assistants[0].id

    assistant = assistant_utils.get_assistant_by_id(test_assistant_id)
    assert_that(assistant.id, equal_to(test_assistant_id))
    validate_assistant_full_response(assistant)


def test_get_assistant_not_found(assistant_utils):
    """Test getting a non-existent assistant."""
    with pytest.raises(Exception) as exc_info:
        assistant_utils.get_assistant_by_id("1234")
    assert_that(
        str(exc_info.value).lower(),
        any_of(contains_string("service unavailable"), contains_string("404")),
    )


def test_get_assistant_by_slug(assistant_utils, default_llm):
    toolkits = assistant_utils.get_assistant_tools()
    assert_that(
        toolkits,
        has_length(greater_than(0)),
        "At least one toolkit is required for testing",
    )

    first_toolkit = toolkits[0]
    assert_that(
        first_toolkit.tools,
        has_length(greater_than(0)),
        "No tools in the first toolkit",
    )
    first_tool = first_toolkit.tools[0]
    test_slug = get_random_name()
    created = assistant_utils.create_assistant(
        llm_model_type=default_llm.base_name,
        toolkits=[
            ToolKitDetails(
                toolkit=first_toolkit.toolkit, tools=[ToolDetails(name=first_tool.name)]
            )
        ],
        system_prompt="You are a helpful test assistant",
        description="Test assistant for slug retrieval",
        slug=test_slug,
        project_name=PROJECT,
    )

    assert_that(created, is_not(None), "Failed to create test assistant")
    full_assistant = assistant_utils.get_assistant_by_id(created.id)
    retrieved = assistant_utils.get_assistant_by_slug(test_slug)

    assert_that(
        retrieved,
        all_of(
            instance_of(Assistant),
            has_property("slug", test_slug),
            has_property("name", full_assistant.name),
            has_property("description", "Test assistant for slug retrieval"),
            has_property("project", PROJECT),
            has_property("system_prompt", is_not(None)),
            has_property("created_date", instance_of(datetime)),
            has_property("shared", instance_of(bool)),
            has_property("is_react", instance_of(bool)),
            has_property("toolkits", instance_of(list)),
        ),
        "Retrieved assistant should have all expected properties",
    )

    assert_that(retrieved.toolkits, has_length(greater_than(0)))
    assert_that(retrieved.toolkits[0].toolkit, equal_to(first_toolkit.toolkit))
    assert_that(retrieved.toolkits[0].tools[0].name, equal_to(first_tool.name))


def test_get_assistant_by_slug_non_found(assistant_utils):
    with pytest.raises(Exception) as exc_info:
        assistant_utils.get_assistant_by_slug("non-existent-assistant-slug")
    assert_that(
        str(exc_info.value).lower(),
        any_of(contains_string("404"), contains_string("not found")),
    )


def test_assistant_full_lifecycle(assistant_utils, default_llm):
    toolkits = assistant_utils.get_assistant_tools()
    assert_that(
        toolkits,
        has_length(greater_than_or_equal_to(2)),
        "At least two toolkits are required for testing",
    )

    # Get first toolkit and its first tool for initial creation
    first_toolkit = toolkits[0]
    assert_that(
        first_toolkit.tools,
        has_length(greater_than(0)),
        "No tools in the first toolkit",
    )
    first_tool = first_toolkit.tools[0]

    # Get second toolkit and its tool for update
    second_toolkit = toolkits[1]
    assert_that(
        second_toolkit.tools,
        has_length(greater_than(0)),
        "No tools in the second toolkit",
    )
    second_tool = second_toolkit.tools[0]

    # Step 2: Create assistant with first toolkit/tool
    created = assistant_utils.create_assistant(
        llm_model_type=default_llm.base_name,
        toolkits=[
            ToolKitDetails(
                toolkit=first_toolkit.toolkit, tools=[ToolDetails(name=first_tool.name)]
            )
        ],
        system_prompt="You are a helpful integration test assistant",
        description="Integration test assistant",
        project_name=PROJECT,
    )

    assert_that(created, is_not(None))
    assistant_name = created.name

    # Step 3: Verify assistant exists in the list
    filters = {"project": PROJECT, "shared": False}
    assistants = assistant_utils.get_assistants(filters=filters)
    found_assistant = next((a for a in assistants if a.name == assistant_name), None)
    assert_that(
        found_assistant,
        is_not(None),
        f"Created assistant '{assistant_name}' not found in list",
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
        project=PROJECT,
        is_react=True,
        shared=False,
    )

    updated = assistant_utils.update_assistant(found_assistant.id, update_request)
    assert_that(updated, is_not(None))

    # Verify update in the list
    assistants_after_update = assistant_utils.get_assistants(
        minimal_response=False, filters=filters
    )
    found_updated = next(
        (a for a in assistants_after_update if a.id == found_assistant.id), None
    )

    expected_name = f"{assistant_name} Updated"
    expected_description = f"{updated_name} description"
    expected_system_prompt = "You are an updated integration test assistant"

    assert_that(found_updated, is_not(None), "Updated assistant should exist")

    # Verify core assistant properties
    assert_that(
        found_updated,
        all_of(
            has_property("name", equal_to(expected_name)),
            has_property("description", equal_to(expected_description)),
            has_property("system_prompt", equal_to(expected_system_prompt)),
            has_property("llm_model_type", equal_to(default_llm.base_name)),
        ),
        "Updated assistant should have correct basic properties",
    )

    expected_toolkit = all_of(
        has_property("toolkit", equal_to(second_toolkit.toolkit)),
        has_property(
            "tools",
            has_item(has_property("name", equal_to(second_tool.name))),
        ),
    )

    assert_that(
        found_updated.toolkits,
        all_of(
            has_length(greater_than(0)),
            has_item(expected_toolkit),
        ),
        "Updated assistant should have correct toolkit configuration",
    )


def test_assistant_full_chat_functionality(assistant_utils, default_llm):
    toolkits = assistant_utils.get_assistant_tools()
    assert_that(
        toolkits,
        has_length(greater_than(0)),
        "At least one toolkit is required for testing",
    )

    # Get first toolkit and its first tool
    first_toolkit = toolkits[0]
    assert_that(
        first_toolkit.tools,
        has_length(greater_than(0)),
        "No tools in the first toolkit",
    )
    first_tool = first_toolkit.tools[0]

    # Create assistant
    created = assistant_utils.create_assistant(
        description="Integration test assistant for chat",
        system_prompt="You are a helpful integration test assistant. Always respond with 'Test response: ' prefix.",
        llm_model_type=default_llm.base_name,
        project_name=PROJECT,
        toolkits=[
            ToolKitDetails(
                toolkit=first_toolkit.toolkit, tools=[ToolDetails(name=first_tool.name)]
            )
        ],
    )

    assert created is not None
    assistant_name = created.name

    # Find assistant in the list
    filters = {"project": PROJECT, "shared": False}
    assistants = assistant_utils.get_assistants(filters=filters)
    found_assistant = next((a for a in assistants if a.name == assistant_name), None)
    assert_that(
        found_assistant,
        is_not(None),
        f"Created assistant '{assistant_name}' not found in list",
    )

    # Test chat functionality
    response = assistant_utils.ask_assistant(
        assistant=found_assistant,
        user_prompt="Hello, this is a test message",
        minimal_response=False,
        conversation_id=str(uuid.uuid4()),
        history=[
            ChatMessage(role=ChatRole.USER, message="Hi there"),
            ChatMessage(role=ChatRole.ASSISTANT, message="Hello! How can I help you?"),
        ],
    )

    assert_that(
        response,
        all_of(
            instance_of(BaseModelResponse),
            has_property(
                "generated", all_of(is_not(None), starts_with("Test response:"))
            ),
            has_property("time_elapsed", is_not(None)),
            has_property("tokens_used", is_(None)),
        ),
        "Chat response should be valid BaseModelResponse with expected properties",
    )

    # Test streaming
    stream_response = assistant_utils.ask_assistant(
        assistant=found_assistant,
        user_prompt="Hello, this is a streaming test",
        conversation_id=str(uuid.uuid4()),
        stream=True,
        minimal_response=False,
    )

    received_chunks = []
    for chunk in stream_response:
        assert_that(chunk, is_not(None))
        received_chunks.append(chunk)
    assert_that(received_chunks, has_length(greater_than(0)))


def test_get_prebuilt_assistants(assistant_utils):
    prebuilt_assistants = assistant_utils.get_prebuilt_assistant()

    assert_that(prebuilt_assistants, instance_of(list))
    assert_that(
        prebuilt_assistants, has_length(greater_than(0)), "No prebuilt assistants found"
    )

    # Verify the first assistant by slug
    first_assistant = prebuilt_assistants[0]
    assert_that(first_assistant.slug, is_not(None), "Prebuilt assistant has no slug")

    assistant_by_slug = assistant_utils.get_prebuilt_assistant_by_slug(
        first_assistant.slug
    )

    # Compare assistant details
    assert_that(
        assistant_by_slug,
        all_of(
            instance_of(Assistant),
            has_property("id", equal_to(first_assistant.id)),
            has_property("slug", equal_to(first_assistant.slug)),
            has_property("name", equal_to(first_assistant.name)),
            has_property("description", equal_to(first_assistant.description)),
            has_property("system_prompt", equal_to(first_assistant.system_prompt)),
        ),
    )

    # Compare assistant toolkits
    assert_that(
        assistant_by_slug.toolkits, has_length(equal_to(len(first_assistant.toolkits)))
    )
    for toolkit1, toolkit2 in zip(assistant_by_slug.toolkits, first_assistant.toolkits):
        assert_that(
            toolkit1,
            all_of(
                has_property("toolkit", equal_to(toolkit2.toolkit)),
                has_property("tools", has_length(equal_to(len(toolkit2.tools)))),
            ),
        )
        for tool1, tool2 in zip(toolkit1.tools, toolkit2.tools):
            assert_that(tool1, has_property("name", equal_to(tool2.name)))


@pytest.mark.skipif(
    os.getenv("ENV") != "preview", reason="valid_assistant_id is for preview env"
)
def test_assistant_evaluate(assistant_utils):
    valid_assistant_id = "05959338-06de-477d-9cc3-08369f858057"
    valid_dataset_id = "codemie-faq-basic"
    evaluation_request = AssistantEvaluationRequest(
        dataset_id=valid_dataset_id, experiment_name=f"Eval {uuid.uuid4()}"
    )

    # Execute evaluation with minimal request

    result = assistant_utils.send_evaluate_assistant_request(
        valid_assistant_id, evaluation_request
    )

    # Verify response structure
    assert_that(result, is_not(None))
    assert_that(result, instance_of(dict))


def test_assistant_evaluate_not_found(assistant_utils):
    invalid_assistant_id = "non-existent-assistant-id"
    valid_dataset_id = "test-dataset-999"
    evaluation_request = AssistantEvaluationRequest(
        dataset_id=valid_dataset_id, experiment_name="Error Test"
    )

    # Test with non-existent assistant ID
    with pytest.raises(Exception) as exc_info:
        assistant_utils.send_evaluate_assistant_request(
            invalid_assistant_id, evaluation_request
        )

    # Verify it's a proper error response
    assert_that(exc_info.value, is_not(None))
