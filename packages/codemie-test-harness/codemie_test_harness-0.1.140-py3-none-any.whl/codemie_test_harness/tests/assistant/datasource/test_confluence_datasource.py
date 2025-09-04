"""Tests for Confluence datasource operations - Final version."""

import os

import pytest
from hamcrest import assert_that, equal_to
from requests import HTTPError

from codemie_test_harness.tests.test_data.pm_tools_test_data import (
    CONFLUENCE_TOOL_PROMPT,
    RESPONSE_FOR_CONFLUENCE_TOOL,
    CONFLUENCE_CLOUD_TOOL_PROMPT,
    RESPONSE_FOR_CONFLUENCE_CLOUD_TOOL,
)
from codemie_test_harness.tests.utils.aws_parameters_store import CredentialsUtil
from codemie_test_harness.tests.utils.base_utils import get_random_name, assert_response


@pytest.fixture(scope="function")
def confluence_cloud_datasource(datasource_utils, confluence_cloud_integration):
    datasource = datasource_utils.create_confluence_datasource(
        setting_id=confluence_cloud_integration.id,
        cql=CredentialsUtil.confluence_cloud_jql(),
    )
    yield datasource
    if datasource:
        datasource_utils.delete_datasource(datasource)


@pytest.mark.regression
@pytest.mark.parametrize(
    "datasource_fixture, prompt, expected_response",
    [
        ("confluence_datasource", CONFLUENCE_TOOL_PROMPT, RESPONSE_FOR_CONFLUENCE_TOOL),
        (
            "confluence_cloud_datasource",
            CONFLUENCE_CLOUD_TOOL_PROMPT,
            RESPONSE_FOR_CONFLUENCE_CLOUD_TOOL,
        ),
    ],
    ids=["Confluence", "Confluence Cloud"],
)
def test_create_datasource_with_confluence_and_confluence_cloud_integration(
    request,
    assistant,
    assistant_utils,
    datasource_utils,
    kb_context,
    similarity_check,
    datasource_fixture,
    prompt,
    expected_response,
):
    datasource = request.getfixturevalue(datasource_fixture)
    assistant = assistant(context=kb_context(datasource))

    response = assistant_utils.ask_assistant(assistant, prompt)
    similarity_check.check_similarity(response, expected_response)

    datasource_utils.update_confluence_datasource(
        datasource.id, full_reindex=True, skip_reindex=False
    )

    response = assistant_utils.ask_assistant(assistant, prompt)
    similarity_check.check_similarity(response, expected_response)


@pytest.mark.regression
def test_edit_description_for_confluence_data_source(
    client, confluence_datasource, datasource_utils
):
    updated_description = get_random_name()

    datasource_utils.update_confluence_datasource(
        confluence_datasource.id, description=updated_description
    )

    updated_datasource = client.datasources.get(confluence_datasource.id)
    assert_that(updated_datasource.description, equal_to(updated_description))


@pytest.mark.regression
def test_create_confluence_datasource_with_existing_name(
    datasource_utils, confluence_datasource
):
    datasource = datasource_utils.get_datasource(confluence_datasource.id)

    try:
        datasource_utils.create_confluence_datasource(
            name=datasource.name, setting_id=datasource.setting_id
        )
        raise AssertionError("There are no error message for duplicate datasource name")
    except HTTPError as e:
        assert_response(
            e.response,
            409,
            f"An index with the name '{datasource.name}' already exists in the project '{os.getenv('PROJECT_NAME')}'.",
        )
