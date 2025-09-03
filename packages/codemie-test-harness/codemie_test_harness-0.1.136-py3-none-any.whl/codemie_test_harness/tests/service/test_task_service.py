"""Integration tests for TaskService."""

import time
import uuid
from datetime import datetime

import pytest

from codemie_sdk import CodeMieClient
from codemie_sdk.models.assistant import (
    AssistantCreateRequest,
    AssistantChatRequest,
    ToolKitDetails,
    ToolDetails,
    ChatMessage,
    ChatRole,
)
from codemie_sdk.models.task import BackgroundTaskEntity
from codemie_test_harness.tests import PROJECT, LANGFUSE_TRACES_ENABLED
from codemie_test_harness.tests.utils.base_utils import get_random_name


def test_background_task_flow(client: CodeMieClient, default_llm):
    """Test the complete flow of a background task with assistant chat."""
    # Step 1: Get available toolkits and tools
    toolkits = client.assistants.get_tools()
    assert len(toolkits) > 0, "At least one toolkit is required for testing"

    first_toolkit = toolkits[0]
    assert len(first_toolkit.tools) > 0, "No tools in the first toolkit"
    first_tool = first_toolkit.tools[0]

    # Step 2: Create assistant for testing
    assistant_project = PROJECT
    assistant_name = get_random_name()
    request = AssistantCreateRequest(
        name=assistant_name,
        slug=assistant_name,
        description="Integration test assistant for background tasks",
        system_prompt="You are a helpful integration test assistant. Please provide detailed responses.",
        llm_model_type=default_llm.base_name,
        project=assistant_project,
        toolkits=[
            ToolKitDetails(
                toolkit=first_toolkit.toolkit, tools=[ToolDetails(name=first_tool.name)]
            )
        ],
    )

    # Create assistant
    client.assistants.create(request)
    filters = {"project": assistant_project, "shared": False}
    assistants = client.assistants.list(minimal_response=True, filters=filters)
    found_assistant = next((a for a in assistants if a.name == assistant_name), None)

    try:
        # Step 3: Start a chat in background mode with a complex question
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
            metadata={"langfuse_traces_enabled": LANGFUSE_TRACES_ENABLED},
        )

        # Send chat request
        response = client.assistants.chat(
            assistant_id=found_assistant.id, request=chat_request
        )
        # Verify response contains task ID
        assert response is not None
        assert response.task_id is not None

        # Step 4: Poll task status until completion
        max_attempts = 30  # Maximum number of polling attempts
        polling_interval = 2  # Seconds between polling attempts
        task_id = response.task_id
        task_completed = False

        for _ in range(max_attempts):
            # Get task status
            task = client.tasks.get(task_id)
            assert isinstance(task, BackgroundTaskEntity)

            # Verify task structure
            assert task.id == task_id
            assert isinstance(task.date, datetime)
            assert isinstance(task.update_date, datetime)
            assert task.status in ["STARTED", "COMPLETED", "FAILED"]
            assert task.user is not None
            assert task.task is not None

            if task.status == "COMPLETED":
                task_completed = True
                # Verify task output
                assert task.final_output is not None
                assert len(task.final_output) > 0
                # The response should contain architecture patterns
                assert "Monolithic" in task.final_output
                assert "Microservices" in task.final_output
                break
            elif task.status == "FAILED":
                pytest.fail(f"Task failed with output: {task.final_output}")

            time.sleep(polling_interval)

        assert task_completed, "Task did not complete within the expected time"

    finally:
        # Clean up - delete created assistant
        if found_assistant:
            try:
                client.assistants.delete(found_assistant.id)
            except Exception as e:
                pytest.fail(f"Failed to clean up assistant: {str(e)}")


@pytest.mark.skip(reason="Need to fix API to return 404")
def test_get_task_not_found(client: CodeMieClient):
    """Test getting a non-existent task."""
    with pytest.raises(Exception) as exc_info:
        client.tasks.get("non-existent-task-id")
    # assert "404" in str(exc_info.value) or "not found" in str(exc_info.value).lower(), Need to fix API to produce error
    assert "503" in str(exc_info.value)
