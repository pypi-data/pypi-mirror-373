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
        f"User integration: {CredentialTypes.AWS}",
        f"User integration: {CredentialTypes.AZURE}",
        f"User integration: {CredentialTypes.GCP}",
        f"User integration: {CredentialTypes.SONAR}",
        f"User integration: {CredentialTypes.SONAR}",
        f"User integration: {CredentialTypes.GIT}",
        f"User integration: {CredentialTypes.GIT}",
        f"User integration: {CredentialTypes.CONFLUENCE}",
        f"User integration: {CredentialTypes.CONFLUENCE}",
        f"User integration: {CredentialTypes.JIRA}",
        f"User integration: {CredentialTypes.JIRA}",
        f"User integration: {CredentialTypes.SQL}",
        f"User integration: {CredentialTypes.SQL}",
        f"User integration: {CredentialTypes.ELASTIC}",
        f"User integration: {CredentialTypes.MCP}",
        f"User integration: {CredentialTypes.AZURE_DEVOPS}",
        f"User integration: {CredentialTypes.FILESYSTEM}",
        f"User integration: {CredentialTypes.EMAIL}",
        f"User integration: {CredentialTypes.TELEGRAM}",
        f"User integration: {CredentialTypes.SERVICE_NOW}",
        f"User integration: {CredentialTypes.KUBERNETES}",
    ],
)
@pytest.mark.regression
@pytest.mark.tescase("EPMCDME-2486, EPMCDME-2487, EPMCDME-2387, EPMCDME-2388")
def test_integration_created(
    credential_type, credentials, general_integration, integration_utils
):
    integration_alias = get_random_name()
    general_integration(
        integration_type=IntegrationType.USER,
        credential_type=credential_type,
        credential_values=credentials,
        integration_alias=integration_alias,
    )
    integration = integration_utils.get_integration_by_alias(
        integration_alias, IntegrationType.USER
    )
    assert_that(
        integration.credential_type == credential_type,
        f"Integration with alias '{integration_alias}' has incorrect credential type: "
        f"expected {credential_type}, got {integration.credential_type}",
    )
    assert_that(
        integration.setting_type == IntegrationType.USER,
        f"Integration with alias '{integration_alias}' has incorrect integration type: "
        f"expected {IntegrationType.USER}, got {integration.setting_type}",
    )


@pytest.mark.parametrize(
    "credential_type, credentials",
    testable_integrations,
    ids=[
        f"User integration: {CredentialTypes.AWS}",
        f"User integration: {CredentialTypes.AZURE}",
        f"User integration: {CredentialTypes.GCP}",
        f"User integration: {CredentialTypes.SONAR}",
        f"User integration: {CredentialTypes.SONAR}",
        f"User integration: {CredentialTypes.CONFLUENCE}",
        f"User integration: {CredentialTypes.CONFLUENCE}",
        f"User integration: {CredentialTypes.JIRA}",
        f"User integration: {CredentialTypes.JIRA}",
        f"User integration: {CredentialTypes.EMAIL}",
        f"User integration: {CredentialTypes.SERVICE_NOW}",
        f"User integration: {CredentialTypes.KUBERNETES}",
    ],
)
@pytest.mark.regression
@pytest.mark.tescase("EPMCDME-2381, EPMCDME-2380, EPMCDME-3107")
def test_integration_after_creation(
    credential_type, credentials, general_integration, integration_utils
):
    integration_alias = get_random_name()
    general_integration(
        integration_type=IntegrationType.USER,
        credential_type=credential_type,
        credential_values=credentials,
        integration_alias=integration_alias,
    )
    integration = integration_utils.get_integration_by_alias(
        integration_alias, IntegrationType.USER
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
        f"User integration: {CredentialTypes.AWS}",
        f"User integration: {CredentialTypes.AZURE}",
        f"User integration: {CredentialTypes.GCP}",
        f"User integration: {CredentialTypes.SONAR}",
        f"User integration: {CredentialTypes.SONAR}",
        f"User integration: {CredentialTypes.GIT}",
        f"User integration: {CredentialTypes.GIT}",
        f"User integration: {CredentialTypes.CONFLUENCE}",
        f"User integration: {CredentialTypes.CONFLUENCE}",
        f"User integration: {CredentialTypes.JIRA}",
        f"User integration: {CredentialTypes.JIRA}",
        f"User integration: {CredentialTypes.SQL}",
        f"User integration: {CredentialTypes.SQL}",
        f"User integration: {CredentialTypes.ELASTIC}",
        f"User integration: {CredentialTypes.MCP}",
        f"User integration: {CredentialTypes.AZURE_DEVOPS}",
        f"User integration: {CredentialTypes.FILESYSTEM}",
        f"User integration: {CredentialTypes.EMAIL}",
        f"User integration: {CredentialTypes.TELEGRAM}",
        f"User integration: {CredentialTypes.SERVICE_NOW}",
        f"User integration: {CredentialTypes.KUBERNETES}",
    ],
)
@pytest.mark.tescase("EPMCDME-2375")
@pytest.mark.regression
def test_update_integration(
    credential_type, credentials, general_integration, integration_utils
):
    integration_alias = get_random_name()
    general_integration(
        integration_type=IntegrationType.USER,
        credential_type=credential_type,
        credential_values=credentials,
        integration_alias=integration_alias,
    )
    integration = integration_utils.get_integration_by_alias(
        integration_alias, IntegrationType.USER
    )
    updated_alias = f"{get_random_name()}-updated"
    update_request = Integration(
        id=integration.id,
        project_name=PROJECT,
        credential_type=credential_type,
        credential_values=credentials,
        alias=updated_alias,
        setting_type=IntegrationType.USER,
    )
    update_response = integration_utils.update_integration(update_request)

    assert_that(
        update_response["message"],
        equal_to("Specified credentials updated"),
        "Integration update response message is not as expected.",
    )

    updated_integration = integration_utils.get_integration_by_alias(
        updated_alias, IntegrationType.USER
    )

    assert_that(updated_integration.alias, equal_to(updated_alias))


