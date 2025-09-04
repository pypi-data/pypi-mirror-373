from time import sleep

import pytest
from hamcrest import (
    assert_that,
    equal_to,
    has_length,
    contains_string,
    all_of,
    less_than_or_equal_to,
    has_property,
    is_not,
)

from codemie_sdk.models.workflow import ExecutionStatus, WorkflowMode
from codemie_test_harness.tests import PROJECT
from codemie_test_harness.tests.utils.base_utils import get_random_name

from codemie_test_harness.tests.utils.yaml_utils import (
    AssistantModel,
    StateModel,
    WorkflowYamlModel,
    prepare_yaml_content,
)


@pytest.fixture(scope="session")
def test_workflow(default_llm, search_utils, workflow_utils):
    assistant_and_state_name = get_random_name()

    assistant = AssistantModel(
        id=assistant_and_state_name,
        model=default_llm.base_name,
        system_prompt="You are simple chatbot. Generate a simple response.",
    )

    state = StateModel(
        id=assistant_and_state_name,
        assistant_id=assistant_and_state_name,
        task='Say "Hello, World!"',
    )

    workflow_yaml = WorkflowYamlModel(
        enable_summarization_node=True,
        assistants=[assistant],
        states=[state],
    )

    yaml_content = prepare_yaml_content(workflow_yaml.model_dump(exclude_none=True))
    created = workflow_utils.create_workflow(
        workflow_yaml=yaml_content,
        workflow_type=WorkflowMode.SEQUENTIAL,
        project_name=PROJECT,
        description="Test workflow for executions",
    )
    assert_that(created, is_not(None))

    workflows = search_utils.list_workflows(projects=PROJECT, per_page=10)
    workflow = next((wf for wf in workflows if wf.name == created.name), None)
    assert_that(workflow, is_not(None))

    return workflow.id


def test_run_workflow(workflow_utils, search_utils, test_workflow: str):
    execution = workflow_utils.run_workflow(test_workflow, "Test")

    assert_that(execution, is_not(None))

    # Test listing all executions
    executions = search_utils.list_workflow_executions(test_workflow_id=test_workflow)
    assert_that(executions, has_length(equal_to(1)))
    found_execution = executions[0]
    execution_id = executions[0].execution_id
    assert_that(
        found_execution,
        all_of(
            has_property("workflow_id", equal_to(test_workflow)),
            has_property("status", is_not(None)),
            has_property("created_date", is_not(None)),
            has_property("created_by", is_not(None)),
        ),
    )

    # Test pagination
    paginated = search_utils.list_workflow_executions(
        test_workflow_id=test_workflow,
        page=0,
        per_page=1,
    )
    assert_that(paginated, has_length(less_than_or_equal_to(1)))

    max_attempts = 30  # 30 * 2 seconds = 60 seconds total wait time
    attempts = 0
    while attempts < max_attempts:
        execution = workflow_utils.get_workflow_execution(
            test_workflow_id=test_workflow, execution_id=execution_id
        )
        if execution.status == ExecutionStatus.SUCCEEDED:
            # Only verify states and outputs on successful execution
            # Verify execution states
            states = workflow_utils.get_workflow_executions_states(
                test_workflow, execution_id
            ).list()
            assert_that(states, has_length(equal_to(2)))

            first_state = states[0]
            second_state = states[1]
            assert_that(first_state.completed_at, is_not(None))
            assert_that(second_state.completed_at, is_not(None))
            assert_that(
                first_state.completed_at,
                less_than_or_equal_to(second_state.completed_at),
            )

            # Verify the state outputs
            for state in states:
                state_output = workflow_utils.get_workflow_executions_states(
                    test_workflow, execution_id
                ).get_output(state.id)
                # For our test workflow, the first state should contain "Hello, World!"
                if state.id == "simple":
                    assert_that(state_output.output, contains_string("Hello, World!"))
            break
        elif execution.status == ExecutionStatus.FAILED:
            pytest.fail(f"Workflow execution failed: {execution.error_message}")

        sleep(2)
        attempts += 1
    else:
        raise TimeoutError(
            f"Workflow execution did not complete within {attempts * 2} seconds"
        )


@pytest.mark.skip(reason="Bug: https://jiraeu.epam.com/browse/EPMCDME-7883")
def test_list_executions_nonexistent_workflow(search_utils):
    with pytest.raises(Exception) as exc_info:
        search_utils.list_workflow_executions("non-existent-id")

    assert_that(
        str(exc_info.value).lower(),
        contains_string("No workflows found with id non-existent-id"),
    )


def test_list_executions_with_invalid_page_number(search_utils):
    with pytest.raises(Exception) as exc_info:
        search_utils.list_workflow_executions(test_workflow_id=None, page=-1)
    assert_that(str(exc_info.value).lower(), contains_string("page"))


def test_list_executions_with_invalid_per_page_value(search_utils):
    with pytest.raises(Exception) as exc_info:
        search_utils.list_workflow_executions(test_workflow_id=None, per_page=0)
    assert_that(str(exc_info.value).lower(), contains_string("per_page"))
