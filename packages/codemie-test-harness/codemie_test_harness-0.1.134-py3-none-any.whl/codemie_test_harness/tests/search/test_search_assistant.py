import pytest
from hamcrest import assert_that

from codemie_test_harness.tests import TEST_USER
from codemie_test_harness.tests.utils.base_utils import get_random_name
from codemie_test_harness.tests.utils.pytest_utils import check_mark


@pytest.fixture(scope="session")
def test_assistant_name():
    base_name = get_random_name()
    return f"{base_name}_assistant_for_search_test"


@pytest.fixture(scope="session")
def test_assistant_partial_name(test_assistant_name):
    return test_assistant_name[:8]


@pytest.fixture(scope="session", autouse=True)
def assistant(assistant_utils, default_llm, test_assistant_name):
    assistant = assistant_utils.create_assistant(
        assistant_name=test_assistant_name,
        shared=True,
        llm_model_type=default_llm.base_name,
    )
    yield assistant
    if assistant:
        assistant_utils.delete_assistant(assistant)


@pytest.fixture(scope="session")
def test_data(test_assistant_name, test_assistant_partial_name):
    return [
        {"search": test_assistant_name},
        {"created_by": TEST_USER, "search": test_assistant_name},
        {"created_by": TEST_USER},
        {"shared": True, "search": test_assistant_name},
        {"is_global": False, "search": test_assistant_name},
        {"search": test_assistant_partial_name},
        {"created_by": TEST_USER, "search": test_assistant_partial_name},
        {"shared": True, "search": test_assistant_partial_name},
        {"is_global": False, "search": test_assistant_partial_name},
    ]


@pytest.fixture
def filters(request, test_data):
    return test_data[request.param]


def pytest_generate_tests(metafunc):
    if "filters" in metafunc.fixturenames:
        is_smoke = check_mark(metafunc, "smoke")

        all_test_cases = [
            {"index": 0, "id": "search_full_name", "smoke": True},
            {"index": 1, "id": "created_by_and_search_full", "smoke": False},
            {"index": 2, "id": "created_by_only", "smoke": False},
            {"index": 3, "id": "shared_and_search_full", "smoke": True},
            {"index": 4, "id": "not_global_and_search_full", "smoke": True},
            {"index": 5, "id": "search_partial_name", "smoke": True},
            {"index": 6, "id": "created_by_and_search_partial", "smoke": False},
            {"index": 7, "id": "shared_and_search_partial", "smoke": True},
            {"index": 8, "id": "not_global_and_search_partial", "smoke": True},
        ]

        if is_smoke:
            test_cases = [case for case in all_test_cases if case["smoke"]]
        else:
            test_cases = all_test_cases

        indices = [case["index"] for case in test_cases]
        ids = [case["id"] for case in test_cases]

        metafunc.parametrize(
            "filters",
            indices,
            ids=ids,
            indirect=True,
        )


@pytest.mark.testcase("EPMCDME-2429, EPMCDME-4102")
@pytest.mark.regression
@pytest.mark.smoke
def test_search_assistant_by_filters(search_utils, filters, test_assistant_name):
    response = search_utils.list_assistants(filters)
    names = list(map(lambda item: item["name"], response))

    assert_that(
        test_assistant_name in names, "Assistant is not found in search results."
    )
