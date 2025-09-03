from codemie_sdk import CodeMieClient
from hamcrest import assert_that, greater_than_or_equal_to

from codemie_test_harness.tests.utils.base_utils import (
    wait_for_entity,
    wait_for_completion,
    clean_json,
)


class SimilarityCheck:
    def __init__(self, client: CodeMieClient, workflow_id: str):
        self.client = client
        self.workflow_id = workflow_id

    def check_similarity(
        self, actual: str, expected: str, similarity_rank=60, assistant_name: str = ""
    ):
        user_prompt = f"<text1>: {actual}, <text2>: {expected}"
        self.client.workflows.run(self.workflow_id, user_prompt)
        executions = self.client.workflows.executions(self.workflow_id)
        execution_id = [row for row in executions.list() if row.prompt == user_prompt][
            0
        ].execution_id
        states_service = executions.states(execution_id)
        state = wait_for_entity(
            lambda: states_service.list(),
            entity_name="similarity_analysis",
        )
        wait_for_completion(execution_state_service=states_service, state_id=state.id)
        output = states_service.get_output(state_id=state.id).output
        output = int(clean_json(output).get("similarity_rank"))
        assert_that(
            output,
            greater_than_or_equal_to(similarity_rank),
            f"Llm answer does not match the expected answer. \nactual: {actual}, \nexpected: {expected}, \nassistant_name: {assistant_name}\n",
        )
