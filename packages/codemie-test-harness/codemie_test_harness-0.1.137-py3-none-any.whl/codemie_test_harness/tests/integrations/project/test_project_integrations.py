import pytest
from hamcrest import assert_that, equal_to
from requests import HTTPError

from codemie_sdk.models.integration import (
    IntegrationType,
    Integration,
    IntegrationTestRequest,
    IntegrationTestResponse,
    CredentialTypes,
)
from codemie_test_harness.tests import PROJECT
from codemie_test_harness.tests.test_data.integrations_test_data import (
    valid_integrations,
    invalid_integrations,
    testable_integrations,
)
from codemie_test_harness.tests.utils.base_utils import (
    get_random_name,
    assert_error_details,
)


@pytest.mark.parametrize(
    "credential_type, credentials",
    valid_integrations,
    ids=[
        f"Project integration: {CredentialTypes.AWS}",
        f"Project integration: {CredentialTypes.AZURE}",
        f"Project integration: {CredentialTypes.GCP}",
        f"Project integration: {CredentialTypes.SONAR}",
        f"Project integration: {CredentialTypes.SONAR}",
        f"Project integration: {CredentialTypes.GIT}",
        f"Project integration: {CredentialTypes.GIT}",
        f"Project integration: {CredentialTypes.CONFLUENCE}",
        f"Project integration: {CredentialTypes.CONFLUENCE}",
        f"Project integration: {CredentialTypes.JIRA}",
        f"Project integration: {CredentialTypes.JIRA}",
        f"Project integration: {CredentialTypes.SQL}",
        f"Project integration: {CredentialTypes.SQL}",
        f"Project integration: {CredentialTypes.ELASTIC}",
        f"Project integration: {CredentialTypes.MCP}",
        f"Project integration: {CredentialTypes.AZURE_DEVOPS}",
        f"Project integration: {CredentialTypes.FILESYSTEM}",
        f"Project integration: {CredentialTypes.EMAIL}",
        f"Project integration: {CredentialTypes.TELEGRAM}",
        f"Project integration: {CredentialTypes.SERVICE_NOW}",
        f"Project integration: {CredentialTypes.KUBERNETES}",
    ],
)
@pytest.mark.regression
def test_integration_created(
    credential_type, credentials, general_integration, integration_utils
):
    integration_alias = get_random_name()
    general_integration(
        integration_type=IntegrationType.PROJECT,
        credential_type=credential_type,
        credential_values=credentials,
        integration_alias=integration_alias,
    )
    integration = integration_utils.get_integration_by_alias(
        integration_alias, IntegrationType.PROJECT
    )
    assert_that(
        integration.credential_type == credential_type,
        f"Integration with alias '{integration_alias}' has incorrect credential type: "
        f"expected {credential_type}, got {integration.credential_type}",
    )
    assert_that(
        integration.setting_type == IntegrationType.PROJECT,
        f"Integration with alias '{integration_alias}' has incorrect integration type: "
        f"expected {IntegrationType.PROJECT}, got {integration.setting_type}",
    )


@pytest.mark.parametrize(
    "credential_type, credentials",
    testable_integrations,
    ids=[
        f"Project integration: {CredentialTypes.AWS}",
        f"Project integration: {CredentialTypes.AZURE}",
        f"Project integration: {CredentialTypes.GCP}",
        f"Project integration: {CredentialTypes.SONAR}",
        f"Project integration: {CredentialTypes.SONAR}",
        f"Project integration: {CredentialTypes.CONFLUENCE}",
        f"Project integration: {CredentialTypes.CONFLUENCE}",
        f"Project integration: {CredentialTypes.JIRA}",
        f"Project integration: {CredentialTypes.JIRA}",
        f"Project integration: {CredentialTypes.EMAIL}",
        f"Project integration: {CredentialTypes.SERVICE_NOW}",
        f"Project integration: {CredentialTypes.KUBERNETES}",
    ],
)
@pytest.mark.regression
def test_integration_after_creation(
    credential_type, credentials, general_integration, integration_utils
):
    integration_alias = get_random_name()
    general_integration(
        integration_type=IntegrationType.PROJECT,
        credential_type=credential_type,
        credential_values=credentials,
        integration_alias=integration_alias,
    )
    integration = integration_utils.get_integration_by_alias(
        integration_alias, IntegrationType.PROJECT
    )
    integration_test_model = IntegrationTestRequest(
        credential_type=integration.credential_type,
        setting_id=integration.id,
    )
    test_response = integration_utils.test_integration(
        integration_test_model, IntegrationTestResponse
    )

    successful_test_response = IntegrationTestResponse(message="", success=True)

    assert_that(
        test_response,
        equal_to(successful_test_response),
        "Integration test response is not successful.",
    )


