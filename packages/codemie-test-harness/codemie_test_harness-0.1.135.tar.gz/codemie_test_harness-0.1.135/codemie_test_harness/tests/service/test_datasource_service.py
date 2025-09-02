"""Integration tests for LLMService."""

import os
from time import sleep

import pytest

from codemie_sdk import CodeMieClient
from codemie_sdk.models.datasource import (
    DataSourceType,
    DataSourceStatus,
    CodeDataSourceRequest,
    CodeDataSourceType,
    UpdateCodeDataSourceRequest,
    ConfluenceDataSourceRequest,
    UpdateConfluenceDataSourceRequest,
    UpdateJiraDataSourceRequest,
    JiraDataSourceRequest,
    GoogleDataSourceRequest,
    UpdateGoogleDataSourceRequest,
    Jira,
    Confluence,
    Code,
)
from codemie_sdk.models.integration import (
    CredentialTypes,
    CredentialValues,
    Integration,
    IntegrationType,
)
from codemie_test_harness.tests import PROJECT
from codemie_test_harness.tests.utils.base_utils import get_random_name


@pytest.fixture
def project_name():
    """Return project name for tests."""
    return PROJECT


@pytest.fixture
def datasource_name():
    return get_random_name()


@pytest.fixture
def integration_config():
    """Configuration for different integration types."""
    return {
        CredentialTypes.GIT: {
            "url": os.getenv("GITLAB_URL"),
            "token_name": "test-token-name",
            "token": os.getenv("GITLAB_TOKEN"),
        },
        CredentialTypes.CONFLUENCE: {
            "url": os.getenv("CONFLUENCE_URL"),
            "token_name": "test-token-name",
            "token": os.getenv("CONFLUENCE_TOKEN"),
        },
        CredentialTypes.JIRA: {
            "url": os.getenv("JIRA_URL"),
            "token_name": "test-token-name",
            "token": os.getenv("JIRA_TOKEN"),
        },
    }


class TestDatasourceBase:
    """Base class for datasource tests with common utility methods."""

    @staticmethod
    def create_integration(
        client: CodeMieClient,
        project_name: str,
        cred_type: CredentialTypes,
        config: dict,
    ) -> Integration:
        """Create integration with given credentials."""
        integration_alias = get_random_name()
        credential_values = [
            CredentialValues(key=k, value=v) for k, v in config[cred_type].items()
        ]

        integration_request = Integration(
            project_name=project_name,
            credential_type=cred_type,
            credential_values=credential_values,
            alias=integration_alias,
            setting_type=IntegrationType.USER,
        )

        client.integrations.create(integration_request)
        sleep(5)
        return client.integrations.get_by_alias(integration_alias)

    @staticmethod
    def cleanup_datasource(client: CodeMieClient, datasource_id: str):
        """Clean up datasource and verify deletion."""
        try:
            client.datasources.delete(datasource_id)
            sleep(5)
            with pytest.raises(Exception) as exc_info:
                client.datasources.get(datasource_id)
            assert "503" in str(exc_info.value)
        except Exception as e:
            pytest.fail(f"Failed to clean up datasource: {str(e)}")

    @staticmethod
    def verify_datasource_exists(
        client: CodeMieClient,
        name: str,
        project_name: str,
        datasource_type: DataSourceType,
    ):
        """Verify datasource exists with given parameters."""
        sleep(5)
        datasources = client.datasources.list(
            datasource_types=datasource_type, projects=project_name
        )
        datasource = next((ds for ds in datasources if ds.name == name), None)
        assert datasource is not None
        assert datasource.project_name == project_name
        assert datasource.type == datasource_type
        return datasource

    @staticmethod
    def verify_datasource_updated(
        client: CodeMieClient, datasource_id: str, expected_values: dict
    ):
        """
        Verify datasource was updated with expected values.
        Handles both root level fields and nested objects (Jira, Confluence).
        """
        sleep(5)
        updated_datasource = client.datasources.get(datasource_id)
        assert updated_datasource is not None

        field_mapping = {
            "jql": ("jira", Jira, "jql"),
            "cql": ("confluence", Confluence, "cql"),
            "link": ("code", Code, "link"),
            "branch": ("code", Code, "branch"),
        }

        for key, value in expected_values.items():
            if key in field_mapping:
                attr, expected_class, sub_attr = field_mapping[key]
                nested_obj = getattr(updated_datasource, attr, None)
                if nested_obj is not None and isinstance(nested_obj, expected_class):
                    actual_value = getattr(nested_obj, sub_attr, None)
                    assert actual_value == value, (
                        f"Expected {key} to be {value}, got {actual_value}"
                    )
                else:
                    pytest.fail(f"Unhandled field in verification: {key}")
            else:
                actual_value = getattr(updated_datasource, key, None)
                assert actual_value == value, (
                    f"Expected {key} to be {value}, got {actual_value}"
                )

        return updated_datasource


