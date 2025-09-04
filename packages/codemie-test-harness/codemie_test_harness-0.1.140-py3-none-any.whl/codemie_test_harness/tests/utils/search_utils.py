from codemie_sdk.models.integration import IntegrationType
from codemie_test_harness.tests.utils.base_utils import BaseUtils


class SearchUtils(BaseUtils):
    def list_assistants(self, filters):
        return self.client.assistants.list(per_page=100, filters=filters)

    def list_workflows(self, page=0, per_page=100, filters=None, projects=None):
        return self.client.workflows.list(
            page=page, per_page=per_page, filters=filters, projects=projects
        )

    def list_workflow_executions(self, test_workflow_id, page=0, per_page=10):
        return self.client.workflows.executions(test_workflow_id).list(
            page=page, per_page=per_page
        )

    def list_data_sources(
        self,
        projects=None,
        datasource_types=None,
        owner=None,
        status=None,
        filters=None,
        per_page=100,
    ):
        return self.client.datasources.list(
            filters=filters,
            owner=owner,
            status=status,
            datasource_types=datasource_types,
            projects=projects,
            per_page=per_page,
        )

    def list_integrations(self, page=0, per_page=100, setting_type=None, filters=None):
        setting_type = IntegrationType.USER if setting_type is None else setting_type
        return self.client.integrations.list(
            page=page, per_page=per_page, setting_type=setting_type, filters=filters
        )
