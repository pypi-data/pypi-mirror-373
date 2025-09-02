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
              "effortTotal" : 525,
              "issues" : [ {
                "key" : "cbdc0649-14e5-4f4b-8fa4-f2c7c6dbafb6",
                "rule" : "python:S3776",
                "severity" : "CRITICAL",
                "component" : "codemie:src/codemie/service/assistant_service.py",
                "project" : "codemie",
                "line" : 765,
                "hash" : "579909ff6065d3fd0355264ce7a164d5",
                "textRange" : {
                  "startLine" : 765,
                  "endLine" : 765,
                  "startOffset" : 8,
                  "endOffset" : 22
                },
                "flows" : [ {
                  "locations" : [ {
                    "component" : "codemie:src/codemie/service/assistant_service.py",
                    "textRange" : {
                      "startLine" : 771,
                      "endLine" : 771,
                      "startOffset" : 8,
                      "endOffset" : 10
                    },
                    "msg" : "+1",
                    "msgFormattings" : [ ]
                  } ]
                }, {
                  "locations" : [ {
                    "component" : "codemie:src/codemie/service/assistant_service.py",
                    "textRange" : {
                      "startLine" : 773,
                      "endLine" : 773,
                      "startOffset" : 12,
                      "endOffset" : 14
                    },
                    "msg" : "+2 (incl 1 for nesting)",
                    "msgFormattings" : [ ]
                  } ]
                }, {
                  "locations" : [ {
                    "component" : "codemie:src/codemie/service/assistant_service.py",
                    "textRange" : {
                      "startLine" : 775,
                      "endLine" : 775,
                      "startOffset" : 8,
                      "endOffset" : 12
                    },
                    "msg" : "+1",
                    "msgFormattings" : [ ]
                  } ]
                }, {
                  "locations" : [ {
                    "component" : "codemie:src/codemie/service/assistant_service.py",
                    "textRange" : {
                      "startLine" : 780,
                      "endLine" : 780,
                      "startOffset" : 8,
                      "endOffset" : 11
                    },
                    "msg" : "+1",
                    "msgFormattings" : [ ]
                  } ]
                }, {
                  "locations" : [ {
                    "component" : "codemie:src/codemie/service/assistant_service.py",
                    "textRange" : {
                      "startLine" : 781,
                      "endLine" : 781,
                      "startOffset" : 12,
                      "endOffset" : 14
                    },
                    "msg" : "+2 (incl 1 for nesting)",
                    "msgFormattings" : [ ]
                  } ]
                }, {
                  "locations" : [ {
                    "component" : "codemie:src/codemie/service/assistant_service.py",
                    "textRange" : {
                      "startLine" : 785,
                      "endLine" : 785,
                      "startOffset" : 8,
                      "endOffset" : 10
                    },
                    "msg" : "+1",
                    "msgFormattings" : [ ]
                  } ]
                }, {
                  "locations" : [ {
                    "component" : "codemie:src/codemie/service/assistant_service.py",
                    "textRange" : {
                      "startLine" : 785,
                      "endLine" : 785,
                      "startOffset" : 30,
                      "endOffset" : 33
                    },
                    "msg" : "+1",
                    "msgFormattings" : [ ]
                  } ]
                }, {
                  "locations" : [ {
                    "component" : "codemie:src/codemie/service/assistant_service.py",
                    "textRange" : {
                      "startLine" : 787,
                      "endLine" : 787,
                      "startOffset" : 12,
                      "endOffset" : 15
                    },
                    "msg" : "+2 (incl 1 for nesting)",
                    "msgFormattings" : [ ]
                  } ]
                }, {
                  "locations" : [ {
                    "component" : "codemie:src/codemie/service/assistant_service.py",
                    "textRange" : {
                      "startLine" : 788,
                      "endLine" : 788,
                      "startOffset" : 16,
                      "endOffset" : 18
                    },
                    "msg" : "+3 (incl 2 for nesting)",
                    "msgFormattings" : [ ]
                  } ]
                }, {
                  "locations" : [ {
                    "component" : "codemie:src/codemie/service/assistant_service.py",
                    "textRange" : {
                      "startLine" : 792,
                      "endLine" : 792,
                      "startOffset" : 12,
                      "endOffset" : 14
                    },
                    "msg" : "+2 (incl 1 for nesting)",
                    "msgFormattings" : [ ]
                  } ]
                }, {
                  "locations" : [ {
                    "component" : "codemie:src/codemie/service/assistant_service.py",
                    "textRange" : {
                      "startLine" : 801,
                      "endLine" : 801,
                      "startOffset" : 8,
                      "endOffset" : 10
                    },
                    "msg" : "+1",
                    "msgFormattings" : [ ]
                  } ]
                } ],
                "status" : "OPEN",
                "message" : "Refactor this function to reduce its Cognitive Complexity from 17 to the 15 allowed.",
                "effort" : "7min",
                "debt" : "7min",
                "author" : "",
                "tags" : [ "brain-overload" ],
                "creationDate" : "2025-08-25T13:38:18+0000",
                "updateDate" : "2025-08-25T13:38:18+0000",
                "type" : "CODE_SMELL",
                "scope" : "MAIN",
                "quickFixAvailable" : false,
                "messageFormattings" : [ ],
                "codeVariants" : [ ],
                "cleanCodeAttribute" : "FOCUSED",
                "cleanCodeAttributeCategory" : "ADAPTABLE",
                "impacts" : [ {
                  "softwareQuality" : "MAINTAINABILITY",
                  "severity" : "HIGH"
                } ],
                "issueStatus" : "OPEN",
                "prioritizedRule" : false
              } ],
              "components" : [ {
                "key" : "codemie:src/codemie/service/assistant_service.py",
                "enabled" : true,
                "qualifier" : "FIL",
                "name" : "assistant_service.py",
                "longName" : "src/codemie/service/assistant_service.py",
                "path" : "src/codemie/service/assistant_service.py"
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
