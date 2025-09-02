"""Integration tests for WorkflowExecutionService."""

from time import sleep

import pytest
import requests

from codemie_sdk import CodeMieClient
from codemie_sdk.models.workflow import (
    WorkflowCreateRequest,
    WorkflowMode,
    ExecutionStatus,
)
from codemie_test_harness.tests import PROJECT
from codemie_test_harness.tests.utils.base_utils import get_random_name


@pytest.fixture
def valid_workflow_yaml(default_llm) -> str:
    """Return a valid workflow YAML configuration for testing."""
    return f"""
assistants:
  - id: asst
    name: Simple assistant
    model: {default_llm.base_name}
    system_prompt: |
      You are simple chatbot. 
      Generate a simple response.

states:
  - id: simple
    assistant_id: asst
    task: |
      Say "Hello, World!"
    next:
      state_id: end
"""


@pytest.fixture
def test_workflow(client: CodeMieClient, valid_workflow_yaml: str):
    """Create a test workflow and clean it up after the test."""
    workflow_name = get_random_name()
    workflow_id = None

    try:
        # Create workflow
        create_request = WorkflowCreateRequest(
            name=workflow_name,
            description="Test workflow for executions",
            project=PROJECT,
            yaml_config=valid_workflow_yaml,
            mode=WorkflowMode.SEQUENTIAL,
            shared=False,
        )

        created = client.workflows.create_workflow(create_request)
        assert created is not None

        sleep(5)  # Wait for workflow to be fully created

        workflows = client.workflows.list(projects=PROJECT, per_page=10)
        workflow = next((wf for wf in workflows if wf.name == workflow_name), None)
        assert workflow is not None
        workflow_id = workflow.id

        yield workflow_id

    finally:
        # Clean up
        if workflow_id:
            try:
                client.workflows.delete(workflow_id)
            except Exception as e:
                pytest.fail(f"Failed to clean up workflow: {str(e)}")


def test_run_workflow(client: CodeMieClient, test_workflow: str):
    """Test workflow execution with state verification."""

    execution_id = None
    try:
        # Create a new execution
        execution = client.workflows.run(test_workflow, "Test")
        assert execution is not None
        sleep(5)

        # Test listing all executions
        executions = client.workflows.executions(test_workflow).list()
        assert executions is not None
        assert len(executions) == 1
        found_execution = executions[0]
        execution_id = executions[0].execution_id
        assert found_execution.workflow_id == test_workflow
        assert found_execution.status is not None
        assert found_execution.created_date is not None
        assert found_execution.created_by is not None

        # Test pagination
        paginated = client.workflows.executions(test_workflow).list(page=0, per_page=1)
        assert len(paginated) <= 1

        max_attempts = 30  # 30 * 2 seconds = 60 seconds total wait time
        attempts = 0
        while attempts < max_attempts:
            execution = client.workflows.executions(test_workflow).get(execution_id)
            if execution.status == ExecutionStatus.SUCCEEDED:
                # Only verify states and outputs on successful execution
                # Verify execution states
                states = (
                    client.workflows.executions(test_workflow)
                    .states(execution_id)
                    .list()
                )
                assert states is not None
                assert len(states) == 2

                first_state = states[0]
                second_state = states[1]
                assert first_state.completed_at is not None
                assert second_state.completed_at is not None
                assert first_state.completed_at < second_state.completed_at

                # Verify the state outputs
                for state in states:
                    state_output = (
                        client.workflows.executions(test_workflow)
                        .states(execution_id)
                        .get_output(state.id)
                    )
                    assert state_output is not None
                    assert state_output.output is not None
                    # For our test workflow, the first state should contain "Hello, World!"
                    if state.id == "simple":
                        assert "Hello, World!" in state_output.output
                break
            elif execution.status == ExecutionStatus.FAILED:
                pytest.fail(f"Workflow execution failed: {execution.error_message}")

            sleep(2)
            attempts += 1
        else:
            raise TimeoutError(
                f"Workflow execution did not complete within {attempts * 2} seconds"
            )

    finally:
        if execution_id:
            try:
                client.workflows.executions(test_workflow).delete_all()
                sleep(5)
                try:
                    client.workflows.executions(test_workflow).get(execution_id)
                    pytest.fail(
                        f"Workflow execution {execution_id} still exists after deletion"
                    )
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code != 404:
                        pytest.fail(
                            f"Unexpected error during cleanup verification: {str(e)}"
                        )
            except Exception as e:
                pytest.fail(f"Failed to clean up workflow execution: {str(e)}")


def test_list_executions_nonexistent_workflow(client: CodeMieClient):
    """Test listing executions for non-existent workflow."""
    workflows = client.workflows.executions("non-existent-id").list()
    print(workflows)
    assert len(workflows) == 0


def test_list_executions_invalid_parameters(client: CodeMieClient, test_workflow: str):
    """Test listing executions with invalid parameters."""
    # Test invalid page number
    with pytest.raises(Exception) as exc_info:
        client.workflows.executions(test_workflow).list(page=-1)
    assert "page" in str(exc_info.value).lower()

    # Test invalid per_page value
    with pytest.raises(Exception) as exc_info:
        client.workflows.executions(test_workflow).list(per_page=0)
    assert "per_page" in str(exc_info.value).lower()
