import copy
import json
import random

import pytest

from codemie_sdk.models.integration import CredentialTypes
from codemie_test_harness.tests.enums.tools import CodeBaseTool
from codemie_test_harness.tests.test_data.direct_tools.codebase_tools_test_data import (
    sonar_tools_test_data,
)
from codemie_test_harness.tests.utils.aws_parameters_store import CredentialsUtil
from codemie_test_harness.tests.utils.base_utils import get_random_name


@pytest.mark.regression
@pytest.mark.parametrize(
    "toolkit, tool_name, prompt, expected_response",
    sonar_tools_test_data,
    ids=[f"{row[1]}" for row in sonar_tools_test_data],
)
def test_workflow_with_sonar_tools_direct(
    workflow_with_tool,
    workflow_utils,
    integration_utils,
    similarity_check,
    toolkit,
    tool_name,
    prompt,
    expected_response,
):
    assistant_and_state_name = get_random_name()
    credential_values = (
        CredentialsUtil.sonar_credentials()
        if tool_name == CodeBaseTool.SONAR
        else CredentialsUtil.sonar_cloud_credentials()
    )

    integration = integration_utils.create_integration(
        CredentialTypes.SONAR, credential_values
    )

    test_workflow = workflow_with_tool(
        assistant_and_state_name,
        CodeBaseTool.SONAR,
        integration=integration,
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id, assistant_and_state_name, user_input=json.dumps(prompt)
    )
    similarity_check.check_similarity(response, expected_response, 80)


@pytest.mark.regression
@pytest.mark.parametrize(
    "toolkit, tool_name, prompt, expected_response",
    sonar_tools_test_data,
    ids=[f"{row[1]}" for row in sonar_tools_test_data],
)
def test_workflow_with_sonar_tools_with_hardcoded_args(
    workflow_with_tool,
    workflow_utils,
    integration_utils,
    similarity_check,
    toolkit,
    tool_name,
    prompt,
    expected_response,
):
    assistant_and_state_name = get_random_name()
    credential_values = (
        CredentialsUtil.sonar_credentials()
        if tool_name == CodeBaseTool.SONAR
        else CredentialsUtil.sonar_cloud_credentials()
    )

    integration = integration_utils.create_integration(
        CredentialTypes.SONAR, credential_values
    )

    test_workflow = workflow_with_tool(
        assistant_and_state_name,
        CodeBaseTool.SONAR,
        integration=integration,
        tool_args=prompt,
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id, assistant_and_state_name
    )
    similarity_check.check_similarity(response, expected_response, 80)


@pytest.mark.regression
@pytest.mark.parametrize(
    "toolkit, tool_name, prompt, expected_response",
    sonar_tools_test_data,
    ids=[f"{row[1]}" for row in sonar_tools_test_data],
)
def test_workflow_with_sonar_tools_with_overriding_args(
    workflow_with_tool,
    workflow_utils,
    integration_utils,
    similarity_check,
    toolkit,
    tool_name,
    prompt,
    expected_response,
):
    assistant_and_state_name = get_random_name()
    credential_values = (
        CredentialsUtil.sonar_credentials()
        if tool_name == CodeBaseTool.SONAR
        else CredentialsUtil.sonar_cloud_credentials()
    )

    integration = integration_utils.create_integration(
        CredentialTypes.SONAR, credential_values
    )

    args_copy = copy.deepcopy(prompt)
    args_copy = {key: random.randint(1, 10) for key in args_copy}

    test_workflow = workflow_with_tool(
        assistant_and_state_name,
        CodeBaseTool.SONAR,
        integration=integration,
        tool_args=args_copy,
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id, assistant_and_state_name, user_input=json.dumps(prompt)
    )
    similarity_check.check_similarity(response, expected_response, 80)
