import pytest

from codemie_test_harness.tests.enums.tools import Toolkit, CloudTool
from codemie_test_harness.tests.test_data.cloud_tools_test_data import cloud_test_data


@pytest.mark.regression
@pytest.mark.parametrize(
    "toolkit,tool_name,credential_type,credentials,prompt,expected_response",
    cloud_test_data,
    ids=[
        f"{Toolkit.CLOUD}_{CloudTool.AWS}",
        f"{Toolkit.CLOUD}_{CloudTool.AZURE}",
        f"{Toolkit.CLOUD}_{CloudTool.GCP}",
        f"{Toolkit.CLOUD}_{CloudTool.KUBERNETES}",
    ],
)
def test_assistant_with_cloud_tools(
    assistant_utils,
    assistant,
    integration_utils,
    similarity_check,
    toolkit,
    tool_name,
    credential_type,
    credentials,
    prompt,
    expected_response,
):
    settings = integration_utils.create_integration(credential_type, credentials)

    aws_assistant = assistant(toolkit, tool_name, settings=settings)

    response = assistant_utils.ask_assistant(aws_assistant, prompt)

    similarity_check.check_similarity(response, expected_response)
