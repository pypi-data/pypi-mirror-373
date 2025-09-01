import os

import pytest

from codemie_test_harness.tests.test_data.mcp_server_test_data import (
    FETCH_MCP_SERVER,
    fetch_expected_response,
    time_expected_response,
    TIME_MCP_SERVER_WITH_CONFIG,
    time_server_prompt,
    fetch_server_prompt,
)
from codemie_test_harness.tests.test_data.mcp_server_test_data import (
    cli_mcp_server_test_data,
    CLI_MCP_SERVER,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name


@pytest.mark.regression
@pytest.mark.mcp
@pytest.mark.testcase("EPMCDME-6419")
@pytest.mark.skipif(
    os.getenv("ENV") == "local", reason="Skipping this test on local environment"
)
def test_workflow_with_time_mcp_server(
    workflow_with_virtual_assistant,
    workflow_utils,
    similarity_check,
):
    """Test workflow execution with Time MCP server."""
    assistant_and_state_name = get_random_name()

    test_workflow = workflow_with_virtual_assistant(
        assistant_and_state_name,
        mcp_servers=[TIME_MCP_SERVER_WITH_CONFIG],
    )

    response = workflow_utils.execute_workflow(
        test_workflow.id,
        assistant_and_state_name,
        time_server_prompt,
    )
    similarity_check.check_similarity(response, time_expected_response)


@pytest.mark.regression
@pytest.mark.mcp
@pytest.mark.testcase("EPMCDME-6419")
@pytest.mark.parametrize(
    "command, expected_answer",
    cli_mcp_server_test_data,
    ids=[f"{row[0]}" for row in cli_mcp_server_test_data],
)
@pytest.mark.skipif(
    os.getenv("ENV") == "local", reason="Skipping this test on local environment"
)
def test_workflow_with_cli_mcp_server(
    workflow_with_virtual_assistant,
    workflow_utils,
    similarity_check,
    command,
    expected_answer,
):
    """Test workflow execution with CLI MCP server."""
    assistant_and_state_name = get_random_name()

    test_workflow = workflow_with_virtual_assistant(
        assistant_and_state_name,
        mcp_servers=[CLI_MCP_SERVER],
        task="Run command. In case of error just explain the issue and do not suggest any workarounds and do not try to run command with other parameters.",
    )

    response = workflow_utils.execute_workflow(
        test_workflow.id, assistant_and_state_name, f"execute the command: '{command}'"
    )
    similarity_check.check_similarity(response, expected_answer)


@pytest.mark.regression
@pytest.mark.mcp
@pytest.mark.testcase("EPMCDME-6419")
@pytest.mark.skipif(
    os.getenv("ENV") == "local", reason="Skipping this test on local environment"
)
def test_workflow_with_fetch_mcp_server(
    workflow_with_virtual_assistant,
    workflow_utils,
    similarity_check,
):
    """Test workflow execution with Fetch MCP server."""
    assistant_and_state_name = get_random_name()

    test_workflow = workflow_with_virtual_assistant(
        assistant_and_state_name, mcp_servers=[FETCH_MCP_SERVER], task="Run tool"
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id, assistant_and_state_name, fetch_server_prompt
    )
    similarity_check.check_similarity(response, fetch_expected_response)
