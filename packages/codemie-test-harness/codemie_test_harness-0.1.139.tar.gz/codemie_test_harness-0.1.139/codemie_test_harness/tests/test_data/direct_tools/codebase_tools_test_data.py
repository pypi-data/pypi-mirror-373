from codemie_test_harness.tests.enums.tools import Toolkit, CodeBaseTool

sonar_tools_test_data = [
    (
        Toolkit.CODEBASE_TOOLS,
        CodeBaseTool.SONAR,
        {
            "relative_url": "/api/issues/search",
            "params": '{"types":"CODE_SMELL","ps":"1"}',
        },
        """
            {
              "total" : 81,
              "p" : 1,
              "ps" : 1,
              "paging" : {
                "pageIndex" : 1,
                "pageSize" : 1,
                "total" : 81
              },
              "effortTotal" : 487,
              "issues" : [ {
                "key" : "62422172-099f-4395-bcdd-afbbbab6fb51",
                "rule" : "python:S6353",
                "severity" : "MINOR",
                "component" : "codemie:src/codemie/service/tools/dynamic_value_utils.py",
                "project" : "codemie",
                "line" : 48,
                "hash" : "c5800fd84edcdca903a5a9105f31e263",
                "textRange" : {
                  "startLine" : 48,
                  "endLine" : 48,
                  "startOffset" : 33,
                  "endOffset" : 45
                },
                "flows" : [ ],
                "resolution" : "FALSE-POSITIVE",
                "status" : "RESOLVED",
                "message" : "Use concise character class syntax '\\w' instead of '[a-zA-Z0-9_]'.",
                "effort" : "5min",
                "debt" : "5min",
                "author" : "",
                "tags" : [ "regex" ],
                "creationDate" : "2025-09-01T09:01:30+0000",
                "updateDate" : "2025-09-01T09:01:30+0000",
                "type" : "CODE_SMELL",
                "scope" : "MAIN",
                "quickFixAvailable" : false,
                "messageFormattings" : [ ],
                "codeVariants" : [ ],
                "cleanCodeAttribute" : "CLEAR",
                "cleanCodeAttributeCategory" : "INTENTIONAL",
                "impacts" : [ {
                  "softwareQuality" : "MAINTAINABILITY",
                  "severity" : "LOW"
                } ],
                "issueStatus" : "FALSE_POSITIVE",
                "prioritizedRule" : false
              } ],
              "components" : [ {
                "key" : "codemie:src/codemie/service/tools/dynamic_value_utils.py",
                "enabled" : true,
                "qualifier" : "FIL",
                "name" : "dynamic_value_utils.py",
                "longName" : "src/codemie/service/tools/dynamic_value_utils.py",
                "path" : "src/codemie/service/tools/dynamic_value_utils.py"
              }, {
                "key" : "codemie",
                "enabled" : true,
                "qualifier" : "TRK",
                "name" : "codemie",
                "longName" : "codemie"
              } ],
              "facets" : [ ]
            }
        """,
    ),
    (
        Toolkit.CODEBASE_TOOLS,
        CodeBaseTool.SONAR_CLOUD,
        {
            "relative_url": "/api/issues/search",
            "params": '{"types":"CODE_SMELL","ps":"1"}',
        },
        """
            {
              "total" : 15,
              "p" : 1,
              "ps" : 1,
              "paging" : {
                "pageIndex" : 1,
                "pageSize" : 1,
                "total" : 15
              },
              "effortTotal" : 127,
              "debtTotal" : 127,
              "issues" : [ {
                "key" : "AZTWg867SN_Wuz1X4Py2",
                "rule" : "kubernetes:S6892",
                "severity" : "MAJOR",
                "component" : "alezander86_python38g:deploy-templates/templates/deployment.yaml",
                "project" : "alezander86_python38g",
                "line" : 34,
                "hash" : "723c0daa435bdafaa7aa13d3ae06ca5e",
                "textRange" : {
                  "startLine" : 34,
                  "endLine" : 34,
                  "startOffset" : 19,
                  "endOffset" : 30
                },
                "flows" : [ ],
                "status" : "OPEN",
                "message" : "Specify a CPU request for this container.",
                "effort" : "5min",
                "debt" : "5min",
                "author" : "codebase@edp.local",
                "tags" : [ ],
                "creationDate" : "2024-11-07T13:14:43+0000",
                "updateDate" : "2025-02-05T14:28:27+0000",
                "type" : "CODE_SMELL",
                "organization" : "alezander86",
                "cleanCodeAttribute" : "COMPLETE",
                "cleanCodeAttributeCategory" : "INTENTIONAL",
                "impacts" : [ {
                  "softwareQuality" : "MAINTAINABILITY",
                  "severity" : "MEDIUM"
                }, {
                  "softwareQuality" : "RELIABILITY",
                  "severity" : "MEDIUM"
                } ],
                "issueStatus" : "OPEN",
                "projectName" : "python38g"
              } ],
              "components" : [ {
                "organization" : "alezander86",
                "key" : "alezander86_python38g:deploy-templates/templates/deployment.yaml",
                "uuid" : "AZTWg8uJSN_Wuz1X4Pye",
                "enabled" : true,
                "qualifier" : "FIL",
                "name" : "deployment.yaml",
                "longName" : "deploy-templates/templates/deployment.yaml",
                "path" : "deploy-templates/templates/deployment.yaml"
              }, {
                "organization" : "alezander86",
                "key" : "alezander86_python38g",
                "uuid" : "AZTWgJZiF0LopzvlIH8p",
                "enabled" : true,
                "qualifier" : "TRK",
                "name" : "python38g",
                "longName" : "python38g"
              } ],
              "organizations" : [ {
                "key" : "alezander86",
                "name" : "Taruraiev Oleksandr"
              } ],
              "facets" : [ ]
            }
        """,
    ),
]
