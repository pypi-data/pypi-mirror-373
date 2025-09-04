import os

import pytest

from codemie_test_harness.tests.enums.tools import Toolkit
from codemie_test_harness.tests.test_data.plugin_tools_test_data import (
    list_files_plugin_tools_test_data,
    CREATE_READ_DELETE_FILE_TEST_DATA,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name
from codemie_test_harness.tests.utils.constants import TESTS_PATH


@pytest.mark.regression
@pytest.mark.plugin
@pytest.mark.parametrize(
    "prompt,expected_response,tool_name",
    list_files_plugin_tools_test_data,
    ids=[row[2] for row in list_files_plugin_tools_test_data],
)
def test_workflow_with_assistant_with_list_files_plugin_tools(
    development_plugin,
    assistant,
    workflow_with_assistant,
    workflow_utils,
    similarity_check,
    prompt,
    expected_response,
    tool_name,
):
    assistant = assistant(Toolkit.PLUGIN, Toolkit.PLUGIN, settings=development_plugin)

    workflow_with_assistant = workflow_with_assistant(assistant, "Run")
    response = workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name, prompt
    )
    similarity_check.check_similarity(response, expected_response)


@pytest.mark.regression
@pytest.mark.plugin
def test_workflow_with_assistant_with_modify_files_plugin_tools(
    assistant,
    workflow_utils,
    workflow_with_assistant,
    development_plugin,
    similarity_check,
):
    file_name = get_random_name()
    try:
        assistant = assistant(
            Toolkit.PLUGIN, Toolkit.PLUGIN, settings=development_plugin
        )
        workflow_with_assistant = workflow_with_assistant(assistant, "Run")

        response = workflow_utils.execute_workflow(
            workflow_with_assistant.id,
            assistant.name,
            user_input=CREATE_READ_DELETE_FILE_TEST_DATA["create_file_prompt"].format(
                file_name, file_name
            ),
        )

        similarity_check.check_similarity(
            response,
            CREATE_READ_DELETE_FILE_TEST_DATA["create_file_response"].format(
                file_name, file_name
            ),
        )

        response = workflow_utils.execute_workflow(
            workflow_with_assistant.id,
            assistant.name,
            user_input=CREATE_READ_DELETE_FILE_TEST_DATA["git_command_prompt"].format(
                file_name
            ),
        )

        similarity_check.check_similarity(
            response,
            CREATE_READ_DELETE_FILE_TEST_DATA["git_command_response"].format(file_name),
        )

        response = workflow_utils.execute_workflow(
            workflow_with_assistant.id,
            assistant.name,
            user_input=CREATE_READ_DELETE_FILE_TEST_DATA[
                "show_file_content_prompt"
            ].format(file_name),
        )

        similarity_check.check_similarity(
            response,
            CREATE_READ_DELETE_FILE_TEST_DATA["show_file_content_response"].format(
                file_name
            ),
        )
    finally:
        os.remove(f"{str(TESTS_PATH / file_name)}.properties")
