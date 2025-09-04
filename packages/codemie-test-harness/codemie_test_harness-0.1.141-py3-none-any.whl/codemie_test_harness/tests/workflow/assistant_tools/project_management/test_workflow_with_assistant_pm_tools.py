import pytest

from codemie_test_harness.tests.enums.tools import Toolkit
from codemie_test_harness.tests.test_data.project_management_test_data import (
    pm_tools_test_data,
)
from codemie_test_harness.tests.utils.constants import (
    project_management_integrations,
)


@pytest.mark.regression
@pytest.mark.parametrize(
    "tool_name, integration_type, prompt, expected_response",
    pm_tools_test_data,
    ids=[f"{row[0]}_{row[1]}" for row in pm_tools_test_data],
)
def test_workflow_with_assistant_with_project_management_tools(
    request,
    assistant,
    integration_utils,
    similarity_check,
    jira_integration,
    workflow_utils,
    workflow_with_assistant,
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

    workflow_with_assistant = workflow_with_assistant(assistant, prompt)
    response = workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name
    )
    similarity_check.check_similarity(response, expected_response)
