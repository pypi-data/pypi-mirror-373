"""Tests for Confluence datasource operations - Final version."""

import os
import pytest
from hamcrest import assert_that, equal_to
from requests import HTTPError

from codemie_test_harness.tests.test_data.pm_tools_test_data import (
    JIRA_TOOL_PROMPT,
    RESPONSE_FOR_JIRA_TOOL,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name, assert_response


@pytest.mark.regression
def test_create_datasource_with_jira_integration(
    assistant,
    assistant_utils,
    datasource_utils,
    jira_datasource,
    kb_context,
    default_llm,
    similarity_check,
):
    assistant = assistant(context=kb_context(jira_datasource))

    response = assistant_utils.ask_assistant(assistant, JIRA_TOOL_PROMPT)
    similarity_check.check_similarity(response, RESPONSE_FOR_JIRA_TOOL)

    datasource_utils.update_jira_datasource(
        jira_datasource.id, full_reindex=True, skip_reindex=False
    )

    response = assistant_utils.ask_assistant(assistant, JIRA_TOOL_PROMPT)
    similarity_check.check_similarity(response, RESPONSE_FOR_JIRA_TOOL)


@pytest.mark.regression
def test_edit_description_for_jira_data_source(
    client, jira_datasource, datasource_utils
):
    updated_description = get_random_name()

    datasource_utils.update_jira_datasource(
        jira_datasource.id, description=updated_description
    )

    updated_datasource = client.datasources.get(jira_datasource.id)
    assert_that(updated_datasource.description, equal_to(updated_description))


@pytest.mark.regression
def test_create_jira_datasource_with_existing_name(jira_datasource, datasource_utils):
    datasource = datasource_utils.get_datasource(jira_datasource.id)

    try:
        datasource_utils.create_jira_datasource(
            name=datasource.name, setting_id=datasource.setting_id
        )
        raise AssertionError("There are no error message for duplicate datasource name")
    except HTTPError as e:
        assert_response(
            e.response,
            409,
            f"An index with the name '{datasource.name}' already exists in the project '{os.getenv('PROJECT_NAME')}'.",
        )
