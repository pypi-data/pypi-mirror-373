import json
import os

import pytest

from codemie_test_harness.tests.test_data.direct_tools.direct_tools_test_data import (
    cli_tools_test_data,
    dev_plugin_tools_test_data,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name
from codemie_test_harness.tests.utils.constants import TESTS_PATH


@pytest.fixture(scope="session", autouse=True)
def prepare_files():
    with open(str(TESTS_PATH / "direct_test_read.properties"), "w") as file:
        file.write("environment=preview")
    with open(str(TESTS_PATH / "direct_test_git.properties"), "w") as file:
        file.write("environment=preview")
    yield

    test_files = [
        "direct_test_read.properties",
        "direct_test_create.properties",
        "direct_test_git.properties",
    ]
    for filename in test_files:
        test_file = TESTS_PATH / filename
        if os.path.exists(test_file):
            os.remove(test_file)


@pytest.mark.regression
@pytest.mark.plugin
@pytest.mark.parametrize(
    "tool_name,prompt,expected_response",
    cli_tools_test_data,
    ids=[f"{row[0]}_{row[1]}" for row in cli_tools_test_data],
)
def test_workflow_with_cli_tools(
    cli_server,
    workflow_utils,
    similarity_check,
    workflow_with_tool,
    tool_name,
    prompt,
    expected_response,
):
    tool_and_state_name = get_random_name()

    _workflow = workflow_with_tool(
        tool_and_state_name, tool_name, integration=cli_server
    )
    response = workflow_utils.execute_workflow(
        _workflow.id, tool_and_state_name, user_input=json.dumps(prompt)
    )

    similarity_check.check_similarity(response, expected_response, 80)


@pytest.mark.regression
@pytest.mark.plugin
@pytest.mark.parametrize(
    "tool_name,prompt,expected_response",
    dev_plugin_tools_test_data,
    ids=[f"{row[0]}_{row[1]}" for row in dev_plugin_tools_test_data],
)
def test_workflow_with_plugin_tools(
    development_plugin,
    workflow_utils,
    similarity_check,
    workflow_with_tool,
    tool_name,
    prompt,
    expected_response,
):
    tool_and_state_name = get_random_name()

    _workflow = workflow_with_tool(
        tool_and_state_name, tool_name, integration=development_plugin
    )
    response = workflow_utils.execute_workflow(
        _workflow.id, tool_and_state_name, user_input=json.dumps(prompt)
    )

    similarity_check.check_similarity(response, expected_response, 80)


@pytest.mark.regression
@pytest.mark.plugin
@pytest.mark.parametrize(
    "tool_name,prompt,expected_response",
    cli_tools_test_data,
    ids=[f"{row[0]}_{row[1]}" for row in cli_tools_test_data],
)
def test_workflow_with_cli_tools_with_hardcoded_args(
    client,
    cli_server,
    workflow_utils,
    similarity_check,
    workflow_with_tool,
    tool_name,
    prompt,
    expected_response,
):
    tool_and_state_name = get_random_name()

    _workflow = workflow_with_tool(
        tool_and_state_name, tool_name, integration=cli_server, tool_args=prompt
    )
    response = workflow_utils.execute_workflow(_workflow.id, tool_and_state_name)

    similarity_check.check_similarity(response, expected_response, 80)


@pytest.mark.regression
@pytest.mark.plugin
@pytest.mark.parametrize(
    "tool_name,prompt,expected_response",
    cli_tools_test_data,
    ids=[f"{row[0]}_{row[1]}" for row in cli_tools_test_data],
)
def test_workflow_with_cli_tools_with_overriding_args(
    cli_server,
    workflow_utils,
    similarity_check,
    workflow_with_tool,
    tool_name,
    prompt,
    expected_response,
):
    tool_and_state_name = get_random_name()

    _workflow = workflow_with_tool(
        tool_and_state_name,
        tool_name,
        integration=cli_server,
        tool_args={"command": "echo 'Test Message'"},
    )
    response = workflow_utils.execute_workflow(
        _workflow.id, tool_and_state_name, user_input=json.dumps(prompt)
    )

    similarity_check.check_similarity(response, expected_response, 80)
