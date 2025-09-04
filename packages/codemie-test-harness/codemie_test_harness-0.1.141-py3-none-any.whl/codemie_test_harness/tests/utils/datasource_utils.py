import os
import time
from time import sleep
from typing import List, Union, Tuple

from codemie_sdk.exceptions import ApiError
from codemie_sdk.models.datasource import (
    DataSource,
    CodeDataSourceRequest,
    ConfluenceDataSourceRequest,
    JiraDataSourceRequest,
    GoogleDataSourceRequest,
    FileDataSourceRequest,
    UpdateCodeDataSourceRequest,
    UpdateGoogleDataSourceRequest,
    UpdateFileDataSourceRequest,
    CodeDataSourceType,
    UpdateConfluenceDataSourceRequest,
    UpdateJiraDataSourceRequest,
)
from codemie_sdk.models.datasource import DataSourceStatus
from codemie_test_harness.tests import PROJECT
from codemie_test_harness.tests.utils.base_utils import (
    BaseUtils,
    get_random_name,
    wait_for_entity,
)


class DataSourceUtils(BaseUtils):
    def create_code_datasource(self, **kwargs):
        create_request_params = {
            "project_name": kwargs.get("project_name", PROJECT),
            "link": kwargs.get("link"),
            "branch": kwargs.get("branch"),
            "index_type": CodeDataSourceType.CODE,
            "embeddings_model": kwargs.get("embeddings_model"),
            "setting_id": kwargs.get("setting_id"),
            "description": kwargs.get("description", get_random_name()),
            "project_space_visible": kwargs.get("project_space_visible", False),
            "name": kwargs.get("name", get_random_name()),
        }

        create_datasource_request = CodeDataSourceRequest(**create_request_params)

        self.client.datasources.create(create_datasource_request)

        datasource = wait_for_entity(
            lambda: self.client.datasources.list(per_page=200),
            entity_name=create_datasource_request.name,
        )

        return self.wait_for_indexing(datasource.id)

    def update_code_datasource(self, datasource_id, **kwargs):
        datasource = self.get_datasource(datasource_id)

        update_request_params = {
            "project_name": datasource.project_name,
            "link": kwargs.get("link", datasource.code.link),
            "branch": kwargs.get("branch", datasource.code.branch),
            "index_type": CodeDataSourceType.CODE,
            "embeddings_model": kwargs.get(
                "embeddings_model", datasource.embeddings_model
            ),
            "setting_id": kwargs.get("setting_id", datasource.setting_id),
            "description": kwargs.get("description", datasource.description),
            "name": datasource.name,
            "project_space_visible": kwargs.get(
                "project_space_visible", datasource.shared_with_project
            ),
            "full_reindex": kwargs.get("full_reindex", False),
            "skip_reindex": kwargs.get("skip_reindex", True),
            "incremental_reindex": kwargs.get("incremental_reindex", False),
        }

        update_datasource_request = UpdateCodeDataSourceRequest(**update_request_params)

        self.client.datasources.update(datasource.id, update_datasource_request)

        return self.wait_for_indexing(datasource.id)

    def create_gitlab_datasource(self, **kwargs):
        return self.create_code_datasource(
            name=kwargs.get("name", get_random_name()),
            link=kwargs.get("link", os.getenv("GITLAB_PROJECT")),
            branch=kwargs.get("branch", "main"),
            setting_id=kwargs.get("setting_id"),
            embeddings_model=kwargs.get("embeddings_model"),
            project_name=kwargs.get("project_name", PROJECT),
        )

    def create_github_datasource(self, **kwargs):
        return self.create_code_datasource(
            name=kwargs.get("name", get_random_name()),
            link=kwargs.get("link", os.getenv("GITHUB_PROJECT")),
            branch=kwargs.get("branch", "master"),
            setting_id=kwargs.get("setting_id"),
            embeddings_model=kwargs.get("embeddings_model"),
        )

    def update_gitlab_datasource(self, datasource_id, **kwargs):
        return self.update_code_datasource(datasource_id, **kwargs)

    def create_google_doc_datasource(self, **kwargs):
        datasource_name = kwargs.get("name", get_random_name())

        create_request_params = {
            "name": datasource_name,
            "project_name": PROJECT,
            "description": kwargs.get("description", get_random_name()),
            "google_doc": kwargs.get("google_doc"),
            "shared_with_project": kwargs.get("shared_with_project", False),
        }

        create_datasource_request = GoogleDataSourceRequest(**create_request_params)
        self.client.datasources.create(create_datasource_request)

        datasource = wait_for_entity(
            lambda: self.client.datasources.list(per_page=200),
            entity_name=datasource_name,
        )

        return self.wait_for_indexing(datasource.id)

    def update_google_doc_datasource(self, datasource_id, **kwargs):
        datasource = self.get_datasource(datasource_id)

        update_request_params = {
            "name": kwargs.get("name", datasource.name),
            "project_name": datasource.project_name,
            "description": kwargs.get("description", datasource.description),
            "google_doc": kwargs.get("google_doc", datasource.google_doc_link),
            "full_reindex": kwargs.get("full_reindex", False),
            "skip_reindex": kwargs.get("skip_reindex", True),
            "incremental_reindex": kwargs.get("incremental_reindex", False),
        }

        update_datasource_request = UpdateGoogleDataSourceRequest(
            **update_request_params
        )
        self.client.datasources.update(datasource_id, update_datasource_request)

        return self.wait_for_indexing(datasource_id)

    def create_file_datasource(
        self,
        name: str,
        description: str,
        files: List[Union[str, Tuple[str, bytes, str]]],
        shared_with_project: bool = False,
        embeddings_model: str = None,
    ) -> DataSource:
        create_request_params = {
            "name": name,
            "project_name": PROJECT,
            "description": description,
            "shared_with_project": shared_with_project,
            "csv_separator": ";",
            "csv_start_row": 1,
            "csv_rows_per_document": 1000,
            "embeddings_model": embeddings_model,
        }

        create_datasource_request = FileDataSourceRequest(**create_request_params)

        self.client.datasources.create_file_datasource(create_datasource_request, files)

        datasource = wait_for_entity(
            lambda: self.client.datasources.list(per_page=200, filters={"name": name}),
            entity_name=name,
        )

        return self.wait_for_indexing(datasource.id)

    def update_file_datasource(self, datasource_id, **kwargs) -> DataSource:
        datasource = self.get_datasource(datasource_id)

        update_request_params = {
            "name": datasource.name,
            "project_name": datasource.project_name,
            "description": kwargs.get("description", datasource.description),
            "project_space_visible": kwargs.get(
                "project_space_visible", datasource.shared_with_project
            ),
            "full_reindex": kwargs.get("full_reindex", False),
            "skip_reindex": kwargs.get("skip_reindex", True),
            "incremental_reindex": kwargs.get("incremental_reindex", False),
            "embeddings_model": kwargs.get(
                "embeddings_model", datasource.embeddings_model
            ),
        }

        update_datasource_request = UpdateFileDataSourceRequest(**update_request_params)
        self.client.datasources.update(datasource_id, update_datasource_request)

        return self.wait_for_indexing(datasource_id)

    def wait_for_indexing(
        self,
        datasource_id: str,
        timeout: int = int(os.getenv("DEFAULT_TIMEOUT")),
        pool_interval: int = 3,
    ) -> DataSource:
        start_time = time.time()
        while time.time() - start_time < timeout:
            sleep(pool_interval)
            datasource = self.client.datasources.get(datasource_id)
            if datasource.status == DataSourceStatus.COMPLETED:
                return datasource
            elif datasource.status == DataSourceStatus.FAILED:
                raise ApiError(f"Datasource {datasource_id} indexing failed")
        raise TimeoutError("Datasource was not indexed within the timeout period.")

    def get_datasource(self, datasource_id):
        return self.client.datasources.get(datasource_id)

    def create_confluence_datasource(self, **kwargs):
        name = kwargs.get("name", get_random_name())
        create_request_params = {
            "name": name,
            "project_name": kwargs.get("project_name", PROJECT),
            "description": kwargs.get("description", get_random_name()),
            "cql": kwargs.get("cql", os.getenv("CQL")),
            "project_space_visible": kwargs.get("project_space_visible", False),
            "setting_id": kwargs.get("setting_id"),
        }

        create_datasource_request = ConfluenceDataSourceRequest(**create_request_params)
        self.client.datasources.create(create_datasource_request)
        datasource = wait_for_entity(
            lambda: self.client.datasources.list(per_page=200),
            entity_name=name,
        )

        return self.wait_for_indexing(datasource.id)

    def update_confluence_datasource(self, datasource_id, **kwargs):
        datasource = self.get_datasource(datasource_id)

        update_request_params = {
            "name": kwargs.get("name", datasource.name),
            "project_name": datasource.project_name,
            "description": kwargs.get("description", datasource.description),
            "cql": kwargs.get("cql", datasource.confluence.cql),
            "full_reindex": kwargs.get("full_reindex", False),
            "skip_reindex": kwargs.get("skip_reindex", True),
            "incremental_reindex": kwargs.get("incremental_reindex", False),
            "setting_id": kwargs.get("setting_id", datasource.setting_id),
            "project_space_visible": kwargs.get(
                "project_space_visible", datasource.shared_with_project
            ),
        }

        update_datasource_request = UpdateConfluenceDataSourceRequest(
            **update_request_params
        )
        self.client.datasources.update(datasource_id, update_datasource_request)

        return self.wait_for_indexing(datasource_id)

    def create_jira_datasource(self, **kwargs):
        name = kwargs.get("name", get_random_name())
        create_request_params = {
            "name": name,
            "project_name": kwargs.get("project_name", PROJECT),
            "description": kwargs.get("description", get_random_name()),
            "jql": kwargs.get("jql", os.getenv("JQL")),
            "project_space_visible": kwargs.get("project_space_visible", False),
            "setting_id": kwargs.get("setting_id"),
        }

        create_datasource_request = JiraDataSourceRequest(**create_request_params)
        self.client.datasources.create(create_datasource_request)
        datasource = wait_for_entity(
            lambda: self.client.datasources.list(per_page=200),
            entity_name=name,
        )

        return self.wait_for_indexing(datasource.id)

    def update_jira_datasource(self, datasource_id, **kwargs):
        datasource = self.get_datasource(datasource_id)

        update_request_params = {
            "name": kwargs.get("name", datasource.name),
            "project_name": datasource.project_name,
            "description": kwargs.get("description", datasource.description),
            "jql": kwargs.get("jql", datasource.jira.jql),
            "full_reindex": kwargs.get("full_reindex", False),
            "skip_reindex": kwargs.get("skip_reindex", True),
            "incremental_reindex": kwargs.get("incremental_reindex", False),
            "setting_id": kwargs.get("setting_id", datasource.setting_id),
            "project_space_visible": kwargs.get(
                "project_space_visible", datasource.shared_with_project
            ),
        }

        update_datasource_request = UpdateJiraDataSourceRequest(**update_request_params)
        self.client.datasources.update(datasource_id, update_datasource_request)

        return self.wait_for_indexing(datasource_id)

    def delete_datasource(self, datasource):
        return self.client.datasources.delete(datasource.id)