class TestDatasources(TestDatasourceBase):
    """Tests for datasource operations."""

    def test_list_datasources(self, client: CodeMieClient):
        """Test successful retrieval of available datasources models."""
        datasource_types = [DataSourceType.CODE, DataSourceType.CONFLUENCE]
        models = client.datasources.list(datasource_types=datasource_types)
        assert isinstance(models, list)
        assert len(models) > 0
        assert all(model.type in datasource_types for model in models)

    @pytest.mark.parametrize(
        "datasource_type",
        [
            DataSourceType.CODE,
            DataSourceType.CONFLUENCE,
            DataSourceType.FILE,
            DataSourceType.JIRA,
            DataSourceType.GOOGLE,
        ],
    )
    def test_list_datasources_by_type(self, client: CodeMieClient, datasource_type):
        """Test successful retrieval of available datasources models."""
        models = client.datasources.list(datasource_types=datasource_type)
        assert isinstance(models, list)
        assert len(models) > 0
        assert all(model.type == datasource_type for model in models)

    @pytest.mark.parametrize(
        "status",
        [
            DataSourceStatus.IN_PROGRESS,
            DataSourceStatus.COMPLETED,
            DataSourceStatus.FAILED,
        ],
    )
    def test_list_datasources_by_status(self, client: CodeMieClient, status):
        """Test successful retrieval of available datasources models."""
        models = client.datasources.list(status=status)
        assert isinstance(models, list)
        assert len(models) > 0
        assert all(model.status == status for model in models)

    def test_create_update_code_datasource(
        self, client: CodeMieClient, integration_config, datasource_name
    ):
        project_name = PROJECT
        integration = self.create_integration(
            client, project_name, CredentialTypes.GIT, integration_config
        )
        embeddings_models = client.llms.list_embeddings()
        assert len(embeddings_models) > 0
        embeddings_model = embeddings_models[0]
        datasource = None
        try:
            create_request_params = {
                "name": datasource_name,
                "project_name": project_name,
                "description": "Code datasource description",
                "link": os.getenv("GITLAB_PROJECT"),
                "branch": "main",
                "index_type": CodeDataSourceType.CODE,
                "embeddings_model": embeddings_model.base_name,
                "setting_id": integration.id,
            }
            create_datasource_request = CodeDataSourceRequest(**create_request_params)
            created = client.datasources.create(create_datasource_request)
            assert created is not None
            datasource = self.verify_datasource_exists(
                client, datasource_name, project_name, DataSourceType.CODE
            )

            update_request_params = {
                "link": os.getenv("GITHUB_PROJECT"),
                "branch": "master",
                "name": datasource_name,
                "project_name": project_name,
                "description": "Updated datasource description",
            }

            update_datasource_request = UpdateCodeDataSourceRequest(
                **update_request_params
            )
            updated = client.datasources.update(
                datasource.id, update_datasource_request
            )
            assert updated is not None
            self.verify_datasource_updated(client, datasource.id, update_request_params)
        finally:
            # Cleanup
            if datasource:
                self.cleanup_datasource(client, datasource.id)
            if integration:
                client.integrations.delete(integration.id)

    def test_create_update_confluence_datasource(
        self, client: CodeMieClient, integration_config, datasource_name
    ):
        project_name = PROJECT
        integration = self.create_integration(
            client, project_name, CredentialTypes.CONFLUENCE, integration_config
        )
        datasource = None
        try:
            create_request_params = {
                "name": datasource_name,
                "project_name": project_name,
                "description": "Datasource for KB space",
                "cql": os.getenv("CQL"),
                "setting_id": integration.id,
            }
            create_datasource_request = ConfluenceDataSourceRequest(
                **create_request_params
            )
            created = client.datasources.create(create_datasource_request)
            assert created is not None
            datasource = self.verify_datasource_exists(
                client, datasource_name, project_name, DataSourceType.CONFLUENCE
            )

            update_request_params = {
                "name": datasource_name,
                "project_name": project_name,
                "description": "Updated datasource description for KB space",
                "cql": "SPACE = MY_KB",
            }

            update_datasource_request = UpdateConfluenceDataSourceRequest(
                **update_request_params
            )
            updated = client.datasources.update(
                datasource.id, update_datasource_request
            )
            assert updated is not None
            self.verify_datasource_updated(client, datasource.id, update_request_params)
        finally:
            # Cleanup
            if datasource:
                self.cleanup_datasource(client, datasource.id)
            if integration:
                client.integrations.delete(integration.id)

    def test_create_update_jira_datasource(
        self, client: CodeMieClient, integration_config, datasource_name
    ):
        project_name = PROJECT
        integration = self.create_integration(
            client, project_name, CredentialTypes.JIRA, integration_config
        )
        datasource = None
        try:
            create_request_params = {
                "name": datasource_name,
                "project_name": project_name,
                "description": "Jira datasource description",
                "jql": os.getenv("JQL"),
                "setting_id": integration.id,
            }
            create_datasource_request = JiraDataSourceRequest(**create_request_params)
            created = client.datasources.create(create_datasource_request)
            assert created is not None
            datasource = self.verify_datasource_exists(
                client, datasource_name, project_name, DataSourceType.JIRA
            )

            update_request_params = {
                "name": datasource_name,
                "project_name": project_name,
                "description": "Updated Jira datasource description",
                "jql": os.getenv("JQL"),
            }

            update_datasource_request = UpdateJiraDataSourceRequest(
                **update_request_params
            )
            updated = client.datasources.update(
                datasource.id, update_datasource_request
            )
            assert updated is not None
            self.verify_datasource_updated(client, datasource.id, update_request_params)
        finally:
            # Cleanup
            if datasource:
                self.cleanup_datasource(client, datasource.id)
            if integration:
                client.integrations.delete(integration.id)

    def test_create_update_google_datasource(
        self, client: CodeMieClient, integration_config, datasource_name
    ):
        project_name = PROJECT
        datasource = None
        try:
            create_request_params = {
                "name": datasource_name,
                "project_name": project_name,
                "description": "Google datasource description",
                "google_doc": "https://docs.google.com/document/d/16qP3UlOKa-wFA2Ztbsu6qfO4jGPM6S65bse5C9D-AzQ/edit?tab=t.0",
            }
            create_datasource_request = GoogleDataSourceRequest(**create_request_params)
            created = client.datasources.create(create_datasource_request)
            assert created is not None
            datasource = self.verify_datasource_exists(
                client, datasource_name, project_name, DataSourceType.GOOGLE
            )

            update_request_params = {
                "name": datasource_name,
                "project_name": project_name,
                "description": "Updated Google datasource description",
            }

            update_datasource_request = UpdateGoogleDataSourceRequest(
                **update_request_params
            )
            updated = client.datasources.update(
                datasource.id, update_datasource_request
            )
            assert updated is not None
            self.verify_datasource_updated(client, datasource.id, update_request_params)
        finally:
            # Cleanup
            if datasource:
                self.cleanup_datasource(client, datasource.id)

    @pytest.mark.parametrize(
        "datasource_type",
        [
            DataSourceType.CODE,
            DataSourceType.CONFLUENCE,
            DataSourceType.FILE,
            DataSourceType.JIRA,
            DataSourceType.GOOGLE,
        ],
    )
    def test_get_datasource_by_id(self, client: CodeMieClient, datasource_type):
        """Test successful retrieval of available datasources models."""
        datasources = client.datasources.list(
            datasource_types=datasource_type, per_page=50
        )
        assert isinstance(datasources, list)
        assert len(datasources) > 0

        original_datasource = datasources[0]
        datasource_id = original_datasource.id
        retrieved_datasource = client.datasources.get(datasource_id)

        # Compare full objects (they should be identical)
        assert retrieved_datasource.id == original_datasource.id
        assert retrieved_datasource.name == original_datasource.name
        assert retrieved_datasource.project_name == original_datasource.project_name
        assert retrieved_datasource.created_by == original_datasource.created_by
        assert (
            retrieved_datasource.shared_with_project
            == original_datasource.shared_with_project
        )
        assert retrieved_datasource.created_date == original_datasource.created_date
        assert retrieved_datasource.error_message == original_datasource.error_message
        assert retrieved_datasource.processing_info is not None
        assert (
            retrieved_datasource.processing_info.processed_documents_count is not None
        )

        if datasource_type == DataSourceType.CODE:
            assert original_datasource.description is None
            assert retrieved_datasource.confluence is None
            assert retrieved_datasource.jira is None
            assert retrieved_datasource.tokens_usage is not None
            assert retrieved_datasource.code.link == original_datasource.code.link
            assert retrieved_datasource.code.branch is not None
        elif datasource_type == DataSourceType.CONFLUENCE:
            assert retrieved_datasource.code is None
            assert retrieved_datasource.jira is None
            assert retrieved_datasource.tokens_usage is not None
            assert retrieved_datasource.confluence is not None
            assert retrieved_datasource.confluence.cql is not None
        elif datasource_type == DataSourceType.JIRA:
            assert retrieved_datasource.code is None
            assert retrieved_datasource.confluence is None
            assert retrieved_datasource.jira is not None
            assert retrieved_datasource.jira.jql is not None
        elif datasource_type == DataSourceType.GOOGLE:
            assert retrieved_datasource.code is None
            assert retrieved_datasource.confluence is None
            assert retrieved_datasource.jira is None
            assert retrieved_datasource.google_doc_link is not None