@pytest.mark.parametrize(
    "credential_type, credentials",
    valid_integrations,
    ids=[
        f"Project integration: {CredentialTypes.AWS}",
        f"Project integration: {CredentialTypes.AZURE}",
        f"Project integration: {CredentialTypes.GCP}",
        f"Project integration: {CredentialTypes.SONAR}",
        f"Project integration: {CredentialTypes.SONAR}",
        f"Project integration: {CredentialTypes.GIT}",
        f"Project integration: {CredentialTypes.GIT}",
        f"Project integration: {CredentialTypes.CONFLUENCE}",
        f"Project integration: {CredentialTypes.CONFLUENCE}",
        f"Project integration: {CredentialTypes.JIRA}",
        f"Project integration: {CredentialTypes.JIRA}",
        f"Project integration: {CredentialTypes.SQL}",
        f"Project integration: {CredentialTypes.SQL}",
        f"Project integration: {CredentialTypes.ELASTIC}",
        f"Project integration: {CredentialTypes.MCP}",
        f"Project integration: {CredentialTypes.AZURE_DEVOPS}",
        f"Project integration: {CredentialTypes.FILESYSTEM}",
        f"Project integration: {CredentialTypes.EMAIL}",
        f"Project integration: {CredentialTypes.TELEGRAM}",
        f"Project integration: {CredentialTypes.SERVICE_NOW}",
        f"Project integration: {CredentialTypes.KUBERNETES}",
    ],
)
@pytest.mark.tescase("EPMCDME-2376")
@pytest.mark.regression
def test_update_integration(
    credential_type, credentials, general_integration, integration_utils
):
    integration_alias = get_random_name()
    general_integration(
        integration_type=IntegrationType.PROJECT,
        credential_type=credential_type,
        credential_values=credentials,
        integration_alias=integration_alias,
    )
    integration = integration_utils.get_integration_by_alias(
        integration_alias, IntegrationType.PROJECT
    )
    updated_alias = f"{get_random_name()}-updated"
    update_request = Integration(
        id=integration.id,
        project_name=PROJECT,
        credential_type=credential_type,
        credential_values=credentials,
        alias=updated_alias,
        setting_type=IntegrationType.PROJECT,
    )
    update_response = integration_utils.update_integration(update_request)

    assert_that(
        update_response["message"],
        equal_to("Specified credentials updated"),
        "Integration update response message is not as expected.",
    )

    updated_integration = integration_utils.get_integration_by_alias(
        updated_alias, IntegrationType.PROJECT
    )

    assert_that(updated_integration.alias, equal_to(updated_alias))


@pytest.mark.parametrize(
    "credential_type, credentials, error_message",
    invalid_integrations,
    ids=[
        f"Project integration: {CredentialTypes.AWS}",
        f"Project integration: {CredentialTypes.AZURE}",
        f"Project integration: {CredentialTypes.GCP}",
        f"Project integration: {CredentialTypes.SONAR}",
        f"Project integration: {CredentialTypes.SONAR}",
        f"Project integration: {CredentialTypes.EMAIL}",
        f"Project integration: {CredentialTypes.JIRA}",
        f"Project integration: {CredentialTypes.CONFLUENCE}",
        f"Project integration: {CredentialTypes.SERVICE_NOW}",
        f"Project integration: {CredentialTypes.KUBERNETES}",
    ],
)
@pytest.mark.regression
def test_integration_with_invalid_credentials(
    credential_type, credentials, error_message, integration_utils
):
    integration_alias = get_random_name()
    create_request = Integration(
        project_name=PROJECT,
        credential_type=credential_type,
        credential_values=credentials,
        alias=integration_alias,
        setting_type=IntegrationType.PROJECT,
    )
    create_response = integration_utils.send_create_integration_request(create_request)

    assert_that(
        create_response["message"],
        equal_to("Specified credentials saved"),
        "Integration create response message is not as expected.",
    )
    integration = integration_utils.get_integration_by_alias(
        integration_alias, IntegrationType.PROJECT
    )

    integration_test_model = IntegrationTestRequest(
        credential_type=integration.credential_type,
        setting_id=integration.id,
    )

    try:
        integration_utils.test_integration(integration_test_model)
        raise AssertionError("Integration test response is not expected.")
    except HTTPError as e:
        assert_error_details(e.response, 400, error_message)


