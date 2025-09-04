import os

import pytest
from hamcrest import assert_that, contains_string, is_not, all_of

from codemie_test_harness.tests.enums.tools import FileManagementTool
from codemie_test_harness.tests.test_data.file_management_tools_test_data import (
    file_management_tools_test_data,
    GENERATE_IMAGE_TOOL_TASK,
    WRITE_FILE_TASK,
    READ_FILE_TOOL_TASK,
    RESPONSE_FOR_READ_FILE_TASK,
    create_file_task,
    insert_to_file_task,
    show_file_task,
    show_diff_task,
    RESPONSE_FOR_DIFF_UPDATE,
    RESPONSE_FOR_FILE_EDITOR,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name


@pytest.mark.regression
@pytest.mark.testcase("EPMCDME-6561")
@pytest.mark.parametrize(
    "tool_name, prompt, expected_response",
    file_management_tools_test_data,
    ids=[
        FileManagementTool.PYTHON_CODE_INTERPRETER,
        FileManagementTool.LIST_DIRECTORY,
        FileManagementTool.WRITE_FILE,
        FileManagementTool.RUN_COMMAND_LINE,
    ],
)
def test_workflow_with_file_management_tools(
    workflow_with_virtual_assistant,
    filesystem_integration,
    workflow_utils,
    similarity_check,
    tool_name,
    prompt,
    expected_response,
):
    assistant_and_state_name = get_random_name()

    test_workflow = workflow_with_virtual_assistant(
        assistant_and_state_name,
        tool_name,
        integration=filesystem_integration,
        task=prompt,
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id, assistant_and_state_name
    )

    similarity_check.check_similarity(response, expected_response)


@pytest.mark.regression
@pytest.mark.testcase("EPMCDME-6561")
@pytest.mark.skipif(
    os.getenv("ENV") == "local", reason="Skipping this test on local environment"
)
def test_workflow_with_generate_image_tool(
    workflow_with_virtual_assistant, filesystem_integration, workflow_utils
):
    assistant_and_state_name = get_random_name()
    test_workflow = workflow_with_virtual_assistant(
        assistant_and_state_name,
        FileManagementTool.GENERATE_IMAGE,
        integration=filesystem_integration,
        task=GENERATE_IMAGE_TOOL_TASK,
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id, assistant_and_state_name
    )

    assert_that(
        response.lower(),
        all_of(
            contains_string("https://"),
            is_not(contains_string("error")),
        ),
    )


@pytest.mark.regression
@pytest.mark.testcase("EPMCDME-6561")
def test_workflow_with_read_file_tool(
    workflow_with_virtual_assistant,
    filesystem_integration,
    workflow_utils,
    similarity_check,
):
    assistant_and_state_name = get_random_name()
    # Step 1: Write file
    workflow_utils.execute_workflow(
        workflow_with_virtual_assistant(
            assistant_and_state_name,
            FileManagementTool.WRITE_FILE,
            integration=filesystem_integration,
            task=WRITE_FILE_TASK,
        ).id,
        assistant_and_state_name,
    )
    # Step 2: Read file
    response = workflow_utils.execute_workflow(
        workflow_with_virtual_assistant(
            assistant_and_state_name,
            FileManagementTool.READ_FILE,
            integration=filesystem_integration,
            task=READ_FILE_TOOL_TASK,
        ).id,
        assistant_and_state_name,
    )
    similarity_check.check_similarity(response, RESPONSE_FOR_READ_FILE_TASK)


@pytest.mark.skip(reason="Test are flaky, tools work unstable")
@pytest.mark.regression
@pytest.mark.testcase("EPMCDME-6561")
def test_workflow_with_file_editing_tool(
    workflow_with_virtual_assistant,
    workflow_utils,
    filesystem_integration,
    similarity_check,
):
    assistant_and_state_name = get_random_name()
    file_to_update = f"sum_{get_random_name()}.py"
    tool_names = (FileManagementTool.WRITE_FILE, FileManagementTool.DIFF_UPDATE)

    # Create the file
    workflow_utils.execute_workflow(
        workflow_with_virtual_assistant(
            assistant_and_state_name,
            tool_names,
            integration=filesystem_integration,
            task=create_file_task(file_to_update),
        ).id,
        assistant_and_state_name,
    )

    # Insert to the file
    workflow_utils.execute_workflow(
        workflow_with_virtual_assistant(
            assistant_and_state_name,
            tool_names,
            integration=filesystem_integration,
            task=insert_to_file_task(file_to_update),
        ).id,
        assistant_and_state_name,
    )

    # Show the diff
    response = workflow_utils.execute_workflow(
        workflow_with_virtual_assistant(
            assistant_and_state_name,
            tool_names,
            integration=filesystem_integration,
            task=show_diff_task(file_to_update),
        ).id,
        assistant_and_state_name,
    )

    similarity_check.check_similarity(response, RESPONSE_FOR_DIFF_UPDATE)


@pytest.mark.skip(reason="Test are flaky, tools work unstable")
@pytest.mark.regression
@pytest.mark.testcase("EPMCDME-6561")
def test_workflow_with_filesystem_tool(
    workflow_with_virtual_assistant,
    workflow_utils,
    filesystem_integration,
    similarity_check,
):
    assistant_and_state_name = get_random_name()
    file_to_update = f"sum_{get_random_name()}.py"

    # Create the file
    workflow_utils.execute_workflow(
        workflow_with_virtual_assistant(
            assistant_and_state_name,
            FileManagementTool.FILESYSTEM_EDITOR,
            integration=filesystem_integration,
            task=create_file_task(file_to_update),
        ).id,
        assistant_and_state_name,
    )

    # Insert to the file
    workflow_utils.execute_workflow(
        workflow_with_virtual_assistant(
            assistant_and_state_name,
            FileManagementTool.FILESYSTEM_EDITOR,
            integration=filesystem_integration,
            task=insert_to_file_task(file_to_update),
        ).id,
        assistant_and_state_name,
    )

    # Show the file content
    response = workflow_utils.execute_workflow(
        workflow_with_virtual_assistant(
            assistant_and_state_name,
            FileManagementTool.FILESYSTEM_EDITOR,
            integration=filesystem_integration,
            task=show_file_task(file_to_update),
        ).id,
        assistant_and_state_name,
    )

    similarity_check.check_similarity(response, RESPONSE_FOR_FILE_EDITOR)
