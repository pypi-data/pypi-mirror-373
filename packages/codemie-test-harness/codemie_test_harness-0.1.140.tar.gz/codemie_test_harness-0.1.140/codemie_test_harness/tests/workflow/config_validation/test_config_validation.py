import re

import pytest
from hamcrest import assert_that

from codemie_sdk.models.workflow import WorkflowCreateRequest
from codemie_test_harness.tests import PROJECT
from codemie_test_harness.tests.test_data.workflow_validation_messages import (
    ASSISTANT_NOT_EXIST,
    ASSISTANT_NOT_EXIST_IN_STATE,
    INVALID_YAML,
    INVALID_DATA_SOURCE,
    INVALID_TOOL,
    INVALID_STATE,
    MISSING_STATES,
    MISSING_ASSISTANT_ID,
    MISSING_SYSTEM_PROMPT,
    MISSING_TOOL_NAME,
    MISSING_TOOLS_ID,
    MISSING_TOOLS_NAME,
    MISSING_STATES_ID,
    MISSING_STATES_NEXT,
    MISSING_STATES_NEXT_CONDITION_EXPRESSION,
    MISSING_STATES_NEXT_CONDITION_THEN,
    MISSING_STATES_NEXT_CONDITION_OTHERWISE,
    MISSING_STATES_NEXT_SWITCH_CASES,
    MISSING_STATES_NEXT_SWITCH_DEFAULT,
    MISSING_STATES_NEXT_SWITCH_CASES_CONDITION,
    MISSING_STATES_NEXT_SWITCH_CASES_STATE_ID,
    INVALID_YAML_FORMAT_PROVIDED,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name

# Map of test yaml file names to expected error messages (as in Java test)
VALIDATION_TEST_DATA = [
    ("invalid_assistant_id.yaml", ASSISTANT_NOT_EXIST),
    ("invalid_assistant_in_state.yaml", ASSISTANT_NOT_EXIST_IN_STATE),
    ("invalid_yaml.yaml", INVALID_YAML),
    ("invalid_data_source.yaml", INVALID_DATA_SOURCE),
    ("invalid_tool.yaml", INVALID_TOOL),
    ("invalid_state.yaml", INVALID_STATE),
    ("missing_required_states.yaml", MISSING_STATES),
    ("missing_required_assistant_id.yaml", MISSING_ASSISTANT_ID),
    ("missing_required_system_prompt.yaml", MISSING_SYSTEM_PROMPT),
    ("missing_required_assistant_tools_name.yaml", MISSING_TOOL_NAME),
    ("missing_required_tools_id.yaml", MISSING_TOOLS_ID),
    ("missing_required_tools_name.yaml", MISSING_TOOLS_NAME),
    ("missing_required_states_id.yaml", MISSING_STATES_ID),
    ("missing_required_states_next.yaml", MISSING_STATES_NEXT),
    (
        "missing_required_states_next_condition_expression.yaml",
        MISSING_STATES_NEXT_CONDITION_EXPRESSION,
    ),
    (
        "missing_required_states_next_condition_then.yaml",
        MISSING_STATES_NEXT_CONDITION_THEN,
    ),
    (
        "missing_required_states_next_condition_otherwise.yaml",
        MISSING_STATES_NEXT_CONDITION_OTHERWISE,
    ),
    (
        "missing_required_states_next_switch_cases.yaml",
        MISSING_STATES_NEXT_SWITCH_CASES,
    ),
    (
        "missing_required_states_next_switch_default.yaml",
        MISSING_STATES_NEXT_SWITCH_DEFAULT,
    ),
    (
        "missing_required_states_next_switch_cases_condition.yaml",
        MISSING_STATES_NEXT_SWITCH_CASES_CONDITION,
    ),
    (
        "missing_required_states_next_switch_cases_state_id.yaml",
        MISSING_STATES_NEXT_SWITCH_CASES_STATE_ID,
    ),
    ("invalid_yaml_format.yaml", INVALID_YAML_FORMAT_PROVIDED),
]

# Path to invalid config yamls (relative to repo root)
INVALID_CONFIG_PATH = "test_data/workflow/invalid_config/"


@pytest.mark.parametrize(
    "file_name, expected_errors",
    VALIDATION_TEST_DATA,
    ids=[f"{row[0]}" for row in VALIDATION_TEST_DATA],
)
@pytest.mark.testcase("EPMCDME-5458")
@pytest.mark.regression
@pytest.mark.smoke
def test_create_workflow_with_invalid_config(
    workflow_utils, file_name, expected_errors
):
    yaml_config = workflow_utils.open_workflow_yaml(INVALID_CONFIG_PATH, file_name)

    request = WorkflowCreateRequest(
        name=get_random_name(),
        description="Test Workflow",
        project=PROJECT,
        yaml_config=yaml_config,
    )

    # Attempt to create workflow with invalid YAML config
    response = workflow_utils.send_request_to_create_workflow_endpoint(request)

    message = response.get("error").get("details")
    cleaned_message = re.sub(r" {2,}", " ", message).replace("<br>", "")

    # Check if the error message matches the expected error
    assert_that(
        any(item in cleaned_message for item in expected_errors),
        "Unexpected error message in workflow creation response",
    )
