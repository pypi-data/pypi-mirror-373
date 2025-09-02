import os

import pytest

from codemie_test_harness.tests.enums.tools import Toolkit
from codemie_test_harness.tests.test_data.open_api_tools_test_data import (
    open_api_tools_test_data,
)


@pytest.mark.regression
@pytest.mark.parametrize(
    "tool_name, prompt, expected_response",
    open_api_tools_test_data,
    ids=[f"{row[0]}" for row in open_api_tools_test_data],
)
@pytest.mark.skipif(
    os.getenv("ENV") == "azure", reason="Still have an issue with encoding long strings"
)
def test_workflow_with_assistant_with_open_api_tools(
    assistant,
    workflow_with_assistant,
    open_api_integration,
    workflow_utils,
    similarity_check,
    tool_name,
    prompt,
    expected_response,
):
    assistant = assistant(Toolkit.OPEN_API, tool_name, settings=open_api_integration)

    workflow_with_assistant = workflow_with_assistant(assistant, "Run")
    response = workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name, prompt
    )

    similarity_check.check_similarity(response, expected_response)
