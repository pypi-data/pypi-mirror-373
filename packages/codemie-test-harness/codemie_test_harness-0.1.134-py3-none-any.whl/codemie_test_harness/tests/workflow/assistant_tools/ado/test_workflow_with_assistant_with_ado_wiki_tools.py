import pytest

from codemie_test_harness.tests.enums.tools import AzureDevOpsWikiTool, Toolkit
from codemie_test_harness.tests.test_data.ado_wiki_tools_test_data import (
    ado_wiki_get_test_data,
    ADO_WIKI_CREATE_PAGE,
    ADO_WIKI_RENAME_PAGE,
    ADO_WIKI_MODIFY_PAGE,
    ADO_WIKI_DELETE_PAGE,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name


@pytest.mark.regression
@pytest.mark.parametrize(
    "toolkit, tool_name, prompt, expected_response",
    ado_wiki_get_test_data,
    ids=[f"{row[1]}" for row in ado_wiki_get_test_data],
)
def test_workflow_with_assistant_with_ado_wiki_get_tools(
    ado_integration,
    assistant,
    similarity_check,
    workflow_with_assistant,
    workflow_utils,
    toolkit,
    tool_name,
    prompt,
    expected_response,
):
    assistant = assistant(toolkit, tool_name, settings=ado_integration)
    workflow_with_assistant = workflow_with_assistant(assistant, prompt)
    response = workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name
    )

    similarity_check.check_similarity(response, expected_response)


@pytest.mark.regression
def test_workflow_with_assistant_with_ado_wiki_modify_tools(
    ado_integration,
    assistant,
    similarity_check,
    workflow_with_assistant,
    workflow_utils,
):
    assistant = assistant(
        Toolkit.AZURE_DEVOPS_WIKI,
        (
            AzureDevOpsWikiTool.MODIFY_WIKI_PAGE,
            AzureDevOpsWikiTool.RENAME_WIKI_PAGE,
            AzureDevOpsWikiTool.DELETE_WIKI_PAGE_BY_PATH,
        ),
        settings=ado_integration,
    )
    workflow_with_assistant = workflow_with_assistant(assistant, "Run")

    # 1. Create the page
    page_title = f"Autotest-Page-{get_random_name()}"
    create_prompt = ADO_WIKI_CREATE_PAGE["prompt_to_assistant"].format(page_title)
    create_expected = ADO_WIKI_CREATE_PAGE["expected_llm_answer"].format(page_title)
    create_response = workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name, create_prompt
    )
    similarity_check.check_similarity(create_response, create_expected)

    # 2. Rename the page
    rename_prompt = ADO_WIKI_RENAME_PAGE["prompt_to_assistant"].format(
        page_title, page_title
    )
    rename_expected = ADO_WIKI_RENAME_PAGE["expected_llm_answer"].format(
        page_title, page_title
    )
    rename_response = workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name, rename_prompt
    )
    similarity_check.check_similarity(rename_response, rename_expected)

    # 3. Modify the page
    modify_prompt = ADO_WIKI_MODIFY_PAGE["prompt_to_assistant"].format(
        page_title + "-Updated"
    )
    modify_expected = ADO_WIKI_MODIFY_PAGE["expected_llm_answer"].format(
        page_title + "-Updated"
    )
    modify_response = workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name, modify_prompt
    )
    similarity_check.check_similarity(modify_response, modify_expected)

    # 4. Delete the page
    delete_prompt = ADO_WIKI_DELETE_PAGE["prompt_to_assistant"].format(
        page_title + "-Updated"
    )
    delete_expected = ADO_WIKI_DELETE_PAGE["expected_llm_answer"].format(
        page_title + "-Updated"
    )
    delete_response = workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name, delete_prompt
    )
    similarity_check.check_similarity(delete_response, delete_expected)
