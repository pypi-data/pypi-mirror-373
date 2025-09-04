import pytest

from codemie_sdk.models.assistant import ToolConfig
from codemie_sdk.models.integration import CredentialTypes
from codemie_test_harness.tests.enums.tools import Toolkit, ProjectManagementTool
from codemie_test_harness.tests.test_data.pm_tools_test_data import (
    CONFLUENCE_TOOL_PROMPT,
    RESPONSE_FOR_CONFLUENCE_TOOL,
    JIRA_TOOL_PROMPT,
    RESPONSE_FOR_JIRA_TOOL,
    RESPONSE_FOR_CONFLUENCE_TOOL_UNAUTHORIZED,
)
from codemie_test_harness.tests.test_data.project_management_test_data import (
    pm_tools_test_data,
)
from codemie_test_harness.tests.utils.aws_parameters_store import CredentialsUtil
from codemie_test_harness.tests.utils.base_utils import credentials_to_dict
from codemie_test_harness.tests.utils.constants import (
    project_management_integrations,
)


@pytest.mark.regression
@pytest.mark.parametrize(
    "tool_name, integration_type, prompt, expected_response",
    pm_tools_test_data,
    ids=[f"{row[0]}_{row[1]}" for row in pm_tools_test_data],
)
def test_assistant_with_project_management_tools(
    request,
    assistant,
    assistant_utils,
    similarity_check,
    tool_name,
    integration_type,
    prompt,
    expected_response,
):
    integration = request.getfixturevalue(
        project_management_integrations[integration_type]
    )

    assistant = assistant(
        Toolkit.PROJECT_MANAGEMENT,
        tool_name,
        settings=integration,
    )

    response = assistant_utils.ask_assistant(assistant, prompt)
    similarity_check.check_similarity(response, expected_response)


@pytest.mark.regression
def test_assistant_with_jira_tool_and_integration_id_in_chat(
    assistant, assistant_utils, integration_utils, similarity_check, jira_integration
):
    invalid_settings = integration_utils.create_integration(
        CredentialTypes.JIRA, CredentialsUtil.invalid_jira_credentials()
    )
    tool_config = ToolConfig(
        name=ProjectManagementTool.JIRA, integration_id=jira_integration.id
    )

    assistant = assistant(
        Toolkit.PROJECT_MANAGEMENT,
        ProjectManagementTool.JIRA,
        settings=invalid_settings,
    )

    response = assistant_utils.ask_assistant(
        assistant, JIRA_TOOL_PROMPT, tools_config=[tool_config]
    )
    similarity_check.check_similarity(response, RESPONSE_FOR_JIRA_TOOL)


@pytest.mark.regression
def test_assistant_with_jira_tool_and_credentials_in_chat(
    assistant, assistant_utils, integration_utils, similarity_check
):
    tool_config = ToolConfig(
        name=ProjectManagementTool.JIRA,
        tool_creds=credentials_to_dict(CredentialsUtil.jira_credentials()),
    )

    assistant = assistant(
        Toolkit.PROJECT_MANAGEMENT,
        ProjectManagementTool.JIRA,
    )

    response = assistant_utils.ask_assistant(
        assistant, JIRA_TOOL_PROMPT, tools_config=[tool_config]
    )
    similarity_check.check_similarity(response, RESPONSE_FOR_JIRA_TOOL)


@pytest.mark.regression
def test_assistant_with_confluence_tool_and_integration_id_in_chat(
    assistant,
    assistant_utils,
    integration_utils,
    similarity_check,
    confluence_integration,
):
    invalid_settings = integration_utils.create_integration(
        CredentialTypes.JIRA, CredentialsUtil.invalid_confluence_credentials()
    )
    tool_config = ToolConfig(
        name=ProjectManagementTool.CONFLUENCE, integration_id=confluence_integration.id
    )

    assistant = assistant(
        Toolkit.PROJECT_MANAGEMENT,
        ProjectManagementTool.CONFLUENCE,
        settings=invalid_settings,
    )

    response = assistant_utils.ask_assistant(
        assistant, CONFLUENCE_TOOL_PROMPT, tools_config=[tool_config]
    )
    similarity_check.check_similarity(response, RESPONSE_FOR_CONFLUENCE_TOOL)


@pytest.mark.regression
def test_assistant_with_confluence_tool_and_credentials_in_chat(
    assistant, assistant_utils, integration_utils, similarity_check
):
    tool_config = ToolConfig(
        name=ProjectManagementTool.CONFLUENCE,
        tool_creds=credentials_to_dict(CredentialsUtil.confluence_credentials()),
    )

    assistant = assistant(Toolkit.PROJECT_MANAGEMENT, ProjectManagementTool.CONFLUENCE)

    response = assistant_utils.ask_assistant(
        assistant, CONFLUENCE_TOOL_PROMPT, tools_config=[tool_config]
    )
    similarity_check.check_similarity(response, RESPONSE_FOR_CONFLUENCE_TOOL)


@pytest.mark.regression
@pytest.mark.skip(reason="Test should be fixed")
def test_assistant_with_confluence_tool_and_without_credentials(
    assistant, assistant_utils, similarity_check
):
    assistant = assistant(Toolkit.PROJECT_MANAGEMENT, ProjectManagementTool.CONFLUENCE)

    response = assistant_utils.ask_assistant(assistant, CONFLUENCE_TOOL_PROMPT)
    similarity_check.check_similarity(
        response, RESPONSE_FOR_CONFLUENCE_TOOL_UNAUTHORIZED
    )
