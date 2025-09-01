import os

import pytest

from codemie_sdk.models.integration import CredentialTypes
from codemie_test_harness.tests.enums.integrations import DataBaseDialect
from codemie_test_harness.tests.utils.aws_parameters_store import CredentialsUtil

valid_integrations = [
    (
        CredentialTypes.AWS,
        CredentialsUtil.aws_credentials(),
    ),
    (
        CredentialTypes.AZURE,
        CredentialsUtil.azure_credentials(),
    ),
    pytest.param(
        CredentialTypes.GCP,
        CredentialsUtil.gcp_credentials(),
        marks=pytest.mark.skipif(
            os.getenv("ENV") == "azure",
            reason="Still have an issue with encoding long strings",
        ),
    ),
    (
        CredentialTypes.SONAR,
        CredentialsUtil.sonar_credentials(),
    ),
    (
        CredentialTypes.SONAR,
        CredentialsUtil.sonar_cloud_credentials(),
    ),
    (
        CredentialTypes.GIT,
        CredentialsUtil.gitlab_credentials(),
    ),
    (
        CredentialTypes.GIT,
        CredentialsUtil.github_credentials(),
    ),
    (
        CredentialTypes.CONFLUENCE,
        CredentialsUtil.confluence_credentials(),
    ),
    (
        CredentialTypes.CONFLUENCE,
        CredentialsUtil.confluence_cloud_credentials(),
    ),
    (
        CredentialTypes.JIRA,
        CredentialsUtil.jira_credentials(),
    ),
    (
        CredentialTypes.JIRA,
        CredentialsUtil.jira_cloud_credentials(),
    ),
    (
        CredentialTypes.SQL,
        CredentialsUtil.sql_credentials(DataBaseDialect.POSTGRES),
    ),
    (
        CredentialTypes.SQL,
        CredentialsUtil.sql_credentials(DataBaseDialect.MY_SQL),
    ),
    (
        CredentialTypes.ELASTIC,
        CredentialsUtil.elastic_credentials(),
    ),
    (
        CredentialTypes.MCP,
        CredentialsUtil.mcp_credentials(),
    ),
    (
        CredentialTypes.AZURE_DEVOPS,
        CredentialsUtil.azure_devops_credentials(),
    ),
    (
        CredentialTypes.FILESYSTEM,
        CredentialsUtil.file_system_credentials(),
    ),
    (
        CredentialTypes.EMAIL,
        CredentialsUtil.gmail_credentials(),
    ),
    (
        CredentialTypes.TELEGRAM,
        CredentialsUtil.telegram_credentials(),
    ),
    (
        CredentialTypes.SERVICE_NOW,
        CredentialsUtil.servicenow_credentials(),
    ),
    (
        CredentialTypes.KUBERNETES,
        CredentialsUtil.kubernetes_credentials(),
    ),
]

testable_integrations = [
    (
        CredentialTypes.AWS,
        CredentialsUtil.aws_credentials(),
    ),
    (
        CredentialTypes.AZURE,
        CredentialsUtil.azure_credentials(),
    ),
    pytest.param(
        CredentialTypes.GCP,
        CredentialsUtil.gcp_credentials(),
        marks=pytest.mark.skipif(
            os.getenv("ENV") == "azure",
            reason="Still have an issue with encoding long strings",
        ),
    ),
    (
        CredentialTypes.SONAR,
        CredentialsUtil.sonar_credentials(),
    ),
    (
        CredentialTypes.SONAR,
        CredentialsUtil.sonar_cloud_credentials(),
    ),
    (
        CredentialTypes.CONFLUENCE,
        CredentialsUtil.confluence_credentials(),
    ),
    (
        CredentialTypes.CONFLUENCE,
        CredentialsUtil.confluence_cloud_credentials(),
    ),
    (
        CredentialTypes.JIRA,
        CredentialsUtil.jira_credentials(),
    ),
    (
        CredentialTypes.JIRA,
        CredentialsUtil.jira_cloud_credentials(),
    ),
    pytest.param(
        CredentialTypes.EMAIL,
        CredentialsUtil.gmail_credentials(),
        marks=pytest.mark.skipif(
            os.getenv("ENV") == "local",
            reason="Skipping this test on local environment",
        ),
    ),
    (
        CredentialTypes.SERVICE_NOW,
        CredentialsUtil.servicenow_credentials(),
    ),
    (
        CredentialTypes.KUBERNETES,
        CredentialsUtil.kubernetes_credentials(),
    ),
]

invalid_integrations = [
    (
        CredentialTypes.AWS,
        CredentialsUtil.invalid_aws_credentials(),
        "An error occurred (SignatureDoesNotMatch) when calling the GetUser operation: The request signature we calculated does not match the signature you provided. Check your AWS Secret Access Key and signing method. Consult the service documentation for details.",
    ),
    (
        CredentialTypes.AZURE,
        CredentialsUtil.invalid_azure_credentials(),
        "Invalid client secret provided. Ensure the secret being sent in the request is the client secret value, not the client secret ID, for a secret added to app",
    ),
    pytest.param(
        CredentialTypes.GCP,
        CredentialsUtil.invalid_gcp_credentials(),
        "Error: ('Could not deserialize key data. The data may be in an incorrect format, "
        + "the provided password may be incorrect, it may be encrypted with an unsupported algorithm, "
        + "or it may be an unsupported key type",
        marks=pytest.mark.skipif(
            os.getenv("ENV") == "azure",
            reason="Still have an issue with encoding long strings",
        ),
    ),
    (
        CredentialTypes.SONAR,
        CredentialsUtil.invalid_sonar_credentials(),
        "Invalid token",
    ),
    (
        CredentialTypes.SONAR,
        CredentialsUtil.invalid_sonar_cloud_credentials(),
        "Invalid token",
    ),
    pytest.param(
        CredentialTypes.EMAIL,
        CredentialsUtil.invalid_gmail_credentials(),
        "SMTP Code: 535. SMTP error",
        marks=pytest.mark.skipif(
            os.getenv("ENV") == "local",
            reason="Skipping this test on local environment",
        ),
    ),
    (
        CredentialTypes.JIRA,
        CredentialsUtil.invalid_jira_credentials(),
        "Unauthorized (401)",
    ),
    (
        CredentialTypes.CONFLUENCE,
        CredentialsUtil.invalid_confluence_credentials(),
        "Access denied",
    ),
    (
        CredentialTypes.SERVICE_NOW,
        CredentialsUtil.invalid_servicenow_credentials(),
        'ServiceNow tool exception. Status: 401. Response: {"error":{"message":"User Not Authenticated","detail":"Required to provide Auth information"}',
    ),
    (
        CredentialTypes.KUBERNETES,
        CredentialsUtil.invalid_kubernetes_credentials(),
        "Error: (401)\nReason: Unauthorized",
    ),
]
