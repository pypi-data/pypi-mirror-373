from time import sleep
import pytest
from hamcrest import (
    assert_that,
    all_of,
    instance_of,
    is_not,
    equal_to,
    less_than_or_equal_to,
    has_length,
    empty,
    any_of,
    has_property,
    greater_than,
)

from codemie_sdk.models.integration import (
    Integration,
    CredentialTypes,
    CredentialValues,
    IntegrationType,
)
from codemie_test_harness.tests import PROJECT, GITHUB_URL
from codemie_test_harness.tests.utils.base_utils import get_random_name


def test_list_project_integrations_minimal_response(search_utils):
    integrations = search_utils.list_integrations(setting_type=IntegrationType.PROJECT)
    assert_that(integrations, all_of(instance_of(list), has_length(greater_than(0))))

    for integration in integrations:
        assert_that(
            integration,
            all_of(
                instance_of(Integration),
                has_property("project_name", has_length(greater_than(0))),
                has_property("credential_type", is_not(any_of(None, empty()))),
                has_property("credential_values", has_length(greater_than(0))),
                has_property("setting_type", equal_to(IntegrationType.PROJECT)),
            ),
        )


def test_list_user_integrations_minimal_response(search_utils):
    integrations = search_utils.list_integrations()
    assert_that(integrations, all_of(instance_of(list), has_length(greater_than(0))))

    for integration in integrations:
        assert_that(
            integration,
            all_of(
                instance_of(Integration),
                has_property("project_name", is_not(None)),
                has_property("credential_type", is_not(any_of(None, empty()))),
                has_property("credential_values", has_length(greater_than(0))),
                has_property("setting_type", equal_to(IntegrationType.USER)),
            ),
        )


def test_list_integrations_with_filters(search_utils):
    filters = {"type": CredentialTypes.GIT}

    project_integrations = search_utils.list_integrations(
        setting_type=IntegrationType.PROJECT, filters=filters
    )
    for integration in project_integrations:
        assert_that(
            integration,
            all_of(
                has_property("credential_type", equal_to(CredentialTypes.GIT)),
                has_property("setting_type", equal_to(IntegrationType.PROJECT)),
            ),
        )

    user_integrations = search_utils.list_integrations(
        setting_type=IntegrationType.USER, filters=filters
    )
    for integration in user_integrations:
        assert_that(
            integration,
            all_of(
                has_property("credential_type", equal_to(CredentialTypes.GIT)),
                has_property("setting_type", equal_to(IntegrationType.USER)),
            ),
        )


def test_list_integrations_with_pagination(search_utils):
    for setting_type in [IntegrationType.PROJECT, IntegrationType.USER]:
        # Get first page with 5 items
        page_1 = search_utils.list_integrations(
            setting_type=setting_type, page=0, per_page=5
        )
        assert_that(len(page_1), less_than_or_equal_to(5))

        # Get second page with 5 items
        page_2 = search_utils.list_integrations(
            setting_type=setting_type, page=1, per_page=5
        )
        assert_that(len(page_2), less_than_or_equal_to(5))

        # Verify pages contain different integrations
        if page_1 and page_2:
            assert_that(page_1[0].id, is_not(equal_to(page_2[0].id)))


@pytest.mark.parametrize(
    "setting_type", [IntegrationType.PROJECT, IntegrationType.USER]
)
def test_integration_full_lifecycle(integration_utils, setting_type: IntegrationType):
    test_project = PROJECT
    test_alias = get_random_name()

    create_request = Integration(
        project_name=test_project,
        credential_type=CredentialTypes.GIT,
        credential_values=[
            CredentialValues(key="url", value="https://github.com/test/repo"),
            CredentialValues(key="token_name", value="test-token-name"),
            CredentialValues(key="token", value="test-token"),
        ],
        alias=test_alias,
        setting_type=setting_type,
    )

    created = integration_utils.send_create_integration_request(create_request)

    assert_that(created, is_not(None))
    sleep(5)  # Verify integration creation

    found_integration = integration_utils.get_integration_by_alias(
        integration_alias=test_alias, integration_type=setting_type
    )

    assert_that(
        found_integration,
        all_of(
            has_property("alias", equal_to(test_alias)),
            has_property("setting_type", equal_to(setting_type)),
        ),
    )
    assert_that(found_integration.credential_values[0].value, equal_to(GITHUB_URL))
    assert_that(
        found_integration.credential_values[1].value, equal_to("test-token-name")
    )

    # Updating the integration
    updated_alias = f"{test_alias} Updated"
    update_request = Integration(
        id=found_integration.id,
        project_name=test_project,
        credential_type=CredentialTypes.GIT,
        credential_values=[
            CredentialValues(key="url", value="https://github.com/test/repo-updated"),
            CredentialValues(key="token_name", value="test-token-name-updated"),
        ],
        alias=updated_alias,
        setting_type=setting_type,
    )

    updated = integration_utils.update_integration(update_request)

    assert_that(updated, is_not(None))
    sleep(5)

    updated_integration = integration_utils.get_integration_by_alias(
        integration_alias=updated_alias, integration_type=setting_type
    )
    assert_that(
        updated_integration,
        all_of(
            has_property("id", equal_to(found_integration.id)),
            has_property("alias", equal_to(updated_alias)),
            has_property("setting_type", equal_to(setting_type)),
        ),
    )
    assert_that(
        updated_integration.credential_values[0].value,
        equal_to(GITHUB_URL),
    )
    assert_that(
        updated_integration.credential_values[1].value,
        equal_to("test-token-name-updated"),
    )


@pytest.mark.parametrize(
    "setting_type", [IntegrationType.PROJECT, IntegrationType.USER]
)
def test_create_integration_with_invalid_data(
    integration_utils, setting_type: IntegrationType
):
    with pytest.raises(Exception):
        invalid_request = Integration(
            project_name="",  # Invalid - empty project name
            credential_type=CredentialTypes.GIT,
            credential_values=[],  # Invalid - empty credentials
            setting_type=setting_type,
        )
        integration_utils.send_create_integration_request(invalid_request)


@pytest.mark.parametrize(
    "setting_type", [IntegrationType.PROJECT, IntegrationType.USER]
)
def test_update_integration_with_invalid_data(
    search_utils, integration_utils, setting_type: IntegrationType
):
    integrations = search_utils.list_integrations(setting_type=setting_type)
    assert_that(integrations, has_length(greater_than(0)))

    with pytest.raises(Exception):
        invalid_request = Integration(
            id=integrations[0].id,
            project_name="",  # Invalid - empty project name
            credential_type=CredentialTypes.GIT,
            credential_values=[],  # Invalid - empty credentials
            setting_type=setting_type,
        )
        integration_utils.update_integration(invalid_request)
