import pytest
from hamcrest import assert_that, greater_than

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
def test_assistant_with_search_tools(
    assistant,
    assistant_utils,
    tool_name,
    prompt,
    expected_percentage,
):
    assistant = assistant(Toolkit.RESEARCH, tool_name)

    response = assistant_utils.ask_assistant(assistant, prompt)

    percent = percent_of_relevant_titles(response)

    assert_that(
        percent,
        greater_than(expected_percentage),
        f"The percentage of relevant titles ({percent}%) is less than {expected_percentage}%",
    )


@pytest.mark.regression
@pytest.mark.parametrize(
    "tool_name,prompt,expected_response",
    interactions_tools_test_data,
    ids=[f"{row[0]}" for row in interactions_tools_test_data],
)
def test_assistant_with_interaction_tools(
    assistant,
    assistant_utils,
    similarity_check,
    tool_name,
    prompt,
    expected_response,
):
    assistant = assistant(Toolkit.RESEARCH, tool_name)

    response = assistant_utils.ask_assistant(assistant, prompt)
    similarity_check.check_similarity(response, expected_response)
