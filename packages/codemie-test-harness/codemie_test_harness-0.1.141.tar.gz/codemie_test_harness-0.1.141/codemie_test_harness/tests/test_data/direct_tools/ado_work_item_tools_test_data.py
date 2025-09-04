from codemie_test_harness.tests.enums.tools import Toolkit, AzureDevOpsWorkItemTool

ado_work_item_get_test_data = [
    (
        Toolkit.AZURE_DEVOPS_WORK_ITEM,
        AzureDevOpsWorkItemTool.GET_WORK_ITEM,
        {"id": "5296"},
        """
            {
              "id" : 5296,
              "url" : "https://dev.azure.com/AntonYeromin/_workitems/edit/5296",
              "System.AreaPath" : "CodemieAnton",
              "System.TeamProject" : "CodemieAnton",
              "System.IterationPath" : "CodemieAnton",
              "System.WorkItemType" : "Task",
              "System.State" : "To Do",
              "System.Reason" : "Added to backlog",
              "System.CreatedDate" : "2025-07-30T11:39:49.453Z",
              "System.CreatedBy" : {
                "displayName" : "Anton Yeromin",
                "url" : "https://spsprodneu1.vssps.visualstudio.com/Add1f60ac-c7d4-4a5f-b497-bdb733dc5847/_apis/Identities/7bfb0794-d7d6-6d0b-be18-a8c9cbedead2",
                "_links" : {
                  "avatar" : {
                    "href" : "https://dev.azure.com/AntonYeromin/_apis/GraphProfile/MemberAvatars/aad.N2JmYjA3OTQtZDdkNi03ZDBiLWJlMTgtYThjOWNiZWRlYWQy"
                  }
                },
                "id" : "7bfb0794-d7d6-6d0b-be18-a8c9cbedead2",
                "uniqueName" : "Anton_Yeromin@epam.com",
                "imageUrl" : "https://dev.azure.com/AntonYeromin/_apis/GraphProfile/MemberAvatars/aad.N2JmYjA3OTQtZDdkNi03ZDBiLWJlMTgtYThjOWNiZWRlYWQy",
                "descriptor" : "aad.N2JmYjA3OTQtZDdkNi03ZDBiLWJlMTgtYThjOWNiZWRlYWQy"
              },
              "System.ChangedDate" : "2025-07-30T11:39:49.453Z",
              "System.ChangedBy" : {
                "displayName" : "Anton Yeromin",
                "url" : "https://spsprodneu1.vssps.visualstudio.com/Add1f60ac-c7d4-4a5f-b497-bdb733dc5847/_apis/Identities/7bfb0794-d7d6-6d0b-be18-a8c9cbedead2",
                "_links" : {
                  "avatar" : {
                    "href" : "https://dev.azure.com/AntonYeromin/_apis/GraphProfile/MemberAvatars/aad.N2JmYjA3OTQtZDdkNi03ZDBiLWJlMTgtYThjOWNiZWRlYWQy"
                  }
                },
                "id" : "7bfb0794-d7d6-6d0b-be18-a8c9cbedead2",
                "uniqueName" : "Anton_Yeromin@epam.com",
                "imageUrl" : "https://dev.azure.com/AntonYeromin/_apis/GraphProfile/MemberAvatars/aad.N2JmYjA3OTQtZDdkNi03ZDBiLWJlMTgtYThjOWNiZWRlYWQy",
                "descriptor" : "aad.N2JmYjA3OTQtZDdkNi03ZDBiLWJlMTgtYThjOWNiZWRlYWQy"
              },
              "System.CommentCount" : 0,
              "System.Title" : "This is test task for testing azure devops integration",
              "Microsoft.VSTS.Common.StateChangeDate" : "2025-07-30T11:39:49.453Z",
              "Microsoft.VSTS.Common.Priority" : 2,
              "System.Description" : "<div>Some task description<br> </div>"
            }
        """,
    ),
    (
        Toolkit.AZURE_DEVOPS_WORK_ITEM,
        AzureDevOpsWorkItemTool.GET_COMMENTS,
        {"work_item_id": "4"},
        """
            [ {
              "url" : "https://dev.azure.com/AntonYeromin/9d40cdc1-5404-4d40-8025-e5267d69dc89/_apis/wit/workItems/4/comments/938412",
              "created_by" : {
                "_links" : { },
                "descriptor" : "aad.MGEwODUxMjItZTgxZi03ZjFkLWJmNDgtM2YwOWVjZWExNzJj",
                "display_name" : "Andrei Maskouchanka",
                "url" : "https://spsprodneu1.vssps.visualstudio.com/Add1f60ac-c7d4-4a5f-b497-bdb733dc5847/_apis/Identities/0a085122-e81f-6f1d-bf48-3f09ecea172c",
                "id" : "0a085122-e81f-6f1d-bf48-3f09ecea172c",
                "image_url" : "https://dev.azure.com/AntonYeromin/_apis/GraphProfile/MemberAvatars/aad.MGEwODUxMjItZTgxZi03ZjFkLWJmNDgtM2YwOWVjZWExNzJj",
                "unique_name" : "Andrei_Maskouchanka@epam.com"
              },
              "created_date" : "2025-04-17T13:30:56.817Z",
              "format" : "html",
              "id" : 938412,
              "mentions" : [ ],
              "modified_by" : {
                "_links" : { },
                "descriptor" : "aad.MGEwODUxMjItZTgxZi03ZjFkLWJmNDgtM2YwOWVjZWExNzJj",
                "display_name" : "Andrei Maskouchanka",
                "url" : "https://spsprodneu1.vssps.visualstudio.com/Add1f60ac-c7d4-4a5f-b497-bdb733dc5847/_apis/Identities/0a085122-e81f-6f1d-bf48-3f09ecea172c",
                "id" : "0a085122-e81f-6f1d-bf48-3f09ecea172c",
                "image_url" : "https://dev.azure.com/AntonYeromin/_apis/GraphProfile/MemberAvatars/aad.MGEwODUxMjItZTgxZi03ZjFkLWJmNDgtM2YwOWVjZWExNzJj",
                "unique_name" : "Andrei_Maskouchanka@epam.com"
              },
              "modified_date" : "2025-04-17T13:36:33.127Z",
              "rendered_text" : "",
              "text" : "<div>GodeMie test for ADO Work Item tool.</div>",
              "version" : 2,
              "work_item_id" : 4
            } ]
        """,
    ),
    (
        Toolkit.AZURE_DEVOPS_WORK_ITEM,
        AzureDevOpsWorkItemTool.GET_RELATION_TYPES,
        {},
        """
            {
              "Affects" : "Microsoft.VSTS.Common.Affects-Forward",
              "Affected By" : "Microsoft.VSTS.Common.Affects-Reverse",
              "Referenced By" : "Microsoft.VSTS.TestCase.SharedParameterReferencedBy-Forward",
              "References" : "Microsoft.VSTS.TestCase.SharedParameterReferencedBy-Reverse",
              "Tested By" : "Microsoft.VSTS.Common.TestedBy-Forward",
              "Tests" : "Microsoft.VSTS.Common.TestedBy-Reverse",
              "Test Case" : "Microsoft.VSTS.TestCase.SharedStepReferencedBy-Forward",
              "Shared Steps" : "Microsoft.VSTS.TestCase.SharedStepReferencedBy-Reverse",
              "Produces For" : "System.LinkTypes.Remote.Dependency-Forward",
              "Consumes From" : "System.LinkTypes.Remote.Dependency-Reverse",
              "Duplicate" : "System.LinkTypes.Duplicate-Forward",
              "Duplicate Of" : "System.LinkTypes.Duplicate-Reverse",
              "Successor" : "System.LinkTypes.Dependency-Forward",
              "Predecessor" : "System.LinkTypes.Dependency-Reverse",
              "Child" : "System.LinkTypes.Hierarchy-Forward",
              "Parent" : "System.LinkTypes.Hierarchy-Reverse",
              "Related" : "System.LinkTypes.Related",
              "Remote Related" : "System.LinkTypes.Remote.Related",
              "Attached File" : "AttachedFile",
              "Hyperlink" : "Hyperlink",
              "Artifact Link" : "ArtifactLink"
            }
        """,
    ),
    (
        Toolkit.AZURE_DEVOPS_WORK_ITEM,
        AzureDevOpsWorkItemTool.SEARCH_WORK_ITEMS,
        {
            "query": "SELECT [System.Id], [System.Title], [System.State] FROM WorkItems WHERE [System.TeamProject] = "
            "'CodemieAnton' AND [System.WorkItemType] = 'Task' AND [System.State] <> 'Closed' ORDER BY "
            "[System.CreatedDate] ASC",
            "limit": 1,
        },
        """
            [ {
              "id" : 30,
              "url" : "https://dev.azure.com/AntonYeromin/_workitems/edit/30",
              "System.Title" : "Autotest Task TnKIcP",
              "System.State" : "To Do",
              "System.AssignedTo" : "N/A",
              "System.CreatedDate" : "2025-04-21T06:50:40.987Z",
              "System.ChangedDate" : "2025-04-21T06:50:40.987Z"
            } ]
        """,
    ),
]
