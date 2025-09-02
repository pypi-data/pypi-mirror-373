"""Integration tests for WorkflowService."""

from time import sleep

import pytest
from pydantic import ValidationError

from codemie_sdk import CodeMieClient
from codemie_sdk.models.workflow import (
    WorkflowCreateRequest,
    WorkflowUpdateRequest,
    WorkflowMode,
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
      Analyze user input and generate focused answer 

states:
  - id: list
    assistant_id: asst
    task: |
      Generate a list 5 colors
    output_schema: |
      {{
        "colors": ["orange", "blue", "red", ...]
      }}
    next:
      state_id: gen
      iter_key: colors
  - id: gen
    assistant_id: asst
    task: |
      Generate a very long text about a color
    next:
      state_id: summary
      iter_key: colors
  - id: summary
    assistant_id: asst
    task: |
      Assess how good color description was. Put a mark from 1 to 10. 1 - worst, 10 - the best. Judge if you are expert in colors.
      Explain your choice and provide reasoning
    next:
      state_id: end
"""


def test_workflow_lifecycle(client: CodeMieClient, valid_workflow_yaml: str):
    """Test full workflow lifecycle: create, get, update, and delete workflow."""
    # Step 1: Create workflow
    workflow_name = get_random_name()
    project = PROJECT
    workflow_id = None
    try:
        create_request = WorkflowCreateRequest(
            name=workflow_name,
            description="Workflow that analyzes and generates content about colors",
            project=project,
            yaml_config=valid_workflow_yaml,
            mode=WorkflowMode.SEQUENTIAL,
            shared=False,
        )

        # Create workflow
        created = client.workflows.create_workflow(create_request)
        assert created is not None

        sleep(5)
        workflows = client.workflows.list(projects=project, per_page=10)
        assert len(workflows) > 0
        workflow = next((wf for wf in workflows if wf.name == workflow_name), None)
        assert workflow.id is not None
        workflow_id = workflow.id
        assert (
            workflow.description
            == "Workflow that analyzes and generates content about colors"
        )
        assert workflow.project == project
        assert workflow.mode == WorkflowMode.SEQUENTIAL
        assert workflow.shared is False
        assert workflow.created_by is not None

        # Step 2: Update the workflow with modified yaml
        updated_yaml = valid_workflow_yaml.replace(
            "Generate a list 5 colors", "Generate a list of 10 vibrant colors"
        )
        updated_name = f"{workflow_name} Updated"
        update_request = WorkflowUpdateRequest(
            name=updated_name,
            project=project,
            description="Updated color analysis workflow",
            yaml_config=updated_yaml,
        )

        updated = client.workflows.update(workflow_id, update_request)
        assert updated is not None

        sleep(5)
        updated_workflow = client.workflows.get(workflow_id)
        assert updated_workflow.name == updated_name
        assert updated_workflow.description == "Updated color analysis workflow"
        assert "Generate a list of 10 vibrant colors" in updated_workflow.yaml_config

        # Step 3: Verify partial update (only name)
        updated_name = "Color Generator v2"
        partial_update = WorkflowUpdateRequest(
            name=updated_name,
            project=project,
            description="Updated color analysis workflow",
            yaml_config=updated_yaml,
        )
        partially_updated = client.workflows.update(workflow_id, partial_update)
        assert partially_updated is not None

        sleep(5)
        partially_updated = client.workflows.get(workflow_id)
        assert partially_updated.id == workflow_id
        assert partially_updated.name == updated_name
        # Other fields should remain unchanged
        assert partially_updated.description == "Updated color analysis workflow"
        assert partially_updated.mode == WorkflowMode.SEQUENTIAL
        assert "Generate a list of 10 vibrant colors" in partially_updated.yaml_config

    finally:
        # Clean up - try to delete the workflow
        try:
            if workflow_id:
                client.workflows.delete(workflow_id)
                sleep(5)
                with pytest.raises(Exception):
                    client.datasources.get(workflow_id)
        except Exception as e:
            pytest.fail(f"Failed to clean up workflow: {str(e)}")


def test_create_workflow_invalid_yaml(client: CodeMieClient, default_llm):
    """Test workflow creation with invalid YAML config."""
    invalid_yaml = f"""
assistants:
  - id: asst
    invalid: : format : here
    model: {default_llm.base_name}
states:
  - missing required fields
"""

    create_request = WorkflowCreateRequest(
        name=get_random_name(),
        description="Test workflow with invalid YAML",
        project=PROJECT,
        yaml_config=invalid_yaml,
    )

    with pytest.raises(Exception) as exc_info:
        client.workflows.create_workflow(create_request)
    assert "400" in str(exc_info.value) or "invalid" in str(exc_info.value).lower()


@pytest.mark.skip(reason="Need to fix API to return 404")
def test_update_workflow_not_found(client: CodeMieClient, valid_workflow_yaml: str):
    """Test updating non-existent workflow."""
    update_request = WorkflowUpdateRequest(
        name=get_random_name(),
        description="Updated description",
        yaml_config=valid_workflow_yaml,
        project=PROJECT,
    )

    with pytest.raises(Exception) as exc_info:
        client.workflows.update("non-existent-id", update_request)
    assert "404" in str(exc_info.value) or "not found" in str(exc_info.value).lower()


def test_create_workflow_validation(client: CodeMieClient, valid_workflow_yaml: str):
    """Test workflow creation with invalid data for validation."""
    # Test with missing required fields
    with pytest.raises(Exception):
        WorkflowCreateRequest(
            name=get_random_name(),  # missing project
            description="Test workflow description",
            yaml_config=valid_workflow_yaml,
        )

    # Test with invalid mode
    with pytest.raises(Exception):
        WorkflowCreateRequest(
            name=get_random_name(),
            description="Test description",
            project=PROJECT,
            yaml_config=valid_workflow_yaml,
            mode="InvalidMode",  # Invalid enum value
        )

    # Test with empty required fields
    with pytest.raises(Exception):
        WorkflowCreateRequest(
            name="",  # Empty name
            description="Test description",
            project=PROJECT,
            yaml_config=valid_workflow_yaml,
        )


@pytest.mark.skip(reason="Need to fix project validation to throw error")
def test_create_workflow_project_validation(
    client: CodeMieClient, valid_workflow_yaml: str
):
    """Test workflow creation with invalid project."""
    create_request = WorkflowCreateRequest(
        name=get_random_name(),
        description="Test workflow with invalid project",
        project="non-existent-project",
        yaml_config=valid_workflow_yaml,
    )

    with pytest.raises(Exception) as exc_info:
        client.workflows.create_workflow(create_request)
    assert "400" in str(exc_info.value) or "project" in str(exc_info.value).lower()


def test_list_workflows(client: CodeMieClient):
    """Test listing workflows with various filters and pagination."""
    workflows = client.workflows.list(per_page=2)
    assert workflows is not None

    workflows = client.workflows.list(per_page=2, page=1)
    assert workflows is not None
    assert len(workflows) <= 2


def test_list_workflows_invalid_parameters(client: CodeMieClient):
    """Test listing workflows with invalid parameters."""
    # Test invalid page number
    with pytest.raises(ValidationError) as exc_info:
        client.workflows.list(page=-1)
    assert "Input should be greater than or equal to 0" in str(exc_info.value)

    # Test invalid per_page value
    with pytest.raises(ValidationError) as exc_info:
        client.workflows.list(per_page=0)
    assert "Input should be greater than 0" in str(exc_info.value)

    # Test invalid project name
    workflows = client.workflows.list(projects="nonexistent-project")
    assert len(workflows) == 0  # Should return empty list for non-existent project
