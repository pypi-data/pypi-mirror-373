from codemie_test_harness.tests.enums.tools import Toolkit, AzureDevOpsTestPlanTool

ado_test_plan_get_test_data = [
    (
        Toolkit.AZURE_DEVOPS_TEST_PLAN,
        AzureDevOpsTestPlanTool.GET_TEST_PLAN,
        "Show the Test Plan with ID 24. Provide output in json format",
        """
            ```json
            [
                {
                    "area_path": "CodemieAnton",
                    "iteration": "CodemieAnton",
                    "name": "This is the first test plan",
                    "state": "Active",
                    "revision": 0,
                    "_links": {},
                    "id": 24,
                    "project": {
                        "id": "9d40cdc1-5404-4d40-8025-e5267d69dc89",
                        "last_update_time": "0001-01-01T00:00:00.000Z",
                        "name": "CodemieAnton",
                        "state": "unchanged",
                        "visibility": "unchanged"
                    },
                    "root_suite": {
                        "id": 25,
                        "name": "This is the first test plan"
                    }
                }
            ]
            ```
            """,
    ),
    (
        Toolkit.AZURE_DEVOPS_TEST_PLAN,
        AzureDevOpsTestPlanTool.GET_TEST_CASE,
        """
            Show the info about test case with ID 26 in suite with ID 25 in test plan with ID 24.
            Data to show: Title, Automation Status, Priority, Description.
        """,
        """
            Here is the information about the test case with ID 26 in the suite with ID 25 in the test plan with ID 24:

            - **Title**: The First Test Case
            - **Automation Status**: Not Automated
            - **Priority**: 2
            - **Description**: This is the first test case
        """,
    ),
    (
        Toolkit.AZURE_DEVOPS_TEST_PLAN,
        AzureDevOpsTestPlanTool.GET_TEST_CASES,
        """
            Show the info about all test cases in suite with ID 25 in test plan with ID 24.
            Data to show: Title, Automation Status, Priority, Description.
        """,
        """
            Here are the details for all test cases in the suite with ID 25 in the test plan with ID 24:

            ### Test Case 1
            - **Title**: The First Test Case
            - **Automation Status**: Not Automated
            - **Priority**: 2
            - **Description**: This is the first test case
            
            ### Test Case 2
            - **Title**: The Second Test Case
            - **Automation Status**: Not Automated
            - **Priority**: 2
            - **Description**: This is the second test case
        """,
    ),
    (
        Toolkit.AZURE_DEVOPS_TEST_PLAN,
        AzureDevOpsTestPlanTool.GET_TEST_SUITE,
        "Show the info about all suites in test plan with ID 24.",
        """
            Here is the information about all suites in test plan with ID 24:

            ~~~markdown
            ### Test Suite ID: 25
            - **Name:** This is the first test plan
            - **Suite Type:** Static Test Suite
            - **Default Configurations:**
              - **ID:** 1
              - **Name:** Windows 10
            - **Inherit Default Configurations:** False
            - **Last Updated By:**
              - **Name:** Andrei Maskouchanka
              - **Email:** Andrei_Maskouchanka@epam.com
            - **Last Updated Date:** 2025-04-21T07:38:57.600Z
            - **Plan:**
              - **ID:** 24
              - **Name:** This is the first test plan
            - **Project:**
              - **ID:** 9d40cdc1-5404-4d40-8025-e5267d69dc89
              - **Name:** CodemieAnton
              - **URL:** [CodemieAnton Project](https://dev.azure.com/AntonYeromin/_apis/projects/CodemieAnton)
            ~~~
        """,
    ),
]

ADO_TEST_PLAN_CREATE_TEST_PLAN = {
    "prompt_to_assistant": """
        Create a new test plan with name '{}' in 'CodemieAnton' project.
        Provide short summary about result and the ID of created test plan in Json format: {{ "ID": "Number" }}
    """,
    "expected_llm_answer": """
        The test plan named '{}' has been successfully created in the 'CodemieAnton' project. 
        Below is the summary of the result:

        ~~~json
        {{
          "ID": {}
        }}
        ~~~
    """,
}

ADO_TEST_PLAN_CREATE_SUITE = {
    "prompt_to_assistant": """
        Create a new test suite with random name
        use 'StaticTestSuite' type
        use parent suite ID {}
        use Test Plan ID {}.
        Provide short summary about result and the ID of created suite in Json format: {{ "ID": "Number" }}
    """,
    "expected_llm_answer": """
        The test suite was created successfully. Here is the summary and ID of the created suite:

        ```json
        {{
          "ID": {}
        }}
        ```
    """,
}

ADO_TEST_PLAN_ADD_TEST_CASE = {
    "prompt_to_assistant": """
        Add the test case with ID 26 to the test suite with ID {}. Use test plan with ID {}.
    """,
    "expected_llm_answer": "The test case with ID 26 has been successfully added to the test suite with ID {} under the test plan with ID {}.",
}

ADO_TEST_PLAN_DELETE_SUITE = {
    "prompt_to_assistant": "Delete the Test Suite with ID {} under the Test Plan with ID {} in 'CodemieAnton' project.",
    "expected_llm_answer": """
        The Test Suite with ID '{}' under the Test Plan with ID '{}' in the 'CodemieAnton' project has been successfully deleted.
    """,
}

ADO_TEST_PLAN_DELETE_PLAN = {
    "prompt_to_assistant": "Delete the Test Plan with ID {} in 'CodemieAnton' project.",
    "expected_llm_answer": "The test plan with ID `{}` in the `CodemieAnton` project has been successfully deleted.",
}
