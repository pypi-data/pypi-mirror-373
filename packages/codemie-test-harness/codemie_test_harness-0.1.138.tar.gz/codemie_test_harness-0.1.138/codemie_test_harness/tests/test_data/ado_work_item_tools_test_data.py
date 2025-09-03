from codemie_test_harness.tests.enums.tools import Toolkit, AzureDevOpsWorkItemTool

ado_work_item_get_test_data = [
    (
        Toolkit.AZURE_DEVOPS_WORK_ITEM,
        AzureDevOpsWorkItemTool.GET_WORK_ITEM,
        "Show work item with id 5296",
        """Here are the details of the work item with ID 5296:

            - **ID:** 5296
            - **Title:** This is test task for testing azure devops integration
            - **State:** To Do
            - **Reason:** Added to backlog
            - **Area Path:** CodemieAnton
            - **Iteration Path:** CodemieAnton
            - **Work Item Type:** Task
            - **Created Date:** July 30, 2025
            - **Created By:** Anton Yeromin
            - **Changed Date:** July 30, 2025
            - **Changed By:** Anton Yeromin
            - **Comment Count:** 0
            - **Priority:** 2
            - **Description:** Some task description

            For more details, you can view the work item [here](https://dev.azure.com/AntonYeromin/_workitems/edit/5296).
        """,
    ),
    (
        Toolkit.AZURE_DEVOPS_WORK_ITEM,
        AzureDevOpsWorkItemTool.GET_COMMENTS,
        "Show the comments of work item with ID=4",
        """
            ### Comments for Work Item ID 4

            - **Comment ID:** 938412
            - **Created By:** [Andrei Maskouchanka](https://spsprodneu1.vssps.visualstudio.com/Add1f60ac-c7d4-4a5f-b497-bdb733dc5847/_apis/Identities/0a085122-e81f-6f1d-bf48-3f09ecea172c)
            - **Created Date:** 2025-04-17T13:30:56.817Z
            - **Modified By:** [Andrei Maskouchanka](https://spsprodneu1.vssps.visualstudio.com/Add1f60ac-c7d4-4a5f-b497-bdb733dc5847/_apis/Identities/0a085122-e81f-6f1d-bf48-3f09ecea172c)
            - **Modified Date:** 2025-04-17T13:30:56.817Z
            - **Text:**
              ~~~markdown
              GodeMie test for ADO Work Item tool.
              ~~~
            
            You can view the comment [here](https://dev.azure.com/AntonYeromin/9d40cdc1-5404-4d40-8025-e5267d69dc89/_apis/wit/workItems/4/comments/938412).
        """,
    ),
    (
        Toolkit.AZURE_DEVOPS_WORK_ITEM,
        AzureDevOpsWorkItemTool.GET_RELATION_TYPES,
        "Show the relation types available. Provide the list of types only.",
        """
            Here are the available relation types:
            
            - Affects
            - Affected By
            - Referenced By
            - References
            - Tested By
            - Tests
            - Test Case
            - Shared Steps
            - Produces For
            - Consumes From
            - Duplicate
            - Duplicate Of
            - Successor
            - Predecessor
            - Child
            - Parent
            - Related
            - Remote Related
            - Attached File
            - Hyperlink
            - Artifact Link
        """,
    ),
    (
        Toolkit.AZURE_DEVOPS_WORK_ITEM,
        AzureDevOpsWorkItemTool.SEARCH_WORK_ITEMS,
        """
            Search Work Items using this query: SELECT [System.Id], [System.Title], [System.State]
                                        FROM WorkItems
                                        WHERE [System.TeamProject] = 'CodemieAnton'
                                          AND [System.WorkItemType] = 'Task'
                                          AND [System.State] <> 'Closed'
                                        ORDER BY [System.CreatedDate] ASC;
                    Return tge only first item.
                    Output Format:
                    **ID**: <id>
                       - **Title**: <title>
                       - **State**: <state>
                       - **URL**: <url>
        """,
        """
            Here are the work items matching your query:
            1. **ID**: 30
               - **Title**: Autotest Task TnKIcP
               - **State**: To Do
               - **URL**: [Work Item #30](https://dev.azure.com/AntonYeromin/_workitems/edit/30).
        """,
    ),
]

ADO_WORK_ITEM_CREATE = {
    "prompt_to_assistant": """
        Create a new Work Item with type 'Task' and title '{}' and description 'Greeting from CodeMie!'
        in the project 'CodemieAnton'. Provide the details about created Work Item.
    """,
    "expected_llm_answer": """
        The work item has been successfully created. Below are the details:

        - **Title**: {}
        - **Description**: Greeting from CodeMie!
        - **Type**: Task
        - **Project**: CodemieAnton
        
        You can view the work item using [this link](https://dev.azure.com/AntonYeromin/9d40cdc1-5404-4d40-8025-e5267d69dc89/_apis/wit/workItems/6).
    """,
}

ADO_WORK_ITEM_UPDATE = {
    "prompt_to_assistant": """
        Update the Work Item with the ID '{}' in the project 'CodemieAnton'.
        Change the type to 'Epic' and title to '{}' and description to 'Updated description'.
    """,
    "expected_llm_answer": """
        The work item with ID `{}` in the project `CodemieAnton` has been successfully updated with the following changes:
        - Type: `Epic`
        - Title: `{}`
        - Description: `Updated description`
    """,
}

ADO_WORK_ITEM_LINK = {
    "prompt_to_assistant": """
        Run {{'source_id': {}, 'target_id': 5296, 'link_type': 'System.LinkTypes.Hierarchy-Reverse'}} to
        link the Work Items with the ID 5296 to be the parent of Work Item with ID '{}' in
        the project 'CodemieAnton'
    """,
    "expected_llm_answer": """
        The Work Item with ID 5296 has been successfully linked as the parent of the Work Item with ID `{}`
        using the `System.LinkTypes.Hierarchy-Reverse` link type.
    """,
}
