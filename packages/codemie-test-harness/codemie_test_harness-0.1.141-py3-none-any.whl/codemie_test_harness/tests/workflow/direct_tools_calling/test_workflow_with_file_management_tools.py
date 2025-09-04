import copy
import json

import pytest

from codemie_test_harness.tests.test_data.direct_tools.file_management_tools_test_data import (
    file_management_tools_test_data,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name


@pytest.mark.regression
@pytest.mark.parametrize(
    "tool, prompt, expected_response",
    file_management_tools_test_data,
    ids=[f"{row[0]}" for row in file_management_tools_test_data],
)
def test_workflow_with_file_management_tools_direct(
    filesystem_integration,
    workflow_utils,
    similarity_check,
    workflow_with_tool,
    tool,
    prompt,
    expected_response,
):
    tool_and_state_name = get_random_name()
    _workflow = workflow_with_tool(
        tool_and_state_name, tool, integration=filesystem_integration
    )
    response = workflow_utils.execute_workflow(
        _workflow.id, tool_and_state_name, user_input=json.dumps(prompt)
    )
    similarity_check.check_similarity(response, expected_response, 85)


@pytest.mark.regression
@pytest.mark.parametrize(
    "tool, prompt, expected_response",
    file_management_tools_test_data,
    ids=[f"{row[0]}" for row in file_management_tools_test_data],
)
def test_workflow_with_file_management_tools_with_hardcoded_args(
    filesystem_integration,
    workflow_utils,
    similarity_check,
    workflow_with_tool,
    tool,
    prompt,
    expected_response,
):
    tool_and_state_name = get_random_name()
    _workflow = workflow_with_tool(
        tool_and_state_name, tool, integration=filesystem_integration, tool_args=prompt
    )
    response = workflow_utils.execute_workflow(_workflow.id, tool_and_state_name)

    similarity_check.check_similarity(response, expected_response, 85)


@pytest.mark.regression
@pytest.mark.parametrize(
    "tool, prompt, expected_response",
    file_management_tools_test_data,
    ids=[f"{row[0]}" for row in file_management_tools_test_data],
)
def test_workflow_with_file_management_tools_with_overriding_args(
    filesystem_integration,
    workflow_utils,
    similarity_check,
    workflow_with_tool,
    tool,
    prompt,
    expected_response,
):
    tool_and_state_name = get_random_name()
    args_copy = copy.deepcopy(prompt) if isinstance(prompt, dict) else prompt
    # Optionally, mutate args_copy as needed for overriding logic
    _workflow = workflow_with_tool(
        tool_and_state_name,
        tool,
        integration=filesystem_integration,
        tool_args=args_copy,
    )
    response = workflow_utils.execute_workflow(
        _workflow.id, tool_and_state_name, user_input=json.dumps(prompt)
    )
    similarity_check.check_similarity(response, expected_response, 85)
