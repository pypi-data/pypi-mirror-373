import pytest

from codemie_sdk.models.integration import CredentialTypes
from codemie_test_harness.tests.enums.tools import CodeBaseTool
from codemie_test_harness.tests.test_data.codebase_tools_test_data import (
    code_tools_test_data,
    sonar_tools_test_data,
)


@pytest.mark.regression
@pytest.mark.parametrize(
    "toolkit,tool_name,prompt,expected_response",
    code_tools_test_data,
    ids=[f"{row[0]}_{row[1]}" for row in code_tools_test_data],
)
def test_workflow_with_codebase_tools(
    assistant,
    code_datasource,
    code_context,
    similarity_check,
    workflow_with_assistant,
    workflow_utils,
    toolkit,
    tool_name,
    prompt,
    expected_response,
):
    assistant = assistant(toolkit, tool_name, context=code_context(code_datasource))
    workflow_with_assistant = workflow_with_assistant(assistant, prompt)
    response = workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name
    )

    similarity_check.check_similarity(response, expected_response)


@pytest.mark.regression
@pytest.mark.parametrize(
    "toolkit, tool_name, credentials, prompt,expected",
    sonar_tools_test_data,
    ids=[f"{row[0]}_{row[1]}" for row in sonar_tools_test_data],
)
def test_workflow_with_sonar_tools(
    assistant,
    code_datasource,
    code_context,
    integration_utils,
    similarity_check,
    workflow_with_assistant,
    workflow_utils,
    toolkit,
    tool_name,
    credentials,
    prompt,
    expected,
):
    settings = integration_utils.create_integration(CredentialTypes.SONAR, credentials)

    assistant = assistant(
        toolkit,
        CodeBaseTool.SONAR,
        context=code_context(code_datasource),
        settings=settings,
    )
    workflow_with_assistant = workflow_with_assistant(assistant, prompt)
    response = workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name
    )

    similarity_check.check_similarity(response, expected)
