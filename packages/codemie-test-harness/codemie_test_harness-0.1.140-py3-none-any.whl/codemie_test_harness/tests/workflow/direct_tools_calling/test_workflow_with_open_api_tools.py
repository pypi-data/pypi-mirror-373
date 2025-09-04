import copy
import json
import os
import random

import pytest

from codemie_test_harness.tests.test_data.direct_tools.open_api_tools_test_data import (
    open_api_tools_test_data,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name

pytestmark = pytest.mark.skipif(
    os.getenv("ENV") == "azure", reason="Still have an issue with encoding long strings"
)


@pytest.mark.regression
@pytest.mark.testcase("EPMCDME-6560")
@pytest.mark.parametrize(
    "toolkit, tool_name, prompt, expected_response",
    open_api_tools_test_data,
    ids=[f"{row[1]}" for row in open_api_tools_test_data],
)
def test_workflow_with_open_api_tools_direct(
    workflow_with_tool,
    workflow_utils,
    open_api_integration,
    toolkit,
    tool_name,
    prompt,
    expected_response,
    similarity_check,
):
    tool_and_state_name = get_random_name()
    test_workflow = workflow_with_tool(
        tool_and_state_name, tool_name, integration=open_api_integration
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id, tool_and_state_name, json.dumps(prompt)
    )

    similarity_check.check_similarity(response, expected_response, 90)


@pytest.mark.regression
@pytest.mark.testcase("EPMCDME-6560")
@pytest.mark.parametrize(
    "toolkit, tool_name, prompt, expected_response",
    open_api_tools_test_data,
    ids=[f"{row[1]}" for row in open_api_tools_test_data],
)
def test_workflow_with_open_api_tools_with_hardcoded_args(
    workflow_with_tool,
    workflow_utils,
    open_api_integration,
    toolkit,
    tool_name,
    prompt,
    expected_response,
    similarity_check,
):
    tool_and_state_name = get_random_name()
    test_workflow = workflow_with_tool(
        tool_and_state_name,
        tool_name,
        tool_args=prompt,
        integration=open_api_integration,
    )
    response = workflow_utils.execute_workflow(test_workflow.id, tool_and_state_name)

    similarity_check.check_similarity(response, expected_response, 90)


@pytest.mark.regression
@pytest.mark.testcase("EPMCDME-6563")
@pytest.mark.parametrize(
    "toolkit, tool_name, prompt, expected_response",
    open_api_tools_test_data,
    ids=[f"{row[1]}" for row in open_api_tools_test_data],
)
def test_workflow_with_open_api_tools_with_overriding_args(
    workflow_with_tool,
    workflow_utils,
    open_api_integration,
    toolkit,
    tool_name,
    prompt,
    expected_response,
    similarity_check,
):
    tool_and_state_name = get_random_name()

    args_copy = copy.deepcopy(prompt)
    args_copy = {key: random.randint(1, 10) for key in args_copy}

    test_workflow = workflow_with_tool(
        tool_and_state_name,
        tool_name,
        tool_args=args_copy,
        integration=open_api_integration,
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id, tool_and_state_name, json.dumps(prompt)
    )

    similarity_check.check_similarity(response, expected_response, 90)
