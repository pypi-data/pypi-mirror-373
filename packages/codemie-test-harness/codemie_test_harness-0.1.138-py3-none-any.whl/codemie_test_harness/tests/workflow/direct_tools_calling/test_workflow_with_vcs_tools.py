import copy
import json
import random

import pytest

from codemie_test_harness.tests.test_data.direct_tools.vcs_tools_test_data import (
    vcs_tools_test_data,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name
from codemie_test_harness.tests.utils.constants import vcs_integrations


@pytest.mark.regression
@pytest.mark.parametrize(
    "toolkit,tool_name,prompt,expected_response",
    vcs_tools_test_data,
    ids=[f"{row[1]}" for row in vcs_tools_test_data],
)
def test_workflow_with_vcs_tools_direct(
    request,
    workflow_with_tool,
    workflow_utils,
    integration_utils,
    toolkit,
    tool_name,
    prompt,
    expected_response,
    similarity_check,
):
    integration = request.getfixturevalue(vcs_integrations[tool_name])

    assistant_and_state_name = get_random_name()

    test_workflow = workflow_with_tool(
        assistant_and_state_name,
        tool_name,
        integration=integration,
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id, assistant_and_state_name, json.dumps(prompt)
    )

    similarity_check.check_similarity(response, expected_response, 95)


@pytest.mark.regression
@pytest.mark.parametrize(
    "toolkit,tool_name,prompt,expected_response",
    vcs_tools_test_data,
    ids=[f"{row[1]}" for row in vcs_tools_test_data],
)
def test_workflow_with_vcs_tools_with_hardcoded_args(
    request,
    workflow_with_tool,
    workflow_utils,
    integration_utils,
    toolkit,
    tool_name,
    prompt,
    expected_response,
    similarity_check,
):
    integration = request.getfixturevalue(vcs_integrations[tool_name])

    assistant_and_state_name = get_random_name()

    test_workflow = workflow_with_tool(
        assistant_and_state_name,
        tool_name,
        integration=integration,
        tool_args=prompt,
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id, assistant_and_state_name
    )

    similarity_check.check_similarity(response, expected_response, 95)


@pytest.mark.regression
@pytest.mark.parametrize(
    "toolkit,tool_name,prompt,expected_response",
    vcs_tools_test_data,
    ids=[f"{row[1]}" for row in vcs_tools_test_data],
)
def test_workflow_with_vcs_tools_with_overriding_args(
    request,
    workflow_with_tool,
    workflow_utils,
    integration_utils,
    toolkit,
    tool_name,
    prompt,
    expected_response,
    similarity_check,
):
    integration = request.getfixturevalue(vcs_integrations[tool_name])

    assistant_and_state_name = get_random_name()

    args_copy = copy.deepcopy(prompt)
    args_copy = {key: random.randint(1, 10) for key in args_copy}

    test_workflow = workflow_with_tool(
        assistant_and_state_name,
        tool_name,
        integration=integration,
        tool_args=args_copy,
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id, assistant_and_state_name, json.dumps(prompt)
    )

    similarity_check.check_similarity(response, expected_response, 95)
