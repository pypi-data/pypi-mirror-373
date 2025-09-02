import pytest

from codemie_test_harness.tests.enums.tools import Toolkit, CloudTool
from codemie_test_harness.tests.test_data.cloud_tools_test_data import cloud_test_data
from codemie_test_harness.tests.utils.base_utils import get_random_name


@pytest.mark.regression
@pytest.mark.tescase("EPMCDME-5093")
@pytest.mark.tescase("EPMCDME-5136")
@pytest.mark.tescase("EPMCDME-5135")
@pytest.mark.parametrize(
    "toolkit, tool_name, credential_type, credentials, prompt, expected_response",
    cloud_test_data,
    ids=[
        f"{Toolkit.CLOUD}_{CloudTool.AWS}",
        f"{Toolkit.CLOUD}_{CloudTool.AZURE}",
        f"{Toolkit.CLOUD}_{CloudTool.GCP}",
        f"{Toolkit.CLOUD}_{CloudTool.KUBERNETES}",
    ],
)
def test_workflow_with_cloud_tools(
    workflow_with_virtual_assistant,
    cloud_integration,
    workflow_utils,
    similarity_check,
    toolkit,
    tool_name,
    credential_type,
    credentials,
    prompt,
    expected_response,
):
    assistant_and_state_name = get_random_name()

    integration = cloud_integration(credential_type, credentials)

    test_workflow = workflow_with_virtual_assistant(
        assistant_and_state_name,
        tool_name,
        integration=integration,
        task=prompt,
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id, assistant_and_state_name
    )
    similarity_check.check_similarity(response, expected_response)