@pytest.mark.parametrize(
    "credential_type, credentials",
    testable_integrations,
    ids=[
        f"Project integration: {CredentialTypes.AWS}",
        f"Project integration: {CredentialTypes.AZURE}",
        f"Project integration: {CredentialTypes.GCP}",
        f"Project integration: {CredentialTypes.SONAR}",
        f"Project integration: {CredentialTypes.SONAR}",
        f"Project integration: {CredentialTypes.CONFLUENCE}",
        f"Project integration: {CredentialTypes.CONFLUENCE}",
        f"Project integration: {CredentialTypes.JIRA}",
        f"Project integration: {CredentialTypes.JIRA}",
        f"Project integration: {CredentialTypes.EMAIL}",
        f"Project integration: {CredentialTypes.SERVICE_NOW}",
        f"Project integration: {CredentialTypes.KUBERNETES}",
    ],
)
@pytest.mark.regression
def test_integration_during_creation(credential_type, credentials, integration_utils):
    integration_test_model = IntegrationTestRequest(
        credential_type=credential_type,
        credential_values=credentials,
    )
    test_response = integration_utils.test_integration(
        integration_test_model, IntegrationTestResponse
    )
    successful_test_response = IntegrationTestResponse(message="", success=True)

    assert_that(
        test_response,
        equal_to(successful_test_response),
        "Integration test response is not successful.",
    )


@pytest.mark.parametrize(
    "credential_type, credentials, error_message",
    invalid_integrations,
    ids=[
        f"Project integration: {CredentialTypes.AWS}",
        f"Project integration: {CredentialTypes.AZURE}",
        f"Project integration: {CredentialTypes.GCP}",
        f"Project integration: {CredentialTypes.SONAR}",
        f"Project integration: {CredentialTypes.SONAR}",
        f"Project integration: {CredentialTypes.EMAIL}",
        f"Project integration: {CredentialTypes.JIRA}",
        f"Project integration: {CredentialTypes.CONFLUENCE}",
        f"Project integration: {CredentialTypes.SERVICE_NOW}",
        f"Project integration: {CredentialTypes.KUBERNETES}",
    ],
)
@pytest.mark.regression
def test_integration_during_creation_with_invalid_credentials(
    credential_type, credentials, error_message, integration_utils
):
    integration_test_model = IntegrationTestRequest(
        credential_type=credential_type,
        credential_values=credentials,
    )

    try:
        integration_utils.test_integration(integration_test_model)
        raise AssertionError("Integration test response is not expected.")
    except HTTPError as e:
        assert_error_details(e.response, 400, error_message)


@pytest.mark.parametrize(
    "credential_type, credentials",
    valid_integrations,
    ids=[
        f"Project integration: {CredentialTypes.AWS}",
        f"Project integration: {CredentialTypes.AZURE}",
        f"Project integration: {CredentialTypes.GCP}",
        f"Project integration: {CredentialTypes.SONAR}",
        f"Project integration: {CredentialTypes.SONAR}",
        f"Project integration: {CredentialTypes.GIT}",
        f"Project integration: {CredentialTypes.GIT}",
        f"Project integration: {CredentialTypes.CONFLUENCE}",
        f"Project integration: {CredentialTypes.CONFLUENCE}",
        f"Project integration: {CredentialTypes.JIRA}",
        f"Project integration: {CredentialTypes.JIRA}",
        f"Project integration: {CredentialTypes.SQL}",
        f"Project integration: {CredentialTypes.SQL}",
        f"Project integration: {CredentialTypes.ELASTIC}",
        f"Project integration: {CredentialTypes.MCP}",
        f"Project integration: {CredentialTypes.AZURE_DEVOPS}",
        f"Project integration: {CredentialTypes.FILESYSTEM}",
        f"Project integration: {CredentialTypes.EMAIL}",
        f"Project integration: {CredentialTypes.TELEGRAM}",
        f"Project integration: {CredentialTypes.SERVICE_NOW}",
        f"Project integration: {CredentialTypes.KUBERNETES}",
    ],
)
@pytest.mark.tescase("EPMCDME-2374")
@pytest.mark.regression
def test_delete_integration(
    credential_type, credentials, general_integration, integration_utils
):
    integration_alias = get_random_name()
    general_integration(
        integration_type=IntegrationType.PROJECT,
        credential_type=credential_type,
        credential_values=credentials,
        integration_alias=integration_alias,
    )
    integration = integration_utils.get_integration_by_alias(
        integration_alias, IntegrationType.PROJECT
    )

    delete_response = integration_utils.delete_integration(integration)

    assert_that(
        delete_response["message"],
        equal_to("Specified credential removed"),
        "Integration delete response is not as expected.",
    )
