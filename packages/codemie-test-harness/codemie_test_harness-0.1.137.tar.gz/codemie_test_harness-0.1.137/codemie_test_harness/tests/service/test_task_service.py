import time
import uuid
from datetime import datetime

import pytest
from hamcrest import (
    assert_that,
    has_length,
    greater_than,
    equal_to,
    is_in,
    contains_string,
    is_not,
)

from codemie_sdk.models.assistant import (
    AssistantChatRequest,
    ToolKitDetails,
    ToolDetails,
    ChatMessage,
    ChatRole,
)
from codemie_sdk.models.task import BackgroundTaskEntity
from codemie_test_harness.tests import PROJECT


def test_run_flow_of_background_task(assistant_utils, default_llm):
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

    created = assistant_utils.create_assistant(
        llm_model_type=default_llm.base_name,
        toolkits=[
            ToolKitDetails(
                toolkit=first_toolkit.toolkit, tools=[ToolDetails(name=first_tool.name)]
            )
        ],
        system_prompt="You are a helpful integration test assistant. Please provide detailed responses.",
        description="Integration test assistant for background tasks",
    )
    filters = {"project": PROJECT, "shared": False}
    assistants = assistant_utils.get_assistants(minimal_response=True, filters=filters)
    found_assistant = next((a for a in assistants if a.name == created.name), None)

    # Start a chat in background mode with a complex question
    complex_question = """
    Please provide a detailed analysis of software architecture patterns, including:
    1. Monolithic Architecture
    2. Microservices Architecture
    3. Event-Driven Architecture
    4. Layered Architecture
    5. Space-Based Architecture
    
    For each pattern, include:
    - Definition
    - Key characteristics
    - Advantages and disadvantages
    - Best use cases
    - Implementation challenges
    - Real-world examples
    """

    chat_request = AssistantChatRequest(
        text=complex_question,
        conversation_id=str(uuid.uuid4()),
        history=[
            ChatMessage(
                role=ChatRole.USER,
                message="Hi, I need help with software architecture",
            ),
            ChatMessage(
                role=ChatRole.ASSISTANT,
                message="Of course! I'd be happy to help with software architecture. What would you like to know?",
            ),
        ],
        stream=False,
        background_task=True,  # Enable background mode
    )

    response = assistant_utils.send_chat_request(
        assistant=found_assistant, request=chat_request
    )

    assert_that(response.task_id, is_not(None))

    # Poll task status until completion
    max_attempts = 30  # Maximum number of polling attempts
    polling_interval = 2  # Seconds between polling attempts
    task_id = response.task_id
    task_completed = False

    for _ in range(max_attempts):
        task = assistant_utils.get_tasks(task_id)
        assert_that(isinstance(task, BackgroundTaskEntity))
        assert_that(task.id, equal_to(task_id))
        assert_that(isinstance(task.date, datetime))
        assert_that(isinstance(task.update_date, datetime))
        assert_that(task.status, is_in(["STARTED", "COMPLETED", "FAILED"]))
        assert_that(task.user, is_not(None))
        assert_that(task.task, is_not(None))

        if task.status == "COMPLETED":
            task_completed = True
            assert_that(len(task.final_output), greater_than(0))

            # The response should contain architecture patterns
            assert_that(task.final_output, contains_string("Monolithic"))
            assert_that(task.final_output, contains_string("Microservices"))
            break
        elif task.status == "FAILED":
            pytest.fail(f"Task failed with output: {task.final_output}")

        time.sleep(polling_interval)

    assert_that(
        task_completed,
        equal_to(True),
        "Task did not complete within the expected time",
    )


def test_get_task_not_found(assistant_utils):
    """Test getting a non-existent task."""
    with pytest.raises(Exception) as exc_info:
        assistant_utils.get_tasks("non-existent-task-id")
    # assert "404" in str(exc_info.value) or "not found" in str(exc_info.value).lower(), Need to fix API to produce error
    assert_that(str(exc_info.value), contains_string("500"))
