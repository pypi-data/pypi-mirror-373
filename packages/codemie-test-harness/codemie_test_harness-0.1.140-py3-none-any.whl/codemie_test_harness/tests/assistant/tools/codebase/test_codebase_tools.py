import pytest

from codemie_sdk.models.integration import CredentialTypes
from codemie_test_harness.tests.enums.tools import (
    CodeBaseTool,
)
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
def test_assistant_with_codebase_tools(
    assistant_utils,
    assistant,
    code_datasource,
    code_context,
    similarity_check,
    toolkit,
    tool_name,
    prompt,
    expected_response,
):
    assistant = assistant(toolkit, tool_name, context=code_context(code_datasource))
    response = assistant_utils.ask_assistant(assistant, prompt)
    similarity_check.check_similarity(response, expected_response)


@pytest.mark.regression
@pytest.mark.parametrize(
    "toolkit, tool_name, credentials, prompt, expected",
    sonar_tools_test_data,
    ids=[f"{row[0]}_{row[1]}" for row in sonar_tools_test_data],
)
def test_assistant_with_sonar_tools(
    assistant_utils,
    assistant,
    code_datasource,
    integration_utils,
    similarity_check,
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
        settings=settings,
    )

    response = assistant_utils.ask_assistant(assistant, prompt)
    similarity_check.check_similarity(response, expected)
