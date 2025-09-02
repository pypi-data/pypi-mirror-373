import pytest
from codemie_sdk.models.integration import CredentialTypes

from codemie_test_harness.tests.enums.tools import Toolkit, AzureDevOpsWorkItemTool
from codemie_test_harness.tests.test_data.ado_work_item_tools_test_data import (
    ado_work_item_get_test_data,
    ADO_WORK_ITEM_CREATE,
    ADO_WORK_ITEM_UPDATE,
    ADO_WORK_ITEM_LINK,
)
from codemie_test_harness.tests.utils.aws_parameters_store import CredentialsUtil
from codemie_test_harness.tests.utils.base_utils import get_random_name
from codemie_test_harness.tests.utils.constants import WORK_ITEM_ID_PATTERN
from codemie_test_harness.tests.utils.json_utils import extract_id_from_ado_response


@pytest.mark.regression
@pytest.mark.parametrize(
    "toolkit,tool_name,prompt,expected_response",
    ado_work_item_get_test_data,
    ids=[f"{row[0]}_{row[1]}" for row in ado_work_item_get_test_data],
)
def test_assistant_with_ado_work_item_get_tools(
    assistant_utils,
    assistant,
    integration_utils,
    similarity_check,
    toolkit,
    tool_name,
    prompt,
    expected_response,
):
    credential_values = CredentialsUtil.azure_devops_credentials()
    settings = integration_utils.create_integration(
        CredentialTypes.AZURE_DEVOPS, credential_values
    )
    assistant = assistant(
        toolkit,
        tool_name,
        settings=settings,
    )

    response = assistant_utils.ask_assistant(assistant, prompt)
    similarity_check.check_similarity(response, expected_response)


@pytest.mark.regression
def test_assistant_with_ado_work_item_modify_tools(
    assistant_utils,
    assistant,
    integration_utils,
    similarity_check,
):
    credential_values = CredentialsUtil.azure_devops_credentials()
    settings = integration_utils.create_integration(
        CredentialTypes.AZURE_DEVOPS, credential_values
    )
    assistant = assistant(
        Toolkit.AZURE_DEVOPS_WORK_ITEM,
        (
            AzureDevOpsWorkItemTool.CREATE_WORK_ITEM,
            AzureDevOpsWorkItemTool.UPDATE_WORK_ITEM,
            AzureDevOpsWorkItemTool.LINK_WORK_ITEMS,
        ),
        settings=settings,
    )

    work_item_title = f"Autotest Task {get_random_name()}"

    create_prompt = ADO_WORK_ITEM_CREATE["prompt_to_assistant"].format(work_item_title)
    create_response = assistant_utils.ask_assistant(assistant, create_prompt)

    work_item_id = extract_id_from_ado_response(create_response, WORK_ITEM_ID_PATTERN)
    create_expected = ADO_WORK_ITEM_CREATE["expected_llm_answer"].format(
        work_item_title
    )
    similarity_check.check_similarity(create_response, create_expected)

    new_title = f"Autotest Epic {get_random_name()}"
    update_prompt = ADO_WORK_ITEM_UPDATE["prompt_to_assistant"].format(
        work_item_id, new_title
    )
    update_response = assistant_utils.ask_assistant(assistant, update_prompt)

    update_expected = ADO_WORK_ITEM_UPDATE["expected_llm_answer"].format(
        work_item_id, new_title
    )
    similarity_check.check_similarity(update_response, update_expected)

    link_prompt = ADO_WORK_ITEM_LINK["prompt_to_assistant"].format(
        work_item_id, work_item_id
    )
    link_response = assistant_utils.ask_assistant(assistant, link_prompt)

    link_expected = ADO_WORK_ITEM_LINK["expected_llm_answer"].format(work_item_id)
    similarity_check.check_similarity(link_response, link_expected)
