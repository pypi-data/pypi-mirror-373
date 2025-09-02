import pytest

from codemie_test_harness.tests.enums.tools import AzureDevOpsWikiTool
from codemie_test_harness.tests.test_data.ado_wiki_tools_test_data import (
    ado_wiki_get_test_data,
    ADO_WIKI_CREATE_PAGE,
    ADO_WIKI_RENAME_PAGE,
    ADO_WIKI_MODIFY_PAGE,
    ADO_WIKI_DELETE_PAGE,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name


@pytest.mark.regression
@pytest.mark.testcase("EPMCDME-5192")
@pytest.mark.parametrize(
    "toolkit, tool_name, prompt, expected_response",
    ado_wiki_get_test_data,
    ids=[f"{row[1]}" for row in ado_wiki_get_test_data],
)
def test_workflow_with_ado_wiki_get_tools(
    ado_integration,
    workflow_with_virtual_assistant,
    workflow_utils,
    similarity_check,
    toolkit,
    tool_name,
    prompt,
    expected_response,
):
    assistant_and_state_name = get_random_name()

    test_workflow = workflow_with_virtual_assistant(
        assistant_and_state_name,
        tool_name,
        integration=ado_integration,
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id, assistant_and_state_name, prompt
    )
    similarity_check.check_similarity(response, expected_response)


@pytest.mark.regression
@pytest.mark.testcase("EPMCDME-5192")
def test_workflow_with_ado_wiki_modify_tools(
    ado_integration,
    workflow_with_virtual_assistant,
    workflow_utils,
    similarity_check,
):
    # 1. Create the page
    page_title = f"Autotest-Page-{get_random_name()}"
    create_prompt = ADO_WIKI_CREATE_PAGE["prompt_to_assistant"].format(page_title)
    create_expected = ADO_WIKI_CREATE_PAGE["expected_llm_answer"].format(page_title)
    assistant_and_state_name = get_random_name()
    create_page_workflow = workflow_with_virtual_assistant(
        assistant_and_state_name,
        AzureDevOpsWikiTool.MODIFY_WIKI_PAGE,
        integration=ado_integration,
    )
    create_response = workflow_utils.execute_workflow(
        create_page_workflow.id, assistant_and_state_name, create_prompt
    )
    similarity_check.check_similarity(create_response, create_expected)

    # 2. Rename the page
    rename_prompt = ADO_WIKI_RENAME_PAGE["prompt_to_assistant"].format(
        page_title, page_title
    )
    rename_expected = ADO_WIKI_RENAME_PAGE["expected_llm_answer"].format(
        page_title, page_title
    )
    assistant_and_state_name = get_random_name()
    rename_page_workflow = workflow_with_virtual_assistant(
        assistant_and_state_name,
        AzureDevOpsWikiTool.RENAME_WIKI_PAGE,
        integration=ado_integration,
    )
    rename_response = workflow_utils.execute_workflow(
        rename_page_workflow.id, assistant_and_state_name, rename_prompt
    )
    similarity_check.check_similarity(rename_response, rename_expected)

    # 3. Modify the page
    modify_prompt = ADO_WIKI_MODIFY_PAGE["prompt_to_assistant"].format(
        page_title + "-Updated"
    )
    modify_expected = ADO_WIKI_MODIFY_PAGE["expected_llm_answer"].format(
        page_title + "-Updated"
    )
    assistant_and_state_name = get_random_name()
    modify_page_workflow = workflow_with_virtual_assistant(
        assistant_and_state_name,
        AzureDevOpsWikiTool.MODIFY_WIKI_PAGE,
        integration=ado_integration,
    )
    modify_response = workflow_utils.execute_workflow(
        modify_page_workflow.id, assistant_and_state_name, modify_prompt
    )
    similarity_check.check_similarity(modify_response, modify_expected)

    # 4. Delete the page
    delete_prompt = ADO_WIKI_DELETE_PAGE["prompt_to_assistant"].format(
        page_title + "-Updated"
    )
    delete_expected = ADO_WIKI_DELETE_PAGE["expected_llm_answer"].format(
        page_title + "-Updated"
    )
    assistant_and_state_name = get_random_name()
    delete_page_workflow = workflow_with_virtual_assistant(
        assistant_and_state_name,
        AzureDevOpsWikiTool.DELETE_WIKI_PAGE_BY_PATH,
        integration=ado_integration,
    )
    delete_response = workflow_utils.execute_workflow(
        delete_page_workflow.id, assistant_and_state_name, delete_prompt
    )
    similarity_check.check_similarity(delete_response, delete_expected)
