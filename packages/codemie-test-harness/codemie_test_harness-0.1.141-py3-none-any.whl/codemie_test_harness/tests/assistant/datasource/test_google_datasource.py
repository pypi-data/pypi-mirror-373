import os

import pytest
from hamcrest import assert_that, equal_to
from requests import HTTPError

from codemie_test_harness.tests.test_data.google_datasource_test_data import (
    GOOGLE_DOC_URL,
    RESPONSE_FOR_GOOGLE_DOC,
    USER_PROMPT,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name, assert_response


@pytest.mark.smoke
@pytest.mark.regression
def test_create_datasource_with_google_integration(
    datasource_utils,
    assistant,
    assistant_utils,
    similarity_check,
    kb_context,
    google_doc_datasource,
):
    assistant = assistant(context=kb_context(google_doc_datasource))

    response_from_llm = assistant_utils.ask_assistant(assistant, USER_PROMPT)
    similarity_check.check_similarity(response_from_llm, RESPONSE_FOR_GOOGLE_DOC)

    datasource_utils.update_google_doc_datasource(
        google_doc_datasource.id, full_reindex=True, skip_reindex=False
    )

    response_from_llm = assistant_utils.ask_assistant(assistant, USER_PROMPT)
    similarity_check.check_similarity(response_from_llm, RESPONSE_FOR_GOOGLE_DOC)


@pytest.mark.regression
@pytest.mark.smoke
def test_edit_description_for_google_data_source(
    client, datasource_utils, google_doc_datasource
):
    updated_description = get_random_name()

    datasource_utils.update_google_doc_datasource(
        google_doc_datasource.id, description=updated_description
    )

    updated_datasource = client.datasources.get(google_doc_datasource.id)
    assert_that(updated_datasource.description, equal_to(updated_description))


@pytest.mark.regression
@pytest.mark.smoke
def test_create_google_doc_datasource_with_existing_name(
    google_doc_datasource, datasource_utils
):
    datasource = datasource_utils.get_datasource(google_doc_datasource.id)

    try:
        datasource_utils.create_google_doc_datasource(
            name=datasource.name, google_doc=GOOGLE_DOC_URL
        )
        raise AssertionError("There are no error message for duplicate datasource name")
    except HTTPError as e:
        assert_response(
            e.response,
            409,
            f"An index with the name '{datasource.name}' already exists in the project '{os.getenv('PROJECT_NAME')}'.",
        )
