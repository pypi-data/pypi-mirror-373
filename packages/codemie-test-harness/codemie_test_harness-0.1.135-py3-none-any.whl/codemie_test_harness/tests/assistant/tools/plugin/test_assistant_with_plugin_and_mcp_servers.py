import os

import pytest

from codemie_test_harness.tests.enums.tools import Toolkit
from codemie_test_harness.tests.test_data.mcp_server_test_data import (
    cli_mcp_server_with_plugin_test_data,
    filesystem_mcp_server_with_plugin_test_data,
)
from codemie_test_harness.tests.utils.constants import TESTS_PATH


@pytest.mark.regression
@pytest.mark.plugin
@pytest.mark.parametrize(
    "prompt,expected_response",
    cli_mcp_server_with_plugin_test_data,
    ids=[f"{row[0]}" for row in cli_mcp_server_with_plugin_test_data],
)
def test_assistant_with_plugin_and_cli_mcp_server(
    cli_server,
    assistant_utils,
    assistant,
    similarity_check,
    prompt,
    expected_response,
):
    assistant = assistant(Toolkit.PLUGIN, Toolkit.PLUGIN, settings=cli_server)

    response = assistant_utils.ask_assistant(assistant, prompt)
    similarity_check.check_similarity(response, expected_response)


@pytest.mark.regression
@pytest.mark.plugin
@pytest.mark.parametrize(
    "prompt,expected_response,tool_name",
    filesystem_mcp_server_with_plugin_test_data,
    ids=[f"{row[2]}" for row in filesystem_mcp_server_with_plugin_test_data],
)
def test_assistant_with_plugin_and_filesystem_mcp_server(
    filesystem_server,
    assistant_utils,
    assistant,
    similarity_check,
    prompt,
    expected_response,
    tool_name,
):
    try:
        assistant = assistant(
            Toolkit.PLUGIN, Toolkit.PLUGIN, settings=filesystem_server
        )

        response = assistant_utils.ask_assistant(assistant, prompt)
        similarity_check.check_similarity(response, expected_response)
    finally:
        file_to_remove = f"{str(TESTS_PATH / 'sdk_tests')}.properties"
        if os.path.exists(file_to_remove):
            os.remove(file_to_remove)
