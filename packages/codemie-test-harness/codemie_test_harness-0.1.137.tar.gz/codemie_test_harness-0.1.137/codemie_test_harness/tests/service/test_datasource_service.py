import os
import pytest
from hamcrest import (
    assert_that,
    is_not,
    instance_of,
    has_property,
    has_length,
    greater_than,
    is_,
    is_in,
    all_of,
    equal_to,
)

from codemie_sdk.models.datasource import (
    DataSourceType,
    DataSourceStatus,
    Jira,
    Confluence,
    Code,
)
from codemie_sdk.models.integration import (
    CredentialTypes,
    CredentialValues,
    IntegrationType,
)
from codemie_test_harness.tests import PROJECT
from codemie_test_harness.tests.utils.base_utils import get_random_name


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
    def verify_datasource_exists(
        search_utils,
        name: str,
        project_name: str,
        datasource_type: DataSourceType,
    ):
        """Verify datasource exists with given parameters."""
        datasources = search_utils.list_data_sources(
            datasource_types=datasource_type, projects=project_name
        )
        datasource = next((ds for ds in datasources if ds.name == name), None)
        assert_that(datasource, is_not(None))
        assert_that(datasource.project_name, equal_to(project_name))
        assert_that(datasource.type, equal_to(datasource_type))
        return datasource

    @staticmethod
    def verify_datasource_updated(
        datasource_utils, datasource_id: str, expected_values: dict
    ):
        """
        Verify datasource was updated with expected values.
        Handles both root level fields and nested objects (Jira, Confluence).
        """
        updated_datasource = datasource_utils.get_datasource(datasource_id)
        assert_that(updated_datasource, is_not(None))

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
                    assert_that(
                        actual_value,
                        equal_to(value),
                        f"Expected {key} to be {value}, got {actual_value}",
                    )
                else:
                    pytest.fail(f"Unhandled field in verification: {key}")
            else:
                actual_value = getattr(updated_datasource, key, None)
                assert_that(
                    actual_value,
                    equal_to(value),
                    f"Expected {key} to be {value}, got {actual_value}",
                )

        return updated_datasource


