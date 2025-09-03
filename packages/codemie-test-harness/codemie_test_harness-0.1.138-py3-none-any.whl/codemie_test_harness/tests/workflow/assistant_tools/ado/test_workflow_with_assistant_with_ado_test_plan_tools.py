import pytest

from codemie_test_harness.tests.enums.tools import AzureDevOpsTestPlanTool, Toolkit
from codemie_test_harness.tests.test_data.ado_test_plan_tools_test_data import (
    ado_test_plan_get_test_data,
    ADO_TEST_PLAN_CREATE_TEST_PLAN,
    ADO_TEST_PLAN_CREATE_SUITE,
    ADO_TEST_PLAN_ADD_TEST_CASE,
    ADO_TEST_PLAN_DELETE_SUITE,
    ADO_TEST_PLAN_DELETE_PLAN,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name
from codemie_test_harness.tests.utils.constants import ID_PATTERN
from codemie_test_harness.tests.utils.json_utils import extract_id_from_ado_response


@pytest.mark.regression
@pytest.mark.parametrize(
    "toolkit, tool_name, prompt, expected_response",
    ado_test_plan_get_test_data,
    ids=[f"{row[1]}" for row in ado_test_plan_get_test_data],
)
def test_workflow_with_assistant_with_ado_test_plan_get_tools(
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
def test_workflow_with_assistant_with_ado_test_plan_tools(
    ado_integration,
    assistant,
    similarity_check,
    workflow_with_assistant,
    workflow_utils,
):
    test_plan_title = f"Autotest Test Plan {get_random_name()}"
    assistant = assistant(
        Toolkit.AZURE_DEVOPS_TEST_PLAN,
        (
            AzureDevOpsTestPlanTool.CREATE_TEST_PLAN,
            AzureDevOpsTestPlanTool.CREATE_TEST_SUITE,
            AzureDevOpsTestPlanTool.ADD_TEST_CASE,
            AzureDevOpsTestPlanTool.DELETE_TEST_SUITE,
            AzureDevOpsTestPlanTool.DELETE_TEST_PLAN,
        ),
        settings=ado_integration,
    )
    workflow_with_assistant = workflow_with_assistant(assistant, "Run")

    # 1. Create the test plan
    create_prompt = ADO_TEST_PLAN_CREATE_TEST_PLAN["prompt_to_assistant"].format(
        test_plan_title
    )
    create_response = workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name, create_prompt
    )

    # Extract the test plan ID from the response
    test_plan_id = extract_id_from_ado_response(create_response, ID_PATTERN)
    create_expected = ADO_TEST_PLAN_CREATE_TEST_PLAN["expected_llm_answer"].format(
        test_plan_title, test_plan_id
    )
    similarity_check.check_similarity(create_response, create_expected)

    # Calculate root suite ID (based on the ADO root suite id implementation)
    root_suite_id = int(test_plan_id) + 1

    # 2. Create test suite
    create_suite_prompt = ADO_TEST_PLAN_CREATE_SUITE["prompt_to_assistant"].format(
        root_suite_id, test_plan_id
    )
    create_suite_response = workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name, create_suite_prompt
    )

    # Extract the test suite ID from the response
    test_suite_id = extract_id_from_ado_response(create_suite_response, ID_PATTERN)
    create_suite_expected = ADO_TEST_PLAN_CREATE_SUITE["expected_llm_answer"].format(
        test_suite_id
    )
    similarity_check.check_similarity(create_suite_response, create_suite_expected)

    # 3. Add test case to the suite
    add_case_prompt = ADO_TEST_PLAN_ADD_TEST_CASE["prompt_to_assistant"].format(
        test_suite_id, test_plan_id
    )
    add_case_response = workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name, add_case_prompt
    )
    add_case_expected = ADO_TEST_PLAN_ADD_TEST_CASE["expected_llm_answer"].format(
        test_suite_id, test_plan_id
    )
    similarity_check.check_similarity(add_case_response, add_case_expected)

    # 4. Delete test suite
    delete_suite_prompt = ADO_TEST_PLAN_DELETE_SUITE["prompt_to_assistant"].format(
        test_suite_id, test_plan_id
    )
    delete_suite_response = workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name, delete_suite_prompt
    )
    delete_suite_expected = ADO_TEST_PLAN_DELETE_SUITE["expected_llm_answer"].format(
        test_suite_id, test_plan_id
    )
    similarity_check.check_similarity(delete_suite_response, delete_suite_expected)

    # 5. Delete test plan
    delete_plan_prompt = ADO_TEST_PLAN_DELETE_PLAN["prompt_to_assistant"].format(
        test_plan_id
    )
    delete_plan_response = workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name, delete_plan_prompt
    )
    delete_plan_expected = ADO_TEST_PLAN_DELETE_PLAN["expected_llm_answer"].format(
        test_plan_id
    )
    similarity_check.check_similarity(delete_plan_response, delete_plan_expected)
