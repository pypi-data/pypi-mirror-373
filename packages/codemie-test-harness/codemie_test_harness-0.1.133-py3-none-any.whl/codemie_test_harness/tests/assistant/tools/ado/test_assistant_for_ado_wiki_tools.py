import pytest

from codemie_test_harness.tests.enums.tools import Toolkit, AzureDevOpsWikiTool
from codemie_sdk.models.integration import CredentialTypes
from codemie_test_harness.tests.test_data.ado_wiki_tools_test_data import (
    ado_wiki_get_test_data,
    ADO_WIKI_CREATE_PAGE,
    ADO_WIKI_RENAME_PAGE,
    ADO_WIKI_MODIFY_PAGE,
    ADO_WIKI_DELETE_PAGE,
)
from codemie_test_harness.tests.utils.aws_parameters_store import CredentialsUtil
from codemie_test_harness.tests.utils.base_utils import get_random_name


@pytest.mark.regression
@pytest.mark.parametrize(
    "toolkit,tool_name,prompt,expected_response",
    ado_wiki_get_test_data,
    ids=[f"{row[0]}_{row[1]}" for row in ado_wiki_get_test_data],
)
def test_assistant_with_ado_wiki_get_tools(
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
def test_assistant_with_ado_wiki_modify_tools(
    assistant_utils,
    assistant,
    integration_utils,
    similarity_check,
):
    page_title = f"Autotest-Page-{get_random_name()}"
    credential_values = CredentialsUtil.azure_devops_credentials()
    settings = integration_utils.create_integration(
        CredentialTypes.AZURE_DEVOPS, credential_values
    )
    assistant = assistant(
        Toolkit.AZURE_DEVOPS_WIKI,
        (
            AzureDevOpsWikiTool.MODIFY_WIKI_PAGE,
            AzureDevOpsWikiTool.RENAME_WIKI_PAGE,
            AzureDevOpsWikiTool.DELETE_WIKI_PAGE_BY_PATH,
        ),
        settings=settings,
    )

    # 1. Create the page
    create_prompt = ADO_WIKI_CREATE_PAGE["prompt_to_assistant"].format(page_title)
    create_expected = ADO_WIKI_CREATE_PAGE["expected_llm_answer"].format(page_title)
    response = assistant_utils.ask_assistant(assistant, create_prompt)
    similarity_check.check_similarity(response, create_expected)

    # 2. Rename the page
    rename_prompt = ADO_WIKI_RENAME_PAGE["prompt_to_assistant"].format(
        page_title, page_title
    )
    rename_expected = ADO_WIKI_RENAME_PAGE["expected_llm_answer"].format(
        page_title, page_title
    )
    response = assistant_utils.ask_assistant(assistant, rename_prompt)
    similarity_check.check_similarity(response, rename_expected)

    # 3. Modify the page
    modify_prompt = ADO_WIKI_MODIFY_PAGE["prompt_to_assistant"].format(
        page_title + "-Updated"
    )
    modify_expected = ADO_WIKI_MODIFY_PAGE["expected_llm_answer"].format(
        page_title + "-Updated"
    )
    response = assistant_utils.ask_assistant(assistant, modify_prompt)
    similarity_check.check_similarity(response, modify_expected)

    # 4. Delete the page
    delete_prompt = ADO_WIKI_DELETE_PAGE["prompt_to_assistant"].format(
        page_title + "-Updated"
    )
    delete_expected = ADO_WIKI_DELETE_PAGE["expected_llm_answer"].format(
        page_title + "-Updated"
    )
    response = assistant_utils.ask_assistant(assistant, delete_prompt)
    similarity_check.check_similarity(response, delete_expected)
