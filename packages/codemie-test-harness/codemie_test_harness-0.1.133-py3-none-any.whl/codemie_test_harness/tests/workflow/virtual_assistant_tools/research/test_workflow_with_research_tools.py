import pytest
from hamcrest import assert_that, greater_than

from codemie_test_harness.tests.enums.tools import ResearchToolName
from codemie_test_harness.tests.test_data.research_tools_test_data import (
    search_tools_test_data,
    interactions_tools_test_data,
)
from codemie_test_harness.tests.utils.base_utils import (
    get_random_name,
    percent_of_relevant_titles,
)


@pytest.mark.regression
@pytest.mark.testcase("EPMCDME-6655")
@pytest.mark.parametrize(
    "tool_name, prompt, expected_percentage",
    search_tools_test_data,
    ids=[ResearchToolName.GOOGLE_SEARCH, ResearchToolName.TAVILY_SEARCH],
)
def test_workflow_with_search_tools(
    workflow_with_virtual_assistant,
    workflow_utils,
    tool_name,
    prompt,
    expected_percentage,
):
    assistant_and_state_name = get_random_name()
    test_workflow = workflow_with_virtual_assistant(
        assistant_and_state_name,
        tool_name,
        task=prompt,
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id, assistant_and_state_name
    )
    percent = percent_of_relevant_titles(response)

    assert_that(
        percent,
        greater_than(expected_percentage),
        f"The percentage of relevant titles ({percent}%) is less than {expected_percentage}%",
    )


@pytest.mark.regression
@pytest.mark.testcase("EPMCDME-6655")
@pytest.mark.parametrize(
    "tool_name, prompt, expected_response",
    interactions_tools_test_data,
    ids=[f"{row[0]}" for row in interactions_tools_test_data],
)
def test_workflow_with_interaction_tools(
    workflow_with_virtual_assistant,
    similarity_check,
    workflow_utils,
    tool_name,
    prompt,
    expected_response,
):
    assistant_and_state_name = get_random_name()
    test_workflow = workflow_with_virtual_assistant(
        assistant_and_state_name,
        tool_name,
        task=prompt,
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id, assistant_and_state_name
    )

    similarity_check.check_similarity(response, expected_response)
