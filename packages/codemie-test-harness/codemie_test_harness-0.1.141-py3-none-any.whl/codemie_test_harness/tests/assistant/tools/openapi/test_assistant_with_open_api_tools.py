import os

import pytest

from codemie_test_harness.tests.enums.tools import Toolkit
from codemie_test_harness.tests.test_data.open_api_tools_test_data import (
    open_api_tools_test_data,
)


@pytest.mark.regression
@pytest.mark.parametrize(
    "tool_name,prompt,expected_response",
    open_api_tools_test_data,
    ids=[f"{row[0]}" for row in open_api_tools_test_data],
)
@pytest.mark.testcase("EPMCDME-6127")
@pytest.mark.skipif(
    os.getenv("ENV") == "azure", reason="Still have an issue with encoding long strings"
)
def test_create_assistant_with_open_api_tool(
    assistant_utils,
    assistant,
    similarity_check,
    open_api_integration,
    tool_name,
    prompt,
    expected_response,
):
    assistant_instance = assistant(
        Toolkit.OPEN_API, tool_name, settings=open_api_integration
    )

    response = assistant_utils.ask_assistant(assistant_instance, prompt)

    similarity_check.check_similarity(response, expected_response)
