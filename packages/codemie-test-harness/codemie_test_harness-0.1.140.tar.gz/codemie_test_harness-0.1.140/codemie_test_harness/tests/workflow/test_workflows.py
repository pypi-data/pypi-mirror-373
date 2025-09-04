import json

import pytest
from hamcrest import assert_that, equal_to

from codemie_test_harness.tests.test_data.output_schema_test_data import output_schema
from codemie_test_harness.tests.utils.base_utils import get_random_name
from codemie_test_harness.tests.utils.yaml_utils import AssistantModel, StateModel


@pytest.mark.regression
@pytest.mark.smoke
def test_workflow_with_json_output_schema(default_llm, workflow, workflow_utils):
    assistant_and_state_name = get_random_name()

    assistant = AssistantModel(
        id=assistant_and_state_name,
        model=default_llm.base_name,
        system_prompt="You are a helpful assistant.",
    )

    state = StateModel(
        id=assistant_and_state_name,
        assistant_id=assistant_and_state_name,
        output_schema=json.dumps(output_schema),
    )

    workflow = workflow(
        workflow_name=get_random_name(),
        assistant_model=assistant,
        state_model=state,
    )

    response = workflow_utils.execute_workflow(
        workflow.id, assistant_and_state_name, user_input="1+1?"
    )

    assert_that(json.loads(response)["results"][0], equal_to(2))
