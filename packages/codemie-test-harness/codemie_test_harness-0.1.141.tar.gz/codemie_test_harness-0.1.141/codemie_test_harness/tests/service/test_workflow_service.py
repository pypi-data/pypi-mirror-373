from time import sleep
import pytest
from pydantic import ValidationError
from hamcrest import (
    assert_that,
    is_not,
    equal_to,
    greater_than,
    has_length,
    is_,
    contains_string,
    any_of,
    less_than_or_equal_to,
)

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


def test_full_workflow_lifecycle(
    workflow_utils, search_utils, valid_workflow_yaml: str
):
    created = workflow_utils.create_workflow(
        workflow_yaml=valid_workflow_yaml,
        workflow_type=WorkflowMode.SEQUENTIAL,
        description="Workflow that analyzes and generates content about colors",
        project_name=PROJECT,
    )

    assert_that(created, is_not(None))

    sleep(5)
    workflows = search_utils.list_workflows(projects=PROJECT, per_page=10)
    assert_that(workflows, has_length(greater_than(0)))
    workflow = next((wf for wf in workflows if wf.name == created.name), None)
    assert_that(workflow.id, is_not(None))
    workflow_id = workflow.id
    assert_that(
        workflow.description,
        equal_to("Workflow that analyzes and generates content about colors"),
    )
    assert_that(workflow.project, equal_to(PROJECT))
    assert_that(workflow.mode, equal_to(WorkflowMode.SEQUENTIAL))
    assert_that(workflow.shared, is_(False))
    assert_that(workflow.created_by, is_not(None))

    # Step 2: Update the workflow with modified yaml
    updated_yaml = valid_workflow_yaml.replace(
        "Generate a list 5 colors", "Generate a list of 10 vibrant colors"
    )
    updated_name = f"{created.name} Updated"
    updated = workflow_utils.update_workflow(
        workflow=workflow,
        name=updated_name,
        project=PROJECT,
        description="Updated color analysis workflow",
        yaml_config=updated_yaml,
    )

    assert_that(updated, is_not(None))

    sleep(5)
    updated_workflow = workflow_utils.get_workflow(workflow_id)
    assert_that(updated_workflow.name, equal_to(updated_name))
    assert_that(
        updated_workflow.description, equal_to("Updated color analysis workflow")
    )
    assert_that(
        updated_workflow.yaml_config,
        contains_string("Generate a list of 10 vibrant colors"),
    )

    # Step 3: Verify partial update (only name)
    updated_name = f"{created.name} Partially Updated"
    partially_updated = workflow_utils.update_workflow(
        workflow=workflow,
        name=updated_name,
        project=PROJECT,
        description="Updated color analysis workflow",
        yaml_config=updated_yaml,
    )

    sleep(5)
    partially_updated = workflow_utils.get_workflow(workflow_id)
    assert_that(partially_updated.id, equal_to(workflow_id))
    assert_that(partially_updated.name, equal_to(updated_name))
    # Other fields should remain unchanged
    assert_that(
        partially_updated.description, equal_to("Updated color analysis workflow")
    )
    assert_that(partially_updated.mode, equal_to(WorkflowMode.SEQUENTIAL))
    assert_that(
        partially_updated.yaml_config,
        contains_string("Generate a list of 10 vibrant colors"),
    )


def test_create_workflow_invalid_yaml(workflow_utils, default_llm):
    """Test workflow creation with invalid YAML config."""
    invalid_yaml = f"""
assistants:
  - id: asst
    invalid: : format : here
    model: {default_llm.base_name}
states:
  - missing required fields
"""

    with pytest.raises(Exception) as exc_info:
        workflow_utils.create_workflow(
            workflow_yaml=invalid_yaml,
            workflow_type=WorkflowMode.SEQUENTIAL,
            description="Test workflow with invalid YAML",
            project_name=PROJECT,
        )
    assert_that(
        str(exc_info.value).lower(),
        any_of(contains_string("400"), contains_string("invalid")),
    )


def test_update_workflow_not_found(workflow_utils, valid_workflow_yaml: str):
    """Test updating non-existent workflow."""
    with pytest.raises(Exception) as exc_info:
        request = WorkflowUpdateRequest(
            name=get_random_name(),
            description="description for non-existent workflow",
            yaml_config=valid_workflow_yaml,
            project=PROJECT,
        )
        workflow_utils.send_update_workflow_request(
            workflow_id="non-existent-id", request=request
        )
    assert_that(
        str(exc_info.value).lower(),
        any_of(contains_string("400"), contains_string("not found")),
    )


def test_create_workflow_with_invalid_data(valid_workflow_yaml: str):
    # Test with missing project field
    with pytest.raises(Exception):
        WorkflowCreateRequest(
            name=get_random_name(),
            description="Test workflow description",
            yaml_config=valid_workflow_yaml,
        )

    # Test with invalid workflow mode
    with pytest.raises(Exception):
        WorkflowCreateRequest(
            name=get_random_name(),
            description="Test description",
            project=PROJECT,
            yaml_config=valid_workflow_yaml,
            mode="InvalidMode",
        )

    # Test with empty workflow name
    with pytest.raises(Exception):
        WorkflowCreateRequest(
            name="",
            description="Test description",
            project=PROJECT,
            yaml_config=valid_workflow_yaml,
        )


def test_create_workflow_project_validation(workflow_utils, valid_workflow_yaml: str):
    """Test workflow creation with invalid project."""
    with pytest.raises(Exception) as exc_info:
        workflow_utils.send_create_workflow_request(
            project_name="non-existent-project",
            workflow_yaml=valid_workflow_yaml,
            description="Test workflow with invalid project",
            workflow_type=WorkflowMode.SEQUENTIAL,
        )
    assert_that(
        str(exc_info.value).lower(),
        any_of(contains_string("400"), contains_string("project")),
    )


def test_list_workflows(search_utils):
    workflows = search_utils.list_workflows(per_page=2)
    assert_that(workflows, has_length((equal_to(2))))

    workflows = search_utils.list_workflows(per_page=2, page=1)
    assert_that(workflows, has_length(less_than_or_equal_to(2)))


def test_list_workflows_with_invalid_parameters(search_utils):
    # Test invalid page number
    with pytest.raises(ValidationError) as exc_info:
        search_utils.list_workflows(page=-1)
    assert_that(
        str(exc_info.value),
        contains_string("Input should be greater than or equal to 0"),
    )

    # Test invalid per_page value
    with pytest.raises(ValidationError) as exc_info:
        search_utils.list_workflows(per_page=0)
    assert_that(str(exc_info.value), contains_string("Input should be greater than 0"))

    # Test invalid project name. Should return empty list for non-existent project
    # Skipped. SDK method fix is required
    # workflows = search_utils.list_workflows(projects="nonexistent-project")
    # assert_that(
    #     workflows, has_length(equal_to(0))
    # )
