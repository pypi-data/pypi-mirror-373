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
@pytest.mark.testcase("EPMCDME-5803, EPMCDME-5804")
def test_create_assistant_with_vcs_tool(
    request,
    assistant_utils,
    assistant,
    similarity_check,
    tool_name,
    prompt,
    expected_response,
):
    integration = request.getfixturevalue(vcs_integrations[tool_name])

    assistant = assistant(Toolkit.VCS, tool_name, settings=integration)

    response = assistant_utils.ask_assistant(assistant, prompt)

    similarity_check.check_similarity(response, expected_response)
