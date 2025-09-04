import copy
import json
import random

import pytest

from codemie_test_harness.tests.test_data.direct_tools.ado_test_plan_tools_test_data import (
    ado_test_plan_get_test_data,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name


@pytest.mark.regression
@pytest.mark.parametrize(
    "toolkit,tool_name,prompt,expected_response",
    ado_test_plan_get_test_data,
    ids=[f"{row[1]}" for row in ado_test_plan_get_test_data],
)
def test_workflow_with_ado_test_plan_get_tools_direct(
    ado_integration,
    workflow_utils,
    similarity_check,
    workflow_with_tool,
    toolkit,
    tool_name,
    prompt,
    expected_response,
):
    tool_and_state_name = get_random_name()

    _workflow = workflow_with_tool(
        tool_and_state_name, tool_name, integration=ado_integration
    )
    response = workflow_utils.execute_workflow(
        _workflow.id, tool_and_state_name, user_input=json.dumps(prompt)
    )

    similarity_check.check_similarity(response, expected_response, 95)


@pytest.mark.regression
@pytest.mark.parametrize(
    "toolkit,tool_name,prompt,expected_response",
    ado_test_plan_get_test_data,
    ids=[f"{row[1]}_hardcoded" for row in ado_test_plan_get_test_data],
)
def test_workflow_with_ado_test_plan_get_tools_with_hardcoded_args(
    ado_integration,
    workflow_utils,
    similarity_check,
    workflow_with_tool,
    toolkit,
    tool_name,
    prompt,
    expected_response,
):
    tool_and_state_name = get_random_name()

    _workflow = workflow_with_tool(
        tool_and_state_name, tool_name, integration=ado_integration, tool_args=prompt
    )
    response = workflow_utils.execute_workflow(_workflow.id, tool_and_state_name)

    similarity_check.check_similarity(response, expected_response, 95)


@pytest.mark.regression
@pytest.mark.parametrize(
    "toolkit,tool_name,prompt,expected_response",
    ado_test_plan_get_test_data,
    ids=[f"{row[1]}_overriding" for row in ado_test_plan_get_test_data],
)
def test_workflow_with_ado_test_plan_get_tools_with_overriding_args(
    ado_integration,
    workflow_utils,
    similarity_check,
    workflow_with_tool,
    toolkit,
    tool_name,
    prompt,
    expected_response,
):
    tool_and_state_name = get_random_name()

    args_copy = copy.deepcopy(prompt)
    args_copy = {key: random.randint(1, 10) for key in args_copy}

    _workflow = workflow_with_tool(
        tool_and_state_name, tool_name, integration=ado_integration, tool_args=args_copy
    )
    response = workflow_utils.execute_workflow(
        _workflow.id, tool_and_state_name, user_input=json.dumps(prompt)
    )

    similarity_check.check_similarity(response, expected_response, 95)
