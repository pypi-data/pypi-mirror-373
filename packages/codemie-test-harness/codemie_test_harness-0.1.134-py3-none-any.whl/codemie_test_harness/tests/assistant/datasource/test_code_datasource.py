import os

import pytest
from hamcrest import assert_that, equal_to
from requests import HTTPError

from codemie_test_harness.tests.test_data.index_test_data import index_test_data
from codemie_test_harness.tests.utils.base_utils import get_random_name, assert_response


@pytest.mark.regression
@pytest.mark.parametrize(
    "embedding_model",
    index_test_data,
    ids=[f"{row[0][0]}" for row in index_test_data],
)
def test_create_index_application_with_embedding_model(
    git_integration,
    datasource_utils,
    assistant,
    assistant_utils,
    similarity_check,
    code_context,
    embedding_model,
):
    question = "Get repo tree and suggest what programming language repository has?"
    expected_answer = """
        The repository primarily uses Java as the programming language, 
        as indicated by the file paths and extensions such as .java.
    """

    datasource = datasource_utils.create_gitlab_datasource(
        setting_id=git_integration.id, embeddings_model=embedding_model
    )

    assistant = assistant(context=code_context(datasource))

    answer = assistant_utils.ask_assistant(assistant, question)
    similarity_check.check_similarity(answer, expected_answer)

    datasource_utils.update_code_datasource(
        datasource.id, full_reindex=True, skip_reindex=False
    )

    answer = assistant_utils.ask_assistant(assistant, question)
    similarity_check.check_similarity(answer, expected_answer)


@pytest.mark.regression
def test_edit_description_for_code_data_source(
    client,
    gitlab_datasource,
    datasource_utils,
):
    updated_description = get_random_name()

    datasource_utils.update_code_datasource(
        gitlab_datasource.id, description=updated_description
    )

    updated_datasource = client.datasources.get(gitlab_datasource.id)
    assert_that(updated_datasource.description, equal_to(updated_description))


@pytest.mark.regression
def test_create_code_datasource_with_existing_name(gitlab_datasource, datasource_utils):
    datasource = datasource_utils.get_datasource(gitlab_datasource.id)

    try:
        datasource_utils.create_gitlab_datasource(
            name=datasource.name,
            setting_id=datasource.setting_id,
            embeddings_model=datasource.embeddings_model,
        )
        raise AssertionError("There are no error message for duplicate datasource name")
    except HTTPError as e:
        assert_response(
            e.response,
            409,
            f"An index with the name '{datasource.name}' already exists in the project '{os.getenv('PROJECT_NAME')}'.",
        )
