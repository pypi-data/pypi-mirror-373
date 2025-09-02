from codemie_sdk.models.integration import IntegrationType
from codemie_test_harness.tests.utils.base_utils import BaseUtils


class SearchUtils(BaseUtils):
    def list_assistants(self, filters):
        return self.client.assistants.list(per_page=100, filters=filters)

    def list_workflows(self, filters=None, projects=None):
        return self.client.workflows.list(
            per_page=100, filters=filters, projects=projects
        )

    def list_data_sources(
        self,
        projects=None,
        datasource_types=None,
        owner=None,
        status=None,
        filters=None,
    ):
        return self.client.datasources.list(
            per_page=100,
            filters=filters,
            owner=owner,
            status=status,
            datasource_types=datasource_types,
            projects=projects,
        )

    def list_integrations(self, setting_type=None, filters=None):
        setting_type = IntegrationType.USER if setting_type is None else setting_type
        return self.client.integrations.list(
            per_page=100, setting_type=setting_type, filters=filters
        )