class TestDatasources(TestDatasourceBase):
    """Tests for datasource operations."""

    def test_list_datasources(self, search_utils):
        datasource_types = [DataSourceType.CODE, DataSourceType.CONFLUENCE]
        datasource_models = search_utils.list_data_sources(
            datasource_types=datasource_types
        )
        assert_that(
            datasource_models, all_of(instance_of(list), has_length(greater_than(0)))
        )
        for model in datasource_models:
            assert_that(model.type, is_in(datasource_types))

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
    def test_list_datasources_filtered_by_type(self, search_utils, datasource_type):
        datasource_models = search_utils.list_data_sources(
            datasource_types=datasource_type
        )
        assert_that(
            datasource_models, all_of(instance_of(list), has_length(greater_than(0)))
        )
        for model in datasource_models:
            assert_that(model.type, is_in(datasource_type))

    @pytest.mark.parametrize(
        "status",
        [
            DataSourceStatus.IN_PROGRESS,
            DataSourceStatus.COMPLETED,
            DataSourceStatus.FAILED,
        ],
    )
    def test_list_datasources_filtered_by_status(self, search_utils, status):
        datasource_models = search_utils.list_data_sources(status=status)
        assert_that(datasource_models, all_of(instance_of(list)))
        for model in datasource_models:
            assert_that(
                model.status,
                equal_to(status),
                f"Datasource {model.name} has status {model.status}, expected {status}",
            )

    def test_create_update_code_datasource(
        self,
        integration_utils,
        llm_utils,
        search_utils,
        integration_config,
        datasource_utils,
    ):
        integration = integration_utils.create_integration(
            credential_type=CredentialTypes.GIT,
            credential_values=[
                CredentialValues(key=k, value=v)
                for k, v in integration_config[CredentialTypes.GIT].items()
            ],
            project_name=PROJECT,
        )
        embeddings_models = llm_utils.list_embedding_llm_models()
        assert_that(embeddings_models, has_length(greater_than(0)))
        embeddings_model = embeddings_models[0]
        create_request_params = {
            "name": integration.alias,
            "project_name": PROJECT,
            "description": "Code datasource description",
            "link": os.getenv("GITLAB_PROJECT"),
            "branch": "main",
            "index_type": DataSourceType.CODE,
            "embeddings_model": embeddings_model.base_name,
            "setting_id": integration.id,
        }
        created = datasource_utils.create_code_datasource(**create_request_params)
        assert_that(created, is_not(None))
        datasource = self.verify_datasource_exists(
            search_utils, integration.alias, PROJECT, DataSourceType.CODE
        )

        update_request_params = {
            "link": os.getenv("GITHUB_PROJECT"),
            "branch": "master",
            "name": integration.alias,
            "project_name": PROJECT,
            "description": "Updated datasource description",
        }

        updated = datasource_utils.update_code_datasource(
            datasource.id, **update_request_params
        )
        assert_that(updated, is_not(None))
        self.verify_datasource_updated(
            datasource_utils, datasource.id, update_request_params
        )

    def test_create_update_confluence_datasource(
        self,
        search_utils,
        integration_utils,
        integration_config,
        datasource_utils,
    ):
        integration = integration_utils.create_user_integration(
            credential_type=CredentialTypes.CONFLUENCE,
            credentials=[
                CredentialValues(key=k, value=v)
                for k, v in integration_config[CredentialTypes.CONFLUENCE].items()
            ],
            project_name=PROJECT,
        )
        create_request_params = {
            "name": integration.alias,
            "project_name": PROJECT,
            "description": "Datasource for KB space",
            "cql": os.getenv("CQL"),
            "setting_id": integration.id,
        }
        created = datasource_utils.create_confluence_datasource(**create_request_params)
        assert_that(created, is_not(None))
        datasource = self.verify_datasource_exists(
            search_utils, integration.alias, PROJECT, DataSourceType.CONFLUENCE
        )

        update_request_params = {
            "name": integration.alias,
            "description": "Updated datasource description for KB space",
            "cql": "SPACE = MY_KB",
        }

        updated = datasource_utils.update_confluence_datasource(
            datasource.id, **update_request_params
        )
        assert_that(updated, is_not(None))
        self.verify_datasource_updated(
            datasource_utils, datasource.id, update_request_params
        )

    def test_create_update_jira_datasource(
        self,
        search_utils,
        integration_utils,
        integration_config,
        datasource_utils,
    ):
        integration = integration_utils.create_integration(
            credential_type=CredentialTypes.JIRA,
            credential_values=[
                CredentialValues(key=k, value=v)
                for k, v in integration_config[CredentialTypes.JIRA].items()
            ],
            setting_type=IntegrationType.USER,
            project_name=PROJECT,
        )
        create_request_params = {
            "name": integration.alias,
            "project_name": PROJECT,
            "description": "Jira datasource description",
            "jql": os.getenv("JQL"),
            "setting_id": integration.id,
        }
        created = datasource_utils.create_jira_datasource(**create_request_params)
        assert_that(created, is_not(None))
        datasource = self.verify_datasource_exists(
            search_utils, integration.alias, PROJECT, DataSourceType.JIRA
        )

        update_request_params = {
            "name": integration.alias,
            "project_name": PROJECT,
            "description": "Updated Jira datasource description",
            "jql": os.getenv("JQL"),
        }

        updated = datasource_utils.update_jira_datasource(
            datasource.id, **update_request_params
        )
        assert_that(updated, is_not(None))
        self.verify_datasource_updated(
            datasource_utils, datasource.id, update_request_params
        )

    def test_create_update_google_datasource(self, search_utils, datasource_utils):
        create_request_params = {
            "name": get_random_name(),
            "project_name": PROJECT,
            "description": "Google datasource description",
            "google_doc": "https://docs.google.com/document/d/19EXgnFCgJontz0ToCAH6zMGwBTdhi5X97P9JIby4wHs/edit?tab=t.0",
        }
        created = datasource_utils.create_google_doc_datasource(**create_request_params)
        assert_that(created, is_not(None))
        datasource = self.verify_datasource_exists(
            search_utils, created.name, PROJECT, DataSourceType.GOOGLE
        )

        update_request_params = {
            "name": created.name,
            "project_name": PROJECT,
            "description": "Updated Google datasource description",
        }

        updated = datasource_utils.update_google_doc_datasource(
            datasource.id, **update_request_params
        )
        assert_that(updated, is_not(None))
        self.verify_datasource_updated(
            datasource_utils, datasource.id, update_request_params
        )

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
    def test_get_datasource_by_id(
        self, datasource_utils, datasource_type, search_utils
    ):
        datasources = search_utils.list_data_sources(
            datasource_types=datasource_type, per_page=50
        )
        assert_that(datasources, all_of(instance_of(list), has_length(greater_than(0))))

        original_datasource = datasources[0]
        datasource_id = original_datasource.id
        retrieved_datasource = datasource_utils.get_datasource(datasource_id)

        # Compare full objects (they should be identical)
        assert_that(
            retrieved_datasource,
            all_of(
                is_not(None),
            ),
        )
        assert_that(retrieved_datasource.id, equal_to(original_datasource.id))
        assert_that(retrieved_datasource.name, equal_to(original_datasource.name))
        assert_that(
            retrieved_datasource.project_name,
            equal_to(original_datasource.project_name),
        )
        assert_that(
            retrieved_datasource.created_by,
            equal_to(original_datasource.created_by),
        )
        assert_that(
            retrieved_datasource.shared_with_project,
            equal_to(original_datasource.shared_with_project),
        )
        assert_that(
            retrieved_datasource.created_date,
            equal_to(original_datasource.created_date),
        )
        assert_that(
            retrieved_datasource.error_message,
            equal_to(original_datasource.error_message),
        )
        assert_that(
            retrieved_datasource.processing_info.processed_documents_count,
            is_not(None),
        )

        if datasource_type == DataSourceType.CODE:
            assert_that(original_datasource.description, is_(None))
            assert_that(
                retrieved_datasource,
                all_of(
                    has_property("confluence", None),
                    has_property("jira", None),
                    has_property("tokens_usage", is_not(None)),
                    has_property("code"),
                ),
            )
            assert_that(
                retrieved_datasource.code.link,
                equal_to(original_datasource.code.link),
            )
            assert_that(retrieved_datasource.code.branch, is_not(None))
        elif datasource_type == DataSourceType.CONFLUENCE:
            assert_that(
                retrieved_datasource,
                all_of(
                    has_property("code", None),
                    has_property("jira", None),
                    has_property("tokens_usage", is_not(None)),
                    has_property("confluence", is_not(None)),
                ),
            )
            assert_that(retrieved_datasource.confluence.cql, is_not(None))
        elif datasource_type == DataSourceType.JIRA:
            assert_that(
                retrieved_datasource,
                all_of(
                    has_property("code", None),
                    has_property("confluence", None),
                    has_property("jira", is_not(None)),
                ),
            )
            assert_that(retrieved_datasource.jira.jql, is_not(None))
        elif datasource_type == DataSourceType.GOOGLE:
            assert_that(
                retrieved_datasource,
                all_of(
                    has_property("code", None),
                    has_property("confluence", None),
                    has_property("jira", None),
                    has_property("google_doc_link", is_not(None)),
                ),
            )
