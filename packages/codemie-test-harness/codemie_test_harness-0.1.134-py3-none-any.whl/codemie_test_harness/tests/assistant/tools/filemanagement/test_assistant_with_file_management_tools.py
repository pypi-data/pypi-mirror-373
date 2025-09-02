import os

import pytest
from hamcrest import assert_that, contains_string, is_not, all_of

from codemie_test_harness.tests.enums.tools import Toolkit, FileManagementTool
from codemie_test_harness.tests.test_data.file_management_tools_test_data import (
    file_management_tools_test_data,
    GENERATE_IMAGE_TOOL_TASK,
    WRITE_FILE_TASK,
    READ_FILE_TOOL_TASK,
    RESPONSE_FOR_READ_FILE_TASK,
    create_file_task,
    insert_to_file_task,
    show_file_task,
    file_editing_tools_test_data,
    show_diff_task,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name


@pytest.mark.regression
@pytest.mark.parametrize(
    "tool_name,prompt,expected_response",
    file_management_tools_test_data,
    ids=[
        FileManagementTool.PYTHON_CODE_INTERPRETER,
        FileManagementTool.LIST_DIRECTORY,
        FileManagementTool.WRITE_FILE,
        FileManagementTool.RUN_COMMAND_LINE,
    ],
)
@pytest.mark.testcase("EPMCDME-6103")
def test_create_assistant_with_file_management_tool(
    filesystem_integration,
    assistant,
    assistant_utils,
    similarity_check,
    tool_name,
    prompt,
    expected_response,
):
    assistant = assistant(
        Toolkit.FILE_MANAGEMENT, tool_name, settings=filesystem_integration
    )

    response = assistant_utils.ask_assistant(assistant, prompt)

    similarity_check.check_similarity(response, expected_response)


@pytest.mark.regression
@pytest.mark.testcase("EPMCDME-6103")
@pytest.mark.skipif(
    os.getenv("ENV") == "local", reason="Skipping this test on local environment"
)
def test_create_assistant_with_file_management_generate_image_tool(
    filesystem_integration, assistant, assistant_utils, similarity_check
):
    assistant = assistant(
        Toolkit.FILE_MANAGEMENT,
        FileManagementTool.GENERATE_IMAGE,
        settings=filesystem_integration,
    )

    response = assistant_utils.ask_assistant(assistant, GENERATE_IMAGE_TOOL_TASK)

    assert_that(
        response.lower(),
        all_of(
            contains_string("https://"),
            is_not(contains_string("error")),
        ),
    )


@pytest.mark.regression
@pytest.mark.testcase("EPMCDME-6103")
def test_create_assistant_with_file_management_read_file_tool(
    filesystem_integration, assistant, assistant_utils, similarity_check
):
    assistant = assistant(
        Toolkit.FILE_MANAGEMENT,
        (FileManagementTool.WRITE_FILE, FileManagementTool.READ_FILE),
        settings=filesystem_integration,
    )

    assistant_utils.ask_assistant(assistant, WRITE_FILE_TASK)

    response = assistant_utils.ask_assistant(assistant, READ_FILE_TOOL_TASK)

    similarity_check.check_similarity(response, RESPONSE_FOR_READ_FILE_TASK)


@pytest.mark.skip(reason="Tests are flaky, tools work unstable")
@pytest.mark.regression
@pytest.mark.parametrize(
    "tool_name,expected_response",
    file_editing_tools_test_data,
    ids=[f"{row[0]}" for row in file_editing_tools_test_data],
)
@pytest.mark.testcase("EPMCDME-6103")
def test_create_assistant_with_file_management_file_editing_tool(
    filesystem_integration,
    assistant,
    assistant_utils,
    similarity_check,
    tool_name,
    expected_response,
):
    assistant = assistant(
        Toolkit.FILE_MANAGEMENT,
        tool_name,
        settings=filesystem_integration,
    )
    file_to_update = f"sum_{get_random_name()}.py"
    assistant_utils.ask_assistant(assistant, create_file_task(file_to_update))

    assistant_utils.ask_assistant(assistant, insert_to_file_task(file_to_update))

    prompt = (
        show_file_task(file_to_update)
        if tool_name == FileManagementTool.FILESYSTEM_EDITOR
        else show_diff_task(file_to_update)
    )

    response = assistant_utils.ask_assistant(assistant, prompt)

    similarity_check.check_similarity(response, expected_response)
