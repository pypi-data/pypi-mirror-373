import pytest

from codemie_test_harness.tests.enums.tools import (
    Toolkit,
)
from codemie_test_harness.tests.test_data.vcs_tools_test_data import (
    vcs_tools_test_data,
)
from codemie_test_harness.tests.utils.constants import vcs_integrations


@pytest.mark.regression
@pytest.mark.parametrize(
    "tool_name,prompt,expected_response",
    vcs_tools_test_data,
    ids=[f"{row[0]}" for row in vcs_tools_test_data],
)
def test_create_workflow_with_assistant_vcs_tool(
    request,
    assistant,
    similarity_check,
    workflow_utils,
    workflow_with_assistant,
    tool_name,
    prompt,
    expected_response,
):
    integration = request.getfixturevalue(vcs_integrations[tool_name])

    assistant = assistant(Toolkit.VCS, tool_name, settings=integration)
    workflow_with_assistant = workflow_with_assistant(assistant, prompt)
    response = workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name
    )

    similarity_check.check_similarity(response, expected_response)
