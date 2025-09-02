import os

from codemie_sdk.models.workflow import (
    WorkflowCreateRequest,
    WorkflowUpdateRequest,
    WorkflowMode,
)
from codemie_test_harness.tests import PROJECT
from codemie_test_harness.tests.utils import api_domain, verify_ssl
from codemie_test_harness.tests.utils.base_utils import (
    BaseUtils,
    get_random_name,
    wait_for_entity,
    wait_for_completion,
)
from codemie_test_harness.tests.utils.http_utils import RequestHandler

workflow_endpoint = "/v1/workflows"


class WorkflowUtils(BaseUtils):
    def send_request_to_create_workflow_endpoint(
        self, request: WorkflowCreateRequest
    ) -> dict:
        """
        Send request to workflow creation endpoint without raising error for response status codes.

        Args:
            request: The workflow creation request containing required fields:
                    - name: Name of the workflow
                    - description: Description of the workflow
                    - project: Project identifier
                    - yaml_config: YAML configuration for the workflow
                    Optional fields with defaults:
                    - mode: WorkflowMode (defaults to SEQUENTIAL)
                    - shared: bool (defaults to False)
                    - icon_url: Optional URL for workflow icon

        Returns:
            Raw response from '/v1/workflows' endpoint
        """

        request_handler = RequestHandler(api_domain, self.client.token, verify_ssl)

        return request_handler.post(
            workflow_endpoint, dict, json_data=request.model_dump()
        )

    def send_create_workflow_request(
        self,
        workflow_yaml,
        workflow_type=WorkflowMode.SEQUENTIAL,
        workflow_name=None,
        shared=False,
        project=None,
    ):
        workflow_name = get_random_name() if not workflow_name else workflow_name

        request = WorkflowCreateRequest(
            name=workflow_name,
            description="Test Workflow",
            project=project if project else PROJECT,
            mode=workflow_type,
            yaml_config=workflow_yaml,
            shared=shared,
        )

        response = self.client.workflows.create_workflow(request)

        return response, workflow_name

    def create_workflow(
        self,
        workflow_type,
        workflow_yaml,
        workflow_name=None,
        shared=False,
        project_name=None,
    ):
        """
        Sends request to workflow creation endpoint and waits for workflow created.
        """
        response = self.send_create_workflow_request(
            workflow_yaml, workflow_type, workflow_name, shared, project_name
        )

        return wait_for_entity(
            lambda: self.client.workflows.list(per_page=200),
            entity_name=response[1],
        )

    def execute_workflow(self, workflow, execution_name, user_input=""):
        self.client.workflows.run(workflow, user_input=user_input)
        executions = self.client.workflows.executions(workflow)
        execution_id = next(
            row.execution_id for row in executions.list() if row.prompt == user_input
        )
        states_service = executions.states(execution_id)
        state = wait_for_entity(
            lambda: states_service.list(),
            entity_name=execution_name,
        )

        wait_for_completion(execution_state_service=states_service, state_id=state.id)
        return states_service.get_output(state_id=state.id).output

    def update_workflow(
        self,
        workflow,
        name=None,
        description=None,
        yaml_config=None,
        mode=None,
        shared=None,
    ):
        request = WorkflowUpdateRequest(
            name=name if name else workflow.name,
            project=workflow.project,
            description=description if description else workflow.description,
            yaml_config=yaml_config if yaml_config else workflow.yaml_config,
            mode=mode if mode else workflow.mode,
            shared=shared if shared else workflow.shared,
        )
        self.client.workflows.update(workflow.id, request)

        return wait_for_entity(
            lambda: self.client.workflows.list(per_page=200),
            entity_name=workflow.name,
        )

    def get_prebuilt_workflows(self):
        return self.client.workflows.get_prebuilt()

    @staticmethod
    def open_workflow_yaml(path, yaml_file, values: dict = None):
        yaml_path = os.path.join(os.path.dirname(__file__), f"../{path}/{yaml_file}")
        assert os.path.exists(yaml_path), f"YAML file not found: {yaml_path}"

        with open(yaml_path, encoding="utf-8") as file:
            template = file.read()

        return template.format(**values) if values else template

    def delete_workflow(self, workflow):
        self.client.workflows.delete(workflow.id)

    def get_executions(self, workflow):
        return self.client.workflows.executions(workflow.id).list()

    def get_first_execution(self, workflow):
        return self.get_executions(workflow)[0]
