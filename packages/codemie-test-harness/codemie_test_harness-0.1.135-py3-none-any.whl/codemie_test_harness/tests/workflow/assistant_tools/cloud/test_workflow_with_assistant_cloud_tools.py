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
def test_workflow_with_cloud_tools(
    assistant,
    integration_utils,
    similarity_check,
    workflow_with_assistant,
    workflow_utils,
    toolkit,
    tool_name,
    credential_type,
    credentials,
    prompt,
    expected_response,
):
    settings = integration_utils.create_integration(credential_type, credentials)

    assistant = assistant(toolkit, tool_name, settings=settings)
    workflow_with_assistant = workflow_with_assistant(assistant, prompt)
    response = workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name
    )

    similarity_check.check_similarity(response, expected_response)
