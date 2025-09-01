import pytest

from codemie_test_harness.tests.test_data.vcs_tools_test_data import (
    vcs_tools_test_data,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name
from codemie_test_harness.tests.utils.constants import vcs_integrations


@pytest.mark.regression
@pytest.mark.parametrize(
    "tool_name, prompt, expected_response",
    vcs_tools_test_data,
    ids=[f"{row[0]}" for row in vcs_tools_test_data],
)
@pytest.mark.testcase("EPMCDME-6560, EPMCDME-6563")
def test_workflow_with_vcs_tool(
    request,
    workflow_with_virtual_assistant,
    workflow_utils,
    similarity_check,
    tool_name,
    prompt,
    expected_response,
):
    integration = request.getfixturevalue(vcs_integrations[tool_name])

    assistant_and_state_name = get_random_name()
    test_workflow = workflow_with_virtual_assistant(
        assistant_and_state_name, tool_name, integration=integration
    )

    response = workflow_utils.execute_workflow(
        test_workflow.id, assistant_and_state_name, user_input=prompt
    )

    similarity_check.check_similarity(response, expected_response)
