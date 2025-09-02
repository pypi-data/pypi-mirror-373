import pytest

from hamcrest import (
    assert_that,
    equal_to,
)
from requests import HTTPError

from codemie_test_harness.tests.test_data.file_test_data import (
    file_test_data,
    large_files_test_data,
    RESPONSE_FOR_TWO_FILES_INDEXED,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name, assert_response
from codemie_test_harness.tests.test_data.index_test_data import index_test_data
from codemie_test_harness.tests.utils.client_factory import get_client
from codemie_test_harness.tests.utils.constants import FILES_PATH
from codemie_test_harness.tests.utils.pytest_utils import check_mark


def pytest_generate_tests(metafunc):
    if "embeddings_model" in metafunc.fixturenames:
        is_smoke = check_mark(metafunc, "smoke")
        if is_smoke:
            all_models = get_client().llms.list_embeddings()
            models = [model.base_name for model in all_models]
        else:
            models = index_test_data

        metafunc.parametrize("embeddings_model", models)

    # Excluding not supported extensions for now
    files_to_exclude = [
        "test.jpg",
        "test.vtt",
        "test.ini",
        "test.gif",
        "test.jpeg",
        "test.png",
    ]
    if (
        "file_name" in metafunc.fixturenames
        and "expected_response" in metafunc.fixturenames
    ):
        test_data = []
        for file_data in file_test_data:
            test_data.append(
                pytest.param(
                    *file_data,  # Unpack the tuple into separate parameters
                    id=f"{file_data[0]}",
                    marks=pytest.mark.skipif(
                        file_data[0] in files_to_exclude,
                        reason=f"Skip {file_data[0]} for indexing test. Will be implemented later",
                    ),
                )
            )

        metafunc.parametrize("file_name,expected_response", test_data)


@pytest.mark.regression
@pytest.mark.smoke
def test_create_assistant_with_file_datasource(
    assistant,
    assistant_utils,
    datasource_utils,
    embeddings_model,
    similarity_check,
    kb_context,
    file_name,
    expected_response,
):
    datasource = datasource_utils.create_file_datasource(
        name=get_random_name(),
        description=f"[Autotest] {file_name} with {embeddings_model} embedding model",
        files=[str(FILES_PATH / file_name)],
        embeddings_model=embeddings_model,
    )

    test_assistant = assistant(context=kb_context(datasource))

    prompt = "Show KB context. Return all information available in the context. Query may be 'Show content of the KB'"
    response = assistant_utils.ask_assistant(test_assistant, prompt)

    similarity_check.check_similarity(
        response, expected_response, assistant_name=test_assistant.name
    )


@pytest.mark.regression
@pytest.mark.smoke
def test_edit_description_for_file_datasource(datasource_utils):
    initial_description = "[Autotest] Initial CSV datasource description"

    datasource = datasource_utils.create_file_datasource(
        name=get_random_name(),
        description=initial_description,
        files=[str(FILES_PATH / "test.csv")],
    )

    assert_that(datasource.description, equal_to(initial_description))

    updated_description = (
        "[Autotest] Updated CSV datasource description with new details"
    )
    updated_datasource = datasource_utils.update_file_datasource(
        datasource.id, name=datasource.name, description=updated_description
    )
    assert_that(updated_datasource.description, equal_to(updated_description))


@pytest.mark.regression
@pytest.mark.smoke
@pytest.mark.parametrize("file_name", large_files_test_data)
def test_create_file_datasource_with_large_files(datasource_utils, file_name):
    try:
        datasource_utils.create_file_datasource(
            name=get_random_name(),
            description="[Autotest] Test datasource with unsupported video-file.mp4",
            files=[str(FILES_PATH / "large-files" / file_name)],
        )
        raise AssertionError("There is no error for large files")
    except HTTPError as e:
        assert_response(
            e.response, 422, "File too large. Maximum size is 104857600 bytes"
        )


@pytest.mark.regression
@pytest.mark.smoke
def test_create_file_datasource_with_big_number_of_files(datasource_utils):
    files = [str(FILES_PATH / "test.txt") for _ in range(11)]

    try:
        datasource_utils.create_file_datasource(
            name=get_random_name(),
            description="[Autotest] Test datasource with unsupported video-file.mp4",
            files=files,
        )
        raise AssertionError("There is no error for large files")
    except HTTPError as e:
        assert_response(e.response, 422, "Too many files. Maximum count is 10")


@pytest.mark.regression
@pytest.mark.smoke
def test_create_file_datasource_with_two_files(
    assistant, assistant_utils, datasource_utils, kb_context, similarity_check
):
    csv_path = FILES_PATH / "test.csv"
    json_path = FILES_PATH / "test.json"

    datasource = datasource_utils.create_file_datasource(
        name=get_random_name(),
        description="[Autotest] Test datasource with two files",
        files=[str(csv_path), str(json_path)],
    )

    test_assistant = assistant(context=kb_context(datasource))

    response = assistant_utils.ask_assistant(
        test_assistant, "What types of data do we have available?"
    )

    similarity_check.check_similarity(response, RESPONSE_FOR_TWO_FILES_INDEXED)
