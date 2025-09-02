import pytest

from codemie_test_harness.tests.enums.tools import Toolkit, ServiceNowTool
from codemie_test_harness.tests.test_data.servicenow_tools_test_data import (
    PROMPT,
    EXPECTED_RESPONSE,
)


@pytest.mark.regression
def test_assistant_with_servicenow_tools(
    assistant_utils,
    assistant,
    service_now_integration,
    similarity_check,
):
    servicenow_assistant = assistant(
        Toolkit.SERVICENOW, ServiceNowTool.SERVICE_NOW, settings=service_now_integration
    )

    response = assistant_utils.ask_assistant(servicenow_assistant, PROMPT)

    similarity_check.check_similarity(response, EXPECTED_RESPONSE, 80)
