from codemie_test_harness.tests.enums.tools import Toolkit, AzureDevOpsTestPlanTool

ado_test_plan_get_test_data = [
    (
        Toolkit.AZURE_DEVOPS_TEST_PLAN,
        AzureDevOpsTestPlanTool.GET_TEST_PLAN,
        {"plan_id": 24},
        """
            {
                  "area_path" : "CodemieAnton",
                  "end_date" : "2025-04-25T13:24:57.037Z",
                  "iteration" : "CodemieAnton",
                  "name" : "This is the first test plan",
                  "owner" : {
                    "_links" : { },
                    "descriptor" : "aad.MGEwODUxMjItZTgxZi03ZjFkLWJmNDgtM2YwOWVjZWExNzJj",
                    "display_name" : "Andrei Maskouchanka",
                    "url" : "https://spsprodneu1.vssps.visualstudio.com/Add1f60ac-c7d4-4a5f-b497-bdb733dc5847/_apis/Identities/0a085122-e81f-6f1d-bf48-3f09ecea172c",
                    "id" : "0a085122-e81f-6f1d-bf48-3f09ecea172c",
                    "image_url" : "https://dev.azure.com/AntonYeromin/_apis/GraphProfile/MemberAvatars/aad.MGEwODUxMjItZTgxZi03ZjFkLWJmNDgtM2YwOWVjZWExNzJj",
                    "unique_name" : "Andrei_Maskouchanka@epam.com"
                  },
                  "start_date" : "2025-04-18T13:24:57.037Z",
                  "state" : "Active",
                  "test_outcome_settings" : {
                    "sync_outcome_across_suites" : false
                  },
                  "revision" : 1,
                  "_links" : { },
                  "id" : 24,
                  "project" : {
                    "id" : "9d40cdc1-5404-4d40-8025-e5267d69dc89",
                    "last_update_time" : "0001-01-01T00:00:00.000Z",
                    "name" : "CodemieAnton",
                    "state" : "unchanged",
                    "visibility" : "unchanged"
                  },
                  "root_suite" : {
                    "id" : 25,
                    "name" : "This is the first test plan"
                  },
                  "updated_by" : {
                    "_links" : { },
                    "descriptor" : "aad.MGEwODUxMjItZTgxZi03ZjFkLWJmNDgtM2YwOWVjZWExNzJj",
                    "display_name" : "Andrei Maskouchanka",
                    "url" : "https://spsprodneu1.vssps.visualstudio.com/Add1f60ac-c7d4-4a5f-b497-bdb733dc5847/_apis/Identities/0a085122-e81f-6f1d-bf48-3f09ecea172c",
                    "id" : "0a085122-e81f-6f1d-bf48-3f09ecea172c",
                    "image_url" : "https://dev.azure.com/AntonYeromin/_apis/GraphProfile/MemberAvatars/aad.MGEwODUxMjItZTgxZi03ZjFkLWJmNDgtM2YwOWVjZWExNzJj",
                    "unique_name" : "Andrei_Maskouchanka@epam.com"
                  },
                  "updated_date" : "2025-04-18T13:24:57.107Z"
            }
        """,
    ),
    (
        Toolkit.AZURE_DEVOPS_TEST_PLAN,
        AzureDevOpsTestPlanTool.GET_TEST_CASE,
        {"plan_id": 24, "suite_id": 25, "test_case_id": "26"},
        """
            {
              "links" : { },
              "point_assignments" : [ {
                "configuration_id" : 1,
                "configuration_name" : "Windows 10",
                "id" : 1,
                "tester" : {
                  "_links" : { },
                  "descriptor" : "aad.MGEwODUxMjItZTgxZi03ZjFkLWJmNDgtM2YwOWVjZWExNzJj",
                  "display_name" : "Andrei Maskouchanka",
                  "url" : "https://spsprodneu1.vssps.visualstudio.com/Add1f60ac-c7d4-4a5f-b497-bdb733dc5847/_apis/Identities/0a085122-e81f-6f1d-bf48-3f09ecea172c",
                  "id" : "0a085122-e81f-6f1d-bf48-3f09ecea172c",
                  "image_url" : "https://dev.azure.com/AntonYeromin/_apis/GraphProfile/MemberAvatars/aad.MGEwODUxMjItZTgxZi03ZjFkLWJmNDgtM2YwOWVjZWExNzJj",
                  "unique_name" : "Andrei_Maskouchanka@epam.com"
                }
              } ],
              "project" : {
                "id" : "9d40cdc1-5404-4d40-8025-e5267d69dc89",
                "last_update_time" : "0001-01-01T00:00:00.000Z",
                "name" : "CodemieAnton",
                "state" : "unchanged",
                "visibility" : "unchanged"
              },
              "test_plan" : {
                "id" : 24,
                "name" : "This is the first test plan"
              },
              "test_suite" : {
                "id" : 25,
                "name" : "<root>"
              },
              "work_item" : {
                "id" : 26,
                "name" : "The First Test Case",
                "work_item_fields" : [ {
                  "Microsoft.VSTS.TCM.Steps" : "<steps id=\"0\" last=\"2\"><step id=\"2\" type=\"ValidateStep\"><parameterizedString isformatted=\"true\">&lt;DIV&gt;&lt;P&gt;Open CodeMie main pade&lt;/P&gt;&lt;/DIV&gt;</parameterizedString><parameterizedString isformatted=\"true\">&lt;P&gt;The main page is opened.&lt;/P&gt;</parameterizedString><description/></step></steps>"
                }, {
                  "Microsoft.VSTS.Common.ActivatedBy" : "Andrei Maskouchanka <Andrei_Maskouchanka@epam.com>"
                }, {
                  "Microsoft.VSTS.Common.ActivatedDate" : "2025-04-18T13:28:08.777Z"
                }, {
                  "Microsoft.VSTS.TCM.AutomationStatus" : "Not Automated"
                }, {
                  "System.Description" : "<div>This is the first test case </div>"
                }, {
                  "System.State" : "Design"
                }, {
                  "System.AssignedTo" : "Andrei Maskouchanka <Andrei_Maskouchanka@epam.com>"
                }, {
                  "Microsoft.VSTS.Common.Priority" : 2
                }, {
                  "Microsoft.VSTS.Common.StateChangeDate" : "2025-04-18T13:28:08.777Z"
                }, {
                  "System.WorkItemType" : "Test Case"
                }, {
                  "System.Rev" : 1
                } ]
              }
            }
        """,
    ),
    (
        Toolkit.AZURE_DEVOPS_TEST_PLAN,
        AzureDevOpsTestPlanTool.GET_TEST_CASES,
        {"plan_id": 24, "suite_id": 25},
        """
            [ {
              "links" : { },
              "point_assignments" : [ {
                "configuration_id" : 1,
                "configuration_name" : "Windows 10",
                "id" : 1,
                "tester" : {
                  "_links" : { },
                  "descriptor" : "aad.MGEwODUxMjItZTgxZi03ZjFkLWJmNDgtM2YwOWVjZWExNzJj",
                  "display_name" : "Andrei Maskouchanka",
                  "url" : "https://spsprodneu1.vssps.visualstudio.com/Add1f60ac-c7d4-4a5f-b497-bdb733dc5847/_apis/Identities/0a085122-e81f-6f1d-bf48-3f09ecea172c",
                  "id" : "0a085122-e81f-6f1d-bf48-3f09ecea172c",
                  "image_url" : "https://dev.azure.com/AntonYeromin/_apis/GraphProfile/MemberAvatars/aad.MGEwODUxMjItZTgxZi03ZjFkLWJmNDgtM2YwOWVjZWExNzJj",
                  "unique_name" : "Andrei_Maskouchanka@epam.com"
                }
              } ],
              "project" : {
                "id" : "9d40cdc1-5404-4d40-8025-e5267d69dc89",
                "last_update_time" : "0001-01-01T00:00:00.000Z",
                "name" : "CodemieAnton",
                "state" : "unchanged",
                "visibility" : "unchanged"
              },
              "test_plan" : {
                "id" : 24,
                "name" : "This is the first test plan"
              },
              "test_suite" : {
                "id" : 25,
                "name" : "This is the first test plan"
              },
              "work_item" : {
                "id" : 26,
                "name" : "The First Test Case",
                "work_item_fields" : [ {
                  "Microsoft.VSTS.TCM.Steps" : "<steps id=\"0\" last=\"2\"><step id=\"2\" type=\"ValidateStep\"><parameterizedString isformatted=\"true\">&lt;DIV&gt;&lt;P&gt;Open CodeMie main pade&lt;/P&gt;&lt;/DIV&gt;</parameterizedString><parameterizedString isformatted=\"true\">&lt;P&gt;The main page is opened.&lt;/P&gt;</parameterizedString><description/></step></steps>"
                }, {
                  "Microsoft.VSTS.Common.ActivatedBy" : "Andrei Maskouchanka <Andrei_Maskouchanka@epam.com>"
                }, {
                  "Microsoft.VSTS.Common.ActivatedDate" : "2025-04-18T13:28:08.777Z"
                }, {
                  "Microsoft.VSTS.TCM.AutomationStatus" : "Not Automated"
                }, {
                  "System.Description" : "<div>This is the first test case </div>"
                }, {
                  "System.State" : "Design"
                }, {
                  "System.AssignedTo" : "Andrei Maskouchanka <Andrei_Maskouchanka@epam.com>"
                }, {
                  "Microsoft.VSTS.Common.Priority" : 2
                }, {
                  "Microsoft.VSTS.Common.StateChangeDate" : "2025-04-18T13:28:08.777Z"
                }, {
                  "System.WorkItemType" : "Test Case"
                }, {
                  "System.Rev" : 1
                } ]
              }
            }, {
              "links" : { },
              "order" : 1,
              "point_assignments" : [ {
                "configuration_id" : 1,
                "configuration_name" : "Windows 10",
                "id" : 2,
                "tester" : {
                  "_links" : { },
                  "descriptor" : "aad.MGEwODUxMjItZTgxZi03ZjFkLWJmNDgtM2YwOWVjZWExNzJj",
                  "display_name" : "Andrei Maskouchanka",
                  "url" : "https://spsprodneu1.vssps.visualstudio.com/Add1f60ac-c7d4-4a5f-b497-bdb733dc5847/_apis/Identities/0a085122-e81f-6f1d-bf48-3f09ecea172c",
                  "id" : "0a085122-e81f-6f1d-bf48-3f09ecea172c",
                  "image_url" : "https://dev.azure.com/AntonYeromin/_apis/GraphProfile/MemberAvatars/aad.MGEwODUxMjItZTgxZi03ZjFkLWJmNDgtM2YwOWVjZWExNzJj",
                  "unique_name" : "Andrei_Maskouchanka@epam.com"
                }
              } ],
              "project" : {
                "id" : "9d40cdc1-5404-4d40-8025-e5267d69dc89",
                "last_update_time" : "0001-01-01T00:00:00.000Z",
                "name" : "CodemieAnton",
                "state" : "unchanged",
                "visibility" : "unchanged"
              },
              "test_plan" : {
                "id" : 24,
                "name" : "This is the first test plan"
              },
              "test_suite" : {
                "id" : 25,
                "name" : "This is the first test plan"
              },
              "work_item" : {
                "id" : 33,
                "name" : "The Second Test Case",
                "work_item_fields" : [ {
                  "Microsoft.VSTS.TCM.Steps" : "<steps id=\"0\" last=\"2\"><step id=\"2\" type=\"ValidateStep\"><parameterizedString isformatted=\"true\">&lt;DIV&gt;&lt;P&gt;Open Integrations tab&lt;/P&gt;&lt;/DIV&gt;</parameterizedString><parameterizedString isformatted=\"true\">&lt;P&gt;The integrations tab is opened&lt;/P&gt;</parameterizedString><description/></step></steps>"
                }, {
                  "Microsoft.VSTS.Common.ActivatedBy" : "Andrei Maskouchanka <Andrei_Maskouchanka@epam.com>"
                }, {
                  "Microsoft.VSTS.Common.ActivatedDate" : "2025-04-21T07:38:57.157Z"
                }, {
                  "Microsoft.VSTS.TCM.AutomationStatus" : "Not Automated"
                }, {
                  "System.Description" : "<div>This is the second test case. </div>"
                }, {
                  "System.State" : "Design"
                }, {
                  "System.AssignedTo" : "Andrei Maskouchanka <Andrei_Maskouchanka@epam.com>"
                }, {
                  "Microsoft.VSTS.Common.Priority" : 2
                }, {
                  "Microsoft.VSTS.Common.StateChangeDate" : "2025-04-21T07:38:57.157Z"
                }, {
                  "System.WorkItemType" : "Test Case"
                }, {
                  "System.Rev" : 1
                } ]
              }
            } ]
        """,
    ),
    (
        Toolkit.AZURE_DEVOPS_TEST_PLAN,
        AzureDevOpsTestPlanTool.GET_TEST_SUITE,
        {"plan_id": 24},
        """
            [ {
              "default_configurations" : [ {
                "id" : 1,
                "name" : "Windows 10"
              } ],
              "inherit_default_configurations" : false,
              "name" : "This is the first test plan",
              "suite_type" : "staticTestSuite",
              "_links" : { },
              "id" : 25,
              "last_updated_date" : "2025-04-21T11:53:52.490Z",
              "plan" : {
                "id" : 24,
                "name" : "This is the first test plan"
              },
              "project" : {
                "id" : "9d40cdc1-5404-4d40-8025-e5267d69dc89",
                "last_update_time" : "0001-01-01T00:00:00.000Z",
                "name" : "CodemieAnton",
                "state" : "unchanged",
                "url" : "https://dev.azure.com/AntonYeromin/_apis/projects/CodemieAnton",
                "visibility" : "unchanged"
              },
              "revision" : 21
            } ]
        """,
    ),
]
