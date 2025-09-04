import os

import pytest

from codemie_test_harness.tests.enums.tools import PluginTool
from codemie_test_harness.tests.test_data.mcp_server_test_data import (
    cli_mcp_server_with_plugin_test_data,
    filesystem_mcp_server_with_plugin_test_data,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name
from codemie_test_harness.tests.utils.constants import TESTS_PATH


@pytest.mark.regression
@pytest.mark.plugin
@pytest.mark.parametrize(
    "prompt,expected_response",
    cli_mcp_server_with_plugin_test_data,
    ids=[f"{row[0]}" for row in cli_mcp_server_with_plugin_test_data],
)
def test_workflow_with_plugin_and_cli_mcp_server(
    cli_server,
    workflow_utils,
    workflow_with_virtual_assistant,
    similarity_check,
    prompt,
    expected_response,
):
    assistant_and_state_name = get_random_name()
    workflow = workflow_with_virtual_assistant(
        assistant_and_state_name,
        PluginTool.RUN_COMMAND,
        integration=cli_server,
        task="Run tool",
    )

    response = workflow_utils.execute_workflow(
        workflow.id, assistant_and_state_name, user_input=prompt
    )
    similarity_check.check_similarity(response, expected_response)


@pytest.mark.regression
@pytest.mark.plugin
@pytest.mark.parametrize(
    "prompt,expected_response,tool_name",
    filesystem_mcp_server_with_plugin_test_data,
    ids=[f"{row[2]}" for row in filesystem_mcp_server_with_plugin_test_data],
)
def test_workflow_with_plugin_and_filesystem_mcp_server(
    filesystem_server,
    workflow_utils,
    workflow_with_virtual_assistant,
    similarity_check,
    prompt,
    expected_response,
    tool_name,
):
    try:
        assistant_and_state_name = get_random_name()
        workflow = workflow_with_virtual_assistant(
            assistant_and_state_name,
            tool_name,
            integration=filesystem_server,
            task="Run tool",
        )

        response = workflow_utils.execute_workflow(
            workflow.id, assistant_and_state_name, user_input=prompt
        )
        similarity_check.check_similarity(response, expected_response)
    finally:
        file_to_remove = f"{str(TESTS_PATH / 'sdk_tests')}.properties"
        if os.path.exists(file_to_remove):
            os.remove(file_to_remove)
