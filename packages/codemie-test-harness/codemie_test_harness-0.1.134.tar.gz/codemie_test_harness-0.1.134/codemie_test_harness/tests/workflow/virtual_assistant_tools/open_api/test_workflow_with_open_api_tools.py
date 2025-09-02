import os

import pytest

from codemie_test_harness.tests.test_data.open_api_tools_test_data import (
    open_api_tools_test_data,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name


@pytest.mark.regression
@pytest.mark.tescase("EPMCDME-6605")
@pytest.mark.parametrize(
    "tool_name, prompt, expected_response",
    open_api_tools_test_data,
    ids=[f"{row[0]}" for row in open_api_tools_test_data],
)
@pytest.mark.skipif(
    os.getenv("ENV") == "azure", reason="Still have an issue with encoding long strings"
)
def test_workflow_with_open_api_tools(
    workflow_with_virtual_assistant,
    open_api_integration,
    workflow_utils,
    similarity_check,
    tool_name,
    prompt,
    expected_response,
):
    assistant_and_state_name = get_random_name()
    test_workflow = workflow_with_virtual_assistant(
        assistant_and_state_name,
        tool_name,
        integration=open_api_integration,
        task=prompt,
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id, assistant_and_state_name
    )
    similarity_check.check_similarity(response, expected_response)
