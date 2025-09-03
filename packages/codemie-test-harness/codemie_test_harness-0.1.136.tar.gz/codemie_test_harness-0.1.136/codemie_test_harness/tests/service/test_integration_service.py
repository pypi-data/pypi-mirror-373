"""Integration tests for IntegrationService."""

from time import sleep

import pytest

from codemie_sdk import CodeMieClient
from codemie_sdk.models.integration import (
    Integration,
    CredentialTypes,
    CredentialValues,
    IntegrationType,
)
from codemie_test_harness.tests import PROJECT
from codemie_test_harness.tests.utils.base_utils import get_random_name


def test_list_project_integrations_minimal(client: CodeMieClient):
    """Test listing project integrations with minimal response."""
    # Get list of project integrations
    integrations = client.integrations.list(setting_type=IntegrationType.PROJECT)

    # Verify we got a list of integrations
    assert isinstance(integrations, list)

    # Verify each integration has the correct type and required fields
    for integration in integrations:
        assert isinstance(integration, Integration)
        assert integration.project_name is not None
        assert integration.credential_type is not None
        assert isinstance(integration.credential_values, list)
        assert integration.setting_type == IntegrationType.PROJECT


def test_list_user_integrations_minimal(client: CodeMieClient):
    """Test listing user integrations with minimal response."""
    # Get list of user integrations
    integrations = client.integrations.list(setting_type=IntegrationType.USER)

    # Verify we got a list of integrations
    assert isinstance(integrations, list)

    # Verify each integration has the correct type and required fields
    for integration in integrations:
        assert isinstance(integration, Integration)
        assert integration.project_name is not None
        assert integration.credential_type is not None
        assert isinstance(integration.credential_values, list)
        assert integration.setting_type == IntegrationType.USER


def test_list_integrations_with_filters(client: CodeMieClient):
    """Test listing integrations with filters for both types."""
    # Test project integrations with filters
    filters = {"type": CredentialTypes.GIT}
    project_integrations = client.integrations.list(
        setting_type=IntegrationType.PROJECT, filters=filters
    )

    for integration in project_integrations:
        assert integration.credential_type == CredentialTypes.GIT
        assert integration.setting_type == IntegrationType.PROJECT

    # Test user integrations with filters
    user_integrations = client.integrations.list(
        setting_type=IntegrationType.USER, filters=filters
    )

    for integration in user_integrations:
        assert integration.credential_type == CredentialTypes.GIT
        assert integration.setting_type == IntegrationType.USER


def test_list_integrations_pagination(client: CodeMieClient):
    """Test integration listing with pagination for both types."""
    for setting_type in [IntegrationType.PROJECT, IntegrationType.USER]:
        # Get first page with 5 items
        page_1 = client.integrations.list(setting_type=setting_type, page=0, per_page=5)
        assert len(page_1) <= 5

        # Get second page with 5 items
        page_2 = client.integrations.list(setting_type=setting_type, page=1, per_page=5)
        assert len(page_2) <= 5

        # Verify pages contain different integrations
        if page_1 and page_2:
            assert page_1[0].id != page_2[0].id


@pytest.mark.parametrize(
    "setting_type", [IntegrationType.PROJECT, IntegrationType.USER]
)
def test_integration_lifecycle(client: CodeMieClient, setting_type: IntegrationType):
    """Test full integration lifecycle for both user and project settings."""
    # Step 1: Create test integration
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

    # Create integration
    created = client.integrations.create(create_request)
    assert created is not None
    sleep(5)

    # Step 2: Verify integration exists in the list
    found = client.integrations.get_by_alias(test_alias, setting_type=setting_type)
    assert found is not None
    assert found.alias == test_alias
    assert found.setting_type == setting_type
    assert found.credential_values[0].value == "https://github.com"
    assert found.credential_values[1].value == "test-token-name"

    try:
        # Step 3: Update the integration
        updated_alias = f"{test_alias} Updated"
        update_request = Integration(
            project_name=test_project,
            credential_type=CredentialTypes.GIT,
            credential_values=[
                CredentialValues(
                    key="url", value="https://github.com/test/repo-updated"
                ),
                CredentialValues(key="token_name", value="test-token-name-updated"),
            ],
            alias=updated_alias,
            setting_type=setting_type,
        )

        updated = client.integrations.update(found.id, update_request)
        assert updated is not None
        sleep(5)

        # Step 4: Get and verify updated integration
        updated_integration = client.integrations.get_by_alias(
            updated_alias, setting_type=setting_type
        )
        assert updated_integration is not None
        assert updated_integration.id == found.id
        assert updated_integration.alias == updated_alias
        assert updated_integration.setting_type == setting_type
        assert updated_integration.credential_values[0].value == "https://github.com"
        assert (
            updated_integration.credential_values[1].value == "test-token-name-updated"
        )

    finally:
        # Step 5: Clean up - delete created integration
        if found:
            try:
                client.integrations.delete(found.id, setting_type=setting_type)
                sleep(5)
                # Verify deletion
                with pytest.raises(Exception) as exc_info:
                    client.integrations.get(found.id, setting_type=setting_type)
                assert (
                    "404" in str(exc_info.value)
                    or "not found" in str(exc_info.value).lower()
                )
            except Exception as e:
                pytest.fail(f"Failed to clean up integration: {str(e)}")


@pytest.mark.parametrize(
    "setting_type", [IntegrationType.PROJECT, IntegrationType.USER]
)
def test_create_integration_invalid_data(
    client: CodeMieClient, setting_type: IntegrationType
):
    """Test creating integration with invalid data for both types."""
    with pytest.raises(Exception):
        invalid_request = Integration(
            project_name="",  # Invalid - empty project name
            credential_type=CredentialTypes.GIT,
            credential_values=[],  # Invalid - empty credentials
            setting_type=setting_type,
        )
        client.integrations.create(invalid_request)


@pytest.mark.parametrize(
    "setting_type", [IntegrationType.PROJECT, IntegrationType.USER]
)
def test_update_integration_invalid_data(
    client: CodeMieClient, setting_type: IntegrationType
):
    """Test updating integration with invalid data for both types."""
    # First, get a valid integration ID
    integrations = client.integrations.list(setting_type=setting_type)
    assert len(integrations) > 0
    test_id = integrations[0].id

    with pytest.raises(Exception):
        invalid_request = Integration(
            project_name="",  # Invalid - empty project name
            credential_type=CredentialTypes.GIT,
            credential_values=[],  # Invalid - empty credentials
            setting_type=setting_type,
        )
        client.integrations.update(test_id, invalid_request)
