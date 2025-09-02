import pytest

from codemie_test_harness.tests.enums.tools import AzureDevOpsWorkItemTool
from codemie_test_harness.tests.test_data.ado_work_item_tools_test_data import (
    ado_work_item_get_test_data,
    ADO_WORK_ITEM_CREATE,
    ADO_WORK_ITEM_UPDATE,
    ADO_WORK_ITEM_LINK,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name
from codemie_test_harness.tests.utils.constants import WORK_ITEM_ID_PATTERN
from codemie_test_harness.tests.utils.json_utils import extract_id_from_ado_response


@pytest.mark.regression
@pytest.mark.testcase("EPMCDME-5384")
@pytest.mark.parametrize(
    "toolkit, tool_name, prompt, expected_response",
    ado_work_item_get_test_data,
    ids=[f"{row[1]}" for row in ado_work_item_get_test_data],
)
def test_workflow_with_ado_work_item_get_tools(
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
@pytest.mark.testcase("EPMCDME-5384")
def test_workflow_with_ado_work_item_modify_tools(
    ado_integration,
    workflow_with_virtual_assistant,
    workflow_utils,
    similarity_check,
):
    # 1. Create the work item
    work_item_title = f"Autotest Task {get_random_name()}"

    create_prompt = ADO_WORK_ITEM_CREATE["prompt_to_assistant"].format(work_item_title)

    create_expected = ADO_WORK_ITEM_CREATE["expected_llm_answer"].format(
        work_item_title
    )
    assistant_and_state_name = get_random_name()
    create_item_workflow = workflow_with_virtual_assistant(
        assistant_and_state_name,
        AzureDevOpsWorkItemTool.CREATE_WORK_ITEM,
        integration=ado_integration,
    )
    create_response = workflow_utils.execute_workflow(
        create_item_workflow.id, assistant_and_state_name, create_prompt
    )
    work_item_id = extract_id_from_ado_response(create_response, WORK_ITEM_ID_PATTERN)
    similarity_check.check_similarity(create_response, create_expected)

    # 2. Update the item
    new_title = f"Autotest Epic {get_random_name()}"
    update_prompt = ADO_WORK_ITEM_UPDATE["prompt_to_assistant"].format(
        work_item_id, new_title
    )

    update_expected = ADO_WORK_ITEM_UPDATE["expected_llm_answer"].format(
        work_item_id, new_title
    )
    assistant_and_state_name = get_random_name()
    update_item_workflow = workflow_with_virtual_assistant(
        assistant_and_state_name,
        AzureDevOpsWorkItemTool.UPDATE_WORK_ITEM,
        integration=ado_integration,
    )
    update_response = workflow_utils.execute_workflow(
        update_item_workflow.id, assistant_and_state_name, update_prompt
    )
    similarity_check.check_similarity(update_response, update_expected)

    # 3. Link the item
    link_prompt = ADO_WORK_ITEM_LINK["prompt_to_assistant"].format(
        work_item_id, work_item_id
    )

    link_expected = ADO_WORK_ITEM_LINK["expected_llm_answer"].format(work_item_id)
    assistant_and_state_name = get_random_name()
    link_item_workflow = workflow_with_virtual_assistant(
        assistant_and_state_name,
        AzureDevOpsWorkItemTool.LINK_WORK_ITEMS,
        integration=ado_integration,
    )
    link_response = workflow_utils.execute_workflow(
        link_item_workflow.id, assistant_and_state_name, link_prompt
    )
    similarity_check.check_similarity(link_response, link_expected)