@pytest.mark.parametrize(
    "credential_type, credentials, error_message",
    invalid_integrations,
    ids=[
        f"User integration: {CredentialTypes.AWS}",
        f"User integration: {CredentialTypes.AZURE}",
        f"User integration: {CredentialTypes.GCP}",
        f"User integration: {CredentialTypes.SONAR}",
        f"User integration: {CredentialTypes.SONAR}",
        f"User integration: {CredentialTypes.EMAIL}",
        f"User integration: {CredentialTypes.JIRA}",
        f"User integration: {CredentialTypes.CONFLUENCE}",
        f"User integration: {CredentialTypes.SERVICE_NOW}",
        f"User integration: {CredentialTypes.KUBERNETES}",
    ],
)
@pytest.mark.tescase("EPMCDME-3111, EPMCDME-2379, EPMCDME-2384")
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
        setting_type=IntegrationType.USER,
    )
    create_response = integration_utils.send_create_integration_request(create_request)

    assert_that(
        create_response["message"],
        equal_to("Specified credentials saved"),
        "Integration create response message is not as expected.",
    )
    integration = integration_utils.get_integration_by_alias(
        integration_alias, IntegrationType.USER
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
        f"User integration: {CredentialTypes.AWS}",
        f"User integration: {CredentialTypes.AZURE}",
        f"User integration: {CredentialTypes.GCP}",
        f"User integration: {CredentialTypes.SONAR}",
        f"User integration: {CredentialTypes.SONAR}",
        f"User integration: {CredentialTypes.CONFLUENCE}",
        f"User integration: {CredentialTypes.CONFLUENCE}",
        f"User integration: {CredentialTypes.JIRA}",
        f"User integration: {CredentialTypes.JIRA}",
        f"User integration: {CredentialTypes.EMAIL}",
        f"User integration: {CredentialTypes.SERVICE_NOW}",
        f"User integration: {CredentialTypes.KUBERNETES}",
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
        f"User integration: {CredentialTypes.AWS}",
        f"User integration: {CredentialTypes.AZURE}",
        f"User integration: {CredentialTypes.GCP}",
        f"User integration: {CredentialTypes.SONAR}",
        f"User integration: {CredentialTypes.SONAR}",
        f"User integration: {CredentialTypes.EMAIL}",
        f"User integration: {CredentialTypes.JIRA}",
        f"User integration: {CredentialTypes.CONFLUENCE}",
        f"User integration: {CredentialTypes.SERVICE_NOW}",
        f"User integration: {CredentialTypes.KUBERNETES}",
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
        f"User integration: {CredentialTypes.AWS}",
        f"User integration: {CredentialTypes.AZURE}",
        f"User integration: {CredentialTypes.GCP}",
        f"User integration: {CredentialTypes.SONAR}",
        f"User integration: {CredentialTypes.SONAR}",
        f"User integration: {CredentialTypes.GIT}",
        f"User integration: {CredentialTypes.GIT}",
        f"User integration: {CredentialTypes.CONFLUENCE}",
        f"User integration: {CredentialTypes.CONFLUENCE}",
        f"User integration: {CredentialTypes.JIRA}",
        f"User integration: {CredentialTypes.JIRA}",
        f"User integration: {CredentialTypes.SQL}",
        f"User integration: {CredentialTypes.SQL}",
        f"User integration: {CredentialTypes.ELASTIC}",
        f"User integration: {CredentialTypes.MCP}",
        f"User integration: {CredentialTypes.AZURE_DEVOPS}",
        f"User integration: {CredentialTypes.FILESYSTEM}",
        f"User integration: {CredentialTypes.EMAIL}",
        f"User integration: {CredentialTypes.TELEGRAM}",
        f"User integration: {CredentialTypes.SERVICE_NOW}",
        f"User integration: {CredentialTypes.KUBERNETES}",
    ],
)
@pytest.mark.tescase("EPMCDME-2373")
@pytest.mark.regression
def test_delete_integration(
    credential_type, credentials, general_integration, integration_utils
):
    integration_alias = get_random_name()
    general_integration(
        integration_type=IntegrationType.USER,
        credential_type=credential_type,
        credential_values=credentials,
        integration_alias=integration_alias,
    )
    integration = integration_utils.get_integration_by_alias(
        integration_alias, IntegrationType.USER
    )

    delete_response = integration_utils.delete_integration(integration)

    assert_that(
        delete_response["message"],
        equal_to("Specified credential removed"),
        "Integration delete response is not as expected.",
    )
