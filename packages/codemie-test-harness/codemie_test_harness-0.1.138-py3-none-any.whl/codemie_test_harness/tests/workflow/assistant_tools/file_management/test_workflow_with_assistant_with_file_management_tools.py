import os

import pytest
from hamcrest import assert_that, contains_string, is_not, all_of

from codemie_test_harness.tests.enums.tools import FileManagementTool, Toolkit
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
def test_workflow_with_assistant_with_file_management_tools(
    assistant,
    workflow_with_assistant,
    filesystem_integration,
    workflow_utils,
    similarity_check,
    tool_name,
    prompt,
    expected_response,
):
    assistant = assistant(Toolkit.FILE_MANAGEMENT, tool_name, filesystem_integration)
    workflow_with_assistant = workflow_with_assistant(assistant, prompt)
    response = workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name
    )

    similarity_check.check_similarity(response, expected_response)


@pytest.mark.regression
@pytest.mark.skipif(
    os.getenv("ENV") == "local", reason="Skipping this test on local environment"
)
def test_workflow_with_assistant_with_generate_image_tool(
    assistant,
    workflow_with_assistant,
    filesystem_integration,
    workflow_utils,
):
    assistant = assistant(
        Toolkit.FILE_MANAGEMENT,
        FileManagementTool.GENERATE_IMAGE,
        filesystem_integration,
    )
    workflow_with_assistant = workflow_with_assistant(
        assistant, GENERATE_IMAGE_TOOL_TASK
    )

    response = workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name
    )

    assert_that(
        response.lower(),
        all_of(
            contains_string("https://"),
            is_not(contains_string("error")),
        ),
    )


@pytest.mark.regression
def test_workflow_with_assistant_with_read_file_tool(
    assistant,
    workflow_with_assistant,
    filesystem_integration,
    workflow_utils,
    similarity_check,
):
    assistant = assistant(
        Toolkit.FILE_MANAGEMENT,
        (FileManagementTool.WRITE_FILE, FileManagementTool.READ_FILE),
        filesystem_integration,
    )
    workflow_with_assistant = workflow_with_assistant(assistant, "Run")

    # Step 1: Write file
    workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name, WRITE_FILE_TASK
    )

    # Step 2: Read file
    response = workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name, READ_FILE_TOOL_TASK
    )
    similarity_check.check_similarity(response, RESPONSE_FOR_READ_FILE_TASK)


@pytest.mark.skip(reason="Test are flaky, tools work unstable")
@pytest.mark.regression
def test_workflow_with_assistant_with_file_editing_tool(
    assistant,
    workflow_with_assistant,
    filesystem_integration,
    workflow_utils,
    similarity_check,
):
    file_to_update = f"sum_{get_random_name()}.py"

    assistant = assistant(
        Toolkit.FILE_MANAGEMENT,
        (FileManagementTool.WRITE_FILE, FileManagementTool.DIFF_UPDATE),
        filesystem_integration,
    )
    workflow_with_assistant = workflow_with_assistant(assistant, "Run")

    # Create the file
    workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name, create_file_task(file_to_update)
    )

    # Insert to the file
    workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name, insert_to_file_task(file_to_update)
    )

    # Show the diff
    response = workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name, show_diff_task(file_to_update)
    )

    similarity_check.check_similarity(response, RESPONSE_FOR_DIFF_UPDATE)


@pytest.mark.skip(reason="Test are flaky, tools work unstable")
@pytest.mark.regression
def test_workflow_with_assistant_with_filesystem_tool(
    assistant,
    workflow_with_assistant,
    workflow_utils,
    filesystem_integration,
    similarity_check,
):
    file_to_update = f"sum_{get_random_name()}.py"

    assistant = assistant(
        Toolkit.FILE_MANAGEMENT,
        FileManagementTool.FILESYSTEM_EDITOR,
        filesystem_integration,
    )
    workflow_with_assistant = workflow_with_assistant(assistant, "Run")

    # Create the file
    workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name, create_file_task(file_to_update)
    )

    # Insert to the file
    workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name, insert_to_file_task(file_to_update)
    )

    # Show the file content
    response = workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name, show_file_task(file_to_update)
    )

    similarity_check.check_similarity(response, RESPONSE_FOR_FILE_EDITOR)
