import random

import pytest
import json
import copy

from hamcrest import equal_to, assert_that

from codemie_test_harness.tests.enums.tools import ServiceNowTool
from codemie_test_harness.tests.test_data.direct_tools.servicenow_tools_test_data import (
    EXPECTED_RESPONSE,
    PROMPT,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name


@pytest.mark.regression
def test_workflow_with_servicenow_tools_direct(
    service_now_integration, workflow_utils, workflow_with_tool
):
    assistant_and_state_name = get_random_name()

    test_workflow = workflow_with_tool(
        assistant_and_state_name,
        ServiceNowTool.SERVICE_NOW,
        integration=service_now_integration,
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id, assistant_and_state_name, user_input=json.dumps(PROMPT)
    )
    assert_that(json.loads(response), equal_to(EXPECTED_RESPONSE))


@pytest.mark.regression
def test_workflow_with_servicenow_tools_with_hardcoded_args(
    service_now_integration, workflow_utils, workflow_with_tool
):
    assistant_and_state_name = get_random_name()

    test_workflow = workflow_with_tool(
        assistant_and_state_name,
        ServiceNowTool.SERVICE_NOW,
        integration=service_now_integration,
        tool_args=PROMPT,
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id, assistant_and_state_name
    )
    assert_that(json.loads(response), equal_to(EXPECTED_RESPONSE))


@pytest.mark.regression
def test_workflow_with_servicenow_tools_with_overriding_args(
    service_now_integration, workflow_utils, workflow_with_tool
):
    assistant_and_state_name = get_random_name()

    args_copy = copy.deepcopy(PROMPT)
    args_copy = {key: random.randint(1, 10) for key in args_copy}

    test_workflow = workflow_with_tool(
        assistant_and_state_name,
        ServiceNowTool.SERVICE_NOW,
        integration=service_now_integration,
        tool_args=args_copy,
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id, assistant_and_state_name, user_input=json.dumps(PROMPT)
    )
    assert_that(json.loads(response), equal_to(EXPECTED_RESPONSE))
