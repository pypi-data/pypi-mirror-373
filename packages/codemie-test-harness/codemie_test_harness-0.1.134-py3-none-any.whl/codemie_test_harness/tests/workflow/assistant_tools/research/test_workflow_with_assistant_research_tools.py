import pytest
from hamcrest import assert_that, greater_than_or_equal_to

from codemie_test_harness.tests.enums.tools import Toolkit, ResearchToolName
from codemie_test_harness.tests.test_data.research_tools_test_data import (
    search_tools_test_data,
    interactions_tools_test_data,
)
from codemie_test_harness.tests.utils.base_utils import percent_of_relevant_titles


@pytest.mark.regression
@pytest.mark.parametrize(
    "tool_name,prompt,expected_percentage",
    search_tools_test_data,
    ids=[ResearchToolName.GOOGLE_SEARCH, ResearchToolName.TAVILY_SEARCH],
)
def test_workflow_with_search_tools(
    assistant,
    tool_name,
    workflow_utils,
    workflow_with_assistant,
    prompt,
    expected_percentage,
):
    assistant = assistant(Toolkit.RESEARCH, tool_name)
    workflow_with_assistant = workflow_with_assistant(assistant, "Run tool")
    response = workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name, user_input=prompt
    )

    percent = percent_of_relevant_titles(response)

    assert_that(
        percent,
        greater_than_or_equal_to(expected_percentage),
        f"The percentage of relevant titles ({percent}%) is less than {expected_percentage}%",
    )


@pytest.mark.regression
@pytest.mark.parametrize(
    "tool_name,prompt,expected_response",
    interactions_tools_test_data,
    ids=[f"{row[0]}" for row in interactions_tools_test_data],
)
def test_workflow_with_interaction_tools(
    assistant,
    similarity_check,
    tool_name,
    workflow_utils,
    workflow_with_assistant,
    prompt,
    expected_response,
):
    assistant = assistant(Toolkit.RESEARCH, tool_name)
    workflow_with_assistant = workflow_with_assistant(assistant, prompt)
    response = workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name
    )

    similarity_check.check_similarity(response, expected_response)
