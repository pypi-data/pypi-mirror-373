from codemie_test_harness.tests.enums.tools import OpenApiTool

INVOKE_API_TOOL_TASK = (
    "Invoke GET /v1/info endpoint. Url you can get from tools available"
)

RESPONSE_FOR_INVOKE_API = """
    Here are the details from the `/v1/info` endpoint:

    - **Message:** Codemie
    - **Version:** 0.28.0-SNAPSHOT.2
    - **Description:** Smart AI assistant 'CodeMie'
    
    If you need further details or assistance, feel free to ask!
"""

OPEN_API_SPEC_TOOL_TASK = "Provide the details about '/v1/assistants' endpoint"

RESPONSE_FOR_OPEN_API_SPEC = """
    The `/v1/assistants` endpoint supports both `GET` and `POST` methods. Here are the details:

    ### GET `/v1/assistants`
    Returns all saved assistants.
    
    - **Tags:** Assistant
    - **Summary:** Index Assistants
    - **Description:** Returns all saved assistants.
    - **Operation ID:** index_assistants_v1_assistants_get
    - **Security:**
      - user-id
      - Authorization
    - **Parameters:**
      - `scope` (query, optional): The scope of assistants to retrieve. Default is `visible_to_user`.
      - `minimal_response` (query, optional): Minimal response flag. Default is `false`.
      - `filters` (query, optional): Filters for the assistants.
      - `page` (query, optional): The page number. Default is `0`.
      - `per_page` (query, optional): Number of items per page. Default is `12`.
    - **Responses:**
      - `200` Successful Response: Returns an array of AssistantListResponse.
      - `422` Validation Error
    
    ### POST `/v1/assistants`
    Creates a new assistant.
    
    - **Tags:** Assistant
    - **Summary:** Create Assistant
    - **Description:** Index user-specific assistant to Elastic with project field.
    - **Operation ID:** create_assistant_v1_assistants_post
    - **Security:**
      - user-id
      - Authorization
    - **Request Body:**
      - Required. The request body must conform to the AssistantRequest schema.
    - **Responses:**
      - `200` Successful Response: Returns a BaseResponse.
      - `422` Validation Error
    
    These endpoints relate to managing assistants, allowing you to list and create assistants in the system.
"""

open_api_tools_test_data = [
    (
        (OpenApiTool.INVOKE_EXTERNAL_API, OpenApiTool.GET_OPEN_API_SPEC),
        INVOKE_API_TOOL_TASK,
        RESPONSE_FOR_INVOKE_API,
    ),
    (
        OpenApiTool.INVOKE_EXTERNAL_API,
        OPEN_API_SPEC_TOOL_TASK,
        RESPONSE_FOR_OPEN_API_SPEC,
    ),
]
