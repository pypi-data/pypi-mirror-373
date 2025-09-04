# Workflow validation error messages

INVALID_YAML_PROVIDED = "Invalid YAML config was provided:"

ASSISTANT_NOT_EXIST = [
    "Assistants do not exist:coverage_assistant -> e3bb4613-d3ed-4391-8350-8702175b0e2x"
]

ASSISTANT_NOT_EXIST_IN_STATE = [
    f"{INVALID_YAML_PROVIDED} 1) In 'coverage' state: 'assistant_id' key references undefined 'another_assistant' assistant"
]

INVALID_YAML = ["Invalid YAML format was provided"]

INVALID_DATA_SOURCE = ["No index_info found with id datasource_id"]

INVALID_TOOL = ["Tools (referenced in assistant definitions) do not exist:Invalid-tool"]

INVALID_STATE = [
    f"{INVALID_YAML_PROVIDED} 1) In 'states[0]': one and only one of 'custom_node_id' or 'tool_id' or 'assistant_id' must be set",
    f"{INVALID_YAML_PROVIDED} 1) In 'states[0]': one and only one of 'assistant_id' or 'custom_node_id' or 'tool_id' must be set",
    f"{INVALID_YAML_PROVIDED} 1) In 'states[0]': one and only one of 'custom_node_id' or 'assistant_id' or 'tool_id' must be set",
    f"{INVALID_YAML_PROVIDED} 1) In 'states[0]': one and only one of 'assistant_id' or 'tool_id' or 'custom_node_id' must be set",
    f"{INVALID_YAML_PROVIDED} 1) In 'states[0]': one and only one of 'tool_id' or 'custom_node_id' or 'assistant_id' must be set",
    f"{INVALID_YAML_PROVIDED} 1) In 'states[0]': one and only one of 'tool_id' or 'assistant_id' or 'custom_node_id' must be set",
]

MISSING_STATES = ["Workflow must have at least one valid state"]

MISSING_ASSISTANT_ID = [
    f"{INVALID_YAML_PROVIDED} 1) In 'assistants[0]': 'id' is required"
]

MISSING_SYSTEM_PROMPT = [
    f"{INVALID_YAML_PROVIDED} 1) In 'assistants[0]': at least one of 'system_prompt' or 'assistant_id' must be set",
    f"{INVALID_YAML_PROVIDED} 1) In 'assistants[0]': at least one of 'assistant_id' or 'system_prompt' must be set",
]

MISSING_TOOL_NAME = [
    f"{INVALID_YAML_PROVIDED} 1) In 'assistants[0].tools[0]': 'name' is required"
]

MISSING_TOOLS_ID = [f"{INVALID_YAML_PROVIDED} 1) In 'tools[0]': 'id' is required"]

MISSING_TOOLS_NAME = [f"{INVALID_YAML_PROVIDED} 1) In 'tools[0]': 'tool' is required"]

MISSING_STATES_ID = [f"{INVALID_YAML_PROVIDED} 1) In 'states[0]': 'id' is required"]

MISSING_STATES_NEXT = [f"{INVALID_YAML_PROVIDED} 1) In 'states[0]': 'next' is required"]

MISSING_STATES_NEXT_CONDITION_EXPRESSION = [
    f"{INVALID_YAML_PROVIDED} 1) In 'states[0].next.condition': 'expression' is required"
]

MISSING_STATES_NEXT_CONDITION_THEN = [
    f"{INVALID_YAML_PROVIDED} 1) In 'states[0].next.condition': 'then' is required"
]

MISSING_STATES_NEXT_CONDITION_OTHERWISE = [
    f"{INVALID_YAML_PROVIDED} 1) In 'states[0].next.condition': 'otherwise' is required"
]

MISSING_STATES_NEXT_SWITCH_CASES = [
    f"{INVALID_YAML_PROVIDED} 1) In 'states[0].next.switch': 'cases' is required"
]

MISSING_STATES_NEXT_SWITCH_DEFAULT = [
    f"{INVALID_YAML_PROVIDED} 1) In 'states[0].next.switch': 'default' is required"
]

MISSING_STATES_NEXT_SWITCH_CASES_CONDITION = [
    f"{INVALID_YAML_PROVIDED} 1) In 'states[0].next.switch.cases[0]': 'condition' is required"
]

MISSING_STATES_NEXT_SWITCH_CASES_STATE_ID = [
    f"{INVALID_YAML_PROVIDED} 1) In 'states[0].next.switch.cases[0]': 'state_id' is required"
]

INVALID_YAML_FORMAT_PROVIDED = ["Invalid YAML format was provided"]
