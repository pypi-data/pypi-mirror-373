from typing import Any

from codemie_sdk.models.integration import (
    Integration,
    CredentialTypes,
    CredentialValues,
    IntegrationType,
    IntegrationTestRequest,
)
from codemie_test_harness.tests import PROJECT
from codemie_test_harness.tests.utils.base_utils import (
    BaseUtils,
    wait_for_entity,
    get_random_name,
)


class IntegrationUtils(BaseUtils):
    def create_integration(
        self,
        credential_type: CredentialTypes,
        credential_values: list[CredentialValues],
        setting_type: IntegrationType = None,
        project_name: str = None,
        integration_alias: str = None,
        is_global: bool = False,
    ):
        setting_type = IntegrationType.PROJECT if setting_type is None else setting_type
        integration_alias = (
            get_random_name() if integration_alias is None else integration_alias
        )
        project_name = PROJECT if project_name is None else project_name

        create_request = Integration(
            project_name=project_name,
            credential_type=credential_type,
            credential_values=credential_values,
            alias=integration_alias,
            setting_type=setting_type,
            is_global=is_global,
        )

        self.client.integrations.create(create_request)

        return wait_for_entity(
            lambda: self.client.integrations.list(setting_type, per_page=200),
            entity_name=integration_alias,
        )

    def get_integration_by_alias(
        self, integration_alias: str, integration_type: IntegrationType
    ):
        return self.client.integrations.get_by_alias(
            setting_type=integration_type, alias=integration_alias
        )

    def test_integration(
        self, integration: IntegrationTestRequest, response_type: Any = None
    ):
        if response_type is None:
            response_type = dict
        return self.client.integrations.test(integration, response_type=response_type)

    def update_integration(self, integration: Integration):
        return self.client.integrations.update(
            setting_id=integration.id, settings=integration
        )

    def send_create_integration_request(self, integration: Integration):
        return self.client.integrations.create(settings=integration)

    def delete_integration(self, integration: Integration):
        return self.client.integrations.delete(
            setting_id=integration.id, setting_type=integration.setting_type
        )

    def delete_integrations_by_type(
        self,
        integration_type: IntegrationType,
        credential_type: CredentialTypes,
        project: str = None,
    ):
        integrations = self.client.integrations.list(
            setting_type=integration_type,
            per_page=100,
            filters={"type": credential_type.value, "search": project}
            if project
            else {"type": credential_type.value},
        )
        for integration in integrations:
            self.client.integrations.delete(
                setting_id=integration.id, setting_type=integration_type
            )

    def create_user_integration(
        self,
        credential_type: CredentialTypes,
        credentials: list[CredentialValues],
        project_name: str = None,
    ):
        return self.create_integration(
            credential_type=credential_type,
            credential_values=credentials,
            setting_type=IntegrationType.USER,
            project_name=project_name,
            is_global=False,
        )

    def create_global_integration(
        self,
        credential_type: CredentialTypes,
        credentials: list[CredentialValues],
        project_name: str = None,
    ):
        return self.create_integration(
            credential_type=credential_type,
            credential_values=credentials,
            setting_type=IntegrationType.USER,
            project_name=project_name,
            is_global=True,
        )

    def create_project_integration(
        self,
        credential_type: CredentialTypes,
        credentials: list[CredentialValues],
        project_name: str = None,
    ):
        return self.create_integration(
            credential_type=credential_type,
            credential_values=credentials,
            setting_type=IntegrationType.PROJECT,
            project_name=project_name,
            is_global=False,
        )
