import copy
import json

import pytest

from codemie_test_harness.tests.enums.tools import NotificationTool
from codemie_test_harness.tests.test_data.direct_tools.notification_tools_test_data import (
    notification_tools_test_data,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name
from codemie_test_harness.tests.utils.constants import notification_integrations


@pytest.mark.regression
@pytest.mark.parametrize(
    "tool, prompt, expected_response",
    notification_tools_test_data,
    ids=[NotificationTool.EMAIL, NotificationTool.TELEGRAM],
)
def test_workflow_with_notification_tools_direct(
    request,
    workflow_utils,
    similarity_check,
    workflow_with_tool,
    tool,
    prompt,
    expected_response,
):
    tool_and_state_name = get_random_name()

    _integration = request.getfixturevalue(notification_integrations[tool])

    _workflow = workflow_with_tool(tool_and_state_name, tool, integration=_integration)

    response = workflow_utils.execute_workflow(
        _workflow.id, tool_and_state_name, user_input=json.dumps(prompt)
    )

    similarity_check.check_similarity(response, expected_response, 80)


@pytest.mark.regression
@pytest.mark.parametrize(
    "tool, prompt, expected_response",
    notification_tools_test_data,
    ids=[NotificationTool.EMAIL, NotificationTool.TELEGRAM],
)
def test_workflow_with_notification_tools_with_hardcoded_args(
    request,
    workflow_utils,
    similarity_check,
    workflow_with_tool,
    tool,
    prompt,
    expected_response,
):
    tool_and_state_name = get_random_name()

    _integration = request.getfixturevalue(notification_integrations[tool])
    _workflow = workflow_with_tool(
        tool_and_state_name, tool, integration=_integration, tool_args=prompt
    )
    response = workflow_utils.execute_workflow(_workflow.id, tool_and_state_name)

    similarity_check.check_similarity(response, expected_response, 80)


@pytest.mark.regression
@pytest.mark.parametrize(
    "tool, prompt, expected_response",
    notification_tools_test_data,
    ids=[NotificationTool.EMAIL, NotificationTool.TELEGRAM],
)
def test_workflow_with_notification_tools_with_overriding_args(
    request,
    workflow_utils,
    similarity_check,
    workflow_with_tool,
    tool,
    prompt,
    expected_response,
):
    tool_and_state_name = get_random_name()

    _integration = request.getfixturevalue(notification_integrations[tool])

    args_copy = copy.deepcopy(prompt) if isinstance(prompt, dict) else prompt
    # Optionally, mutate args_copy as needed for overriding logic
    _workflow = workflow_with_tool(
        tool_and_state_name,
        tool,
        integration=_integration,
        tool_args=args_copy,
    )

    response = workflow_utils.execute_workflow(
        _workflow.id, tool_and_state_name, user_input=json.dumps(prompt)
    )

    similarity_check.check_similarity(response, expected_response, 75)
