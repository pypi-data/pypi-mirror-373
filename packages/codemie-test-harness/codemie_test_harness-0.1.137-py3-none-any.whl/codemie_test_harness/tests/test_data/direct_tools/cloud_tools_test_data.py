import os

import pytest

from codemie_test_harness.tests.enums.tools import Toolkit, CloudTool
from codemie_sdk.models.integration import CredentialTypes
from codemie_test_harness.tests.utils.aws_parameters_store import CredentialsUtil

cloud_test_data = [
    (
        Toolkit.CLOUD,
        CloudTool.AWS,
        CredentialTypes.AWS,
        CredentialsUtil.aws_credentials(),
        {
            "query": {
                "service": "s3",
                "method_name": "list_buckets",
                "method_arguments": {},
            }
        },
        """
            {
               "ResponseMetadata":{
                  "RequestId":"7F5A7MRRFPY9RPTC",
                  "HostId":"YDtbO8lMQau9e0tDDDDC0GGnZnqQb1RxW9bRHQcV3P6v/FhWgLyVS63l79oBVOchAzQ9AXZeY1kCmeUWsoUTYg==",
                  "HTTPStatusCode":200,
                  "HTTPHeaders":{
                     "x-amz-id-2":"YDtbO8lMQau9e0tDDDDC0GGnZnqQb1RxW9bRHQcV3P6v/FhWgLyVS63l79oBVOchAzQ9AXZeY1kCmeUWsoUTYg==",
                     "x-amz-request-id":"7F5A7MRRFPY9RPTC",
                     "date":"Wed, 25 Jun 2025 15:39:54 GMT",
                     "content-type":"application/xml",
                     "transfer-encoding":"chunked",
                     "server":"AmazonS3"
                  },
                  "RetryAttempts":0
               },
               "Buckets":[
                  {
                     "Name":"az-v3-codemie-terraform-states-025066278959",
                     "CreationDate": datetime.datetime(2025, 6, 20, 13, 31, 10, tzinfo=tzlocal())
                  },
                  {
                     "Name":"codemie-bucket",
                     "CreationDate": datetime.datetime(2025, 1, 29, 17, 30, 57, tzinfo=tzlocal())
                  },
                  {
                     "Name":"codemie-it-terraform-states-025066278959",
                     "CreationDate": datetime.datetime(2025, 6, 16, 21, 30, 46, tzinfo=tzlocal())
                  },
                  {
                     "Name":"codemie-it-user-data-025066278959",
                     "CreationDate": datetime.datetime(2025, 6, 16, 21, 30, 48, tzinfo=tzlocal())
                  },
                  {
                     "Name":"codemie-terraform-states-025066278959",
                     "CreationDate": datetime.datetime(2025, 6, 13, 13, 30, 50, tzinfo=tzlocal())
                  },
                  {
                     "Name":"codemie-terraform-states-yevhen-l-025066278959",
                     "CreationDate": datetime.datetime(2025, 6, 17, 9, 30, 58, tzinfo=tzlocal())
                  },
                  {
                     "Name":"codemie-user-data-025066278959",
                     "CreationDate": datetime.datetime(2025, 6, 16, 13, 31, 5, tzinfo=tzlocal())
                  },
                  {
                     "Name":"codemie-yl-user-data-025066278959",
                     "CreationDate": datetime.datetime(2025, 6, 17, 11, 31, 1, tzinfo=tzlocal())
                  },
                  {
                     "Name":"epam-cloud-s3-access-logs-025066278959-eu-central-1",
                     "CreationDate": datetime.datetime(2024, 11, 9, 19, 51, 46, tzinfo=tzlocal())
                  },
                  {
                     "Name":"epam-cloud-s3-access-logs-025066278959-eu-north-1",
                     "CreationDate": datetime.datetime(2025, 5, 17, 15, 31, 2, tzinfo=tzlocal())
                  },
                  {
                     "Name":"epam-cloud-s3-access-logs-025066278959-eu-west-2",
                     "CreationDate": datetime.datetime(2025, 5, 21, 15, 30, 57, tzinfo=tzlocal())

                  },
                  {
                     "Name":"epam-cloud-s3-access-logs-025066278959-us-east-1",
                     "CreationDate": datetime.datetime(2024, 11, 27, 15, 31, tzinfo=tzlocal())
                  },
                  {
                     "Name":"sk-codemie-terraform-states-025066278959",
                     "CreationDate": datetime.datetime(2025, 6, 4, 15, 30, 48, tzinfo=tzlocal())
                  },
                  {
                     "Name":"terraform-states-025066278959",
                     "CreationDate": datetime.datetime(2024, 11, 13, 22, 30, 57, tzinfo=tzlocal())
                  }
               ],
               "Owner":{
                  "ID":"978dcce1304506a42ed130c2cfdd87fe9c0652869232df15b4b5589a6481d4e5"
               }
            }
        """,
    ),
    (
        Toolkit.CLOUD,
        CloudTool.AZURE,
        CredentialTypes.AZURE,
        CredentialsUtil.azure_credentials(),
        {
            "method": "GET",
            "url": "https://management.azure.com/subscriptions/08679d2f-8945-4e08-8df8-b8e58626b13a/resourceGroups/krci-codemie-azure-env-rg?api-version=2021-04-01",
        },
        """
            {
              "id" : "/subscriptions/08679d2f-8945-4e08-8df8-b8e58626b13a/resourceGroups/krci-codemie-azure-env-rg",
              "name" : "krci-codemie-azure-env-rg",
              "type" : "Microsoft.Resources/resourceGroups",
              "location" : "westeurope",
              "tags" : {
                "environment" : "codemie-azure"
              },
              "properties" : {
                "provisioningState" : "Succeeded"
              }
            }
        """,
    ),
    pytest.param(
        Toolkit.CLOUD,
        CloudTool.GCP,
        CredentialTypes.GCP,
        CredentialsUtil.gcp_credentials(),
        {
            "method": "GET",
            "scopes": ["https://www.googleapis.com/auth/cloud-platform"],
            "url": "https://www.googleapis.com/storage/v1/b/009fb622-4e29-42aa-bafd-584c61f5e1e1",
        },
        """
            {
               "kind":"storage#bucket",
               "selfLink":"https://www.googleapis.com/storage/v1/b/009fb622-4e29-42aa-bafd-584c61f5e1e1",
               "id":"009fb622-4e29-42aa-bafd-584c61f5e1e1",
               "name":"009fb622-4e29-42aa-bafd-584c61f5e1e1",
               "projectNumber":"415940185513",
               "generation":"1731334834610581052",
               "metageneration":"1",
               "location":"US",
               "storageClass":"STANDARD",
               "etag":"CAE=",
               "timeCreated":"2024-11-11T14:20:34.897Z",
               "updated":"2024-11-11T14:20:34.897Z",
               "softDeletePolicy":{
                  "retentionDurationSeconds":"604800",
                  "effectiveTime":"2024-11-11T14:20:34.897Z"
               },
               "iamConfiguration":{
                  "bucketPolicyOnly":{
                     "enabled":false
                  },
                  "uniformBucketLevelAccess":{
                     "enabled":false
                  },
                  "publicAccessPrevention":"inherited"
               },
               "locationType":"multi-region",
               "rpo":"DEFAULT"
            }
        """,
        marks=pytest.mark.skipif(
            os.getenv("ENV") == "azure",
            reason="Still have an issue with encoding long strings",
        ),
    ),
    (
        Toolkit.CLOUD,
        CloudTool.KUBERNETES,
        CredentialTypes.KUBERNETES,
        CredentialsUtil.kubernetes_credentials(),
        {"method": "GET", "suburl": "/api/v1/namespaces/argocd/services"},
        """
            {
              "kind" : "ServiceList",
              "apiVersion" : "v1",
              "metadata" : {
                "resourceVersion" : "1940273724"
              },
              "items" : [ {
                "metadata" : {
                  "name" : "argo-cd-argocd-applicationset-controller",
                  "namespace" : "argocd",
                  "uid" : "db4e6042-41df-4b0d-88b6-7c69f2b5e109",
                  "resourceVersion" : "1915134165",
                  "creationTimestamp" : "2024-01-08T17:15:41Z",
                  "labels" : {
                    "app.kubernetes.io/component" : "applicationset-controller",
                    "app.kubernetes.io/instance" : "argo-cd",
                    "app.kubernetes.io/managed-by" : "Helm",
                    "app.kubernetes.io/name" : "argocd-applicationset-controller",
                    "app.kubernetes.io/part-of" : "argocd",
                    "app.kubernetes.io/version" : "v3.0.12",
                    "argocd.argoproj.io/instance-edp" : "eks-sandbox-argo-cd",
                    "helm.sh/chart" : "argo-cd-8.2.5"
                  },
                  "managedFields" : [ {
                    "manager" : "argocd-controller",
                    "operation" : "Apply",
                    "apiVersion" : "v1",
                    "time" : "2025-08-01T14:44:31Z",
                    "fieldsType" : "FieldsV1",
                    "fieldsV1" : {
                      "f:metadata" : {
                        "f:labels" : {
                          "f:app.kubernetes.io/component" : { },
                          "f:app.kubernetes.io/instance" : { },
                          "f:app.kubernetes.io/managed-by" : { },
                          "f:app.kubernetes.io/name" : { },
                          "f:app.kubernetes.io/part-of" : { },
                          "f:app.kubernetes.io/version" : { },
                          "f:argocd.argoproj.io/instance-edp" : { },
                          "f:helm.sh/chart" : { }
                        }
                      },
                      "f:spec" : {
                        "f:ports" : {
                          "k:{\"port\":7000,\"protocol\":\"TCP\"}" : {
                            "." : { },
                            "f:name" : { },
                            "f:port" : { },
                            "f:targetPort" : { }
                          }
                        },
                        "f:selector" : { },
                        "f:type" : { }
                      }
                    }
                  } ]
                },
                "spec" : {
                  "ports" : [ {
                    "name" : "http-webhook",
                    "protocol" : "TCP",
                    "port" : 7000,
                    "targetPort" : "webhook"
                  } ],
                  "selector" : {
                    "app.kubernetes.io/instance" : "argo-cd",
                    "app.kubernetes.io/name" : "argocd-applicationset-controller"
                  },
                  "clusterIP" : "10.100.216.226",
                  "clusterIPs" : [ "10.100.216.226" ],
                  "type" : "ClusterIP",
                  "sessionAffinity" : "None",
                  "ipFamilies" : [ "IPv4" ],
                  "ipFamilyPolicy" : "SingleStack",
                  "internalTrafficPolicy" : "Cluster"
                },
                "status" : {
                  "loadBalancer" : { }
                }
              }, {
                "metadata" : {
                  "name" : "argo-cd-argocd-repo-server",
                  "namespace" : "argocd",
                  "uid" : "9d0ab30b-04d7-4589-9fc6-35d99823dd90",
                  "resourceVersion" : "1915134170",
                  "creationTimestamp" : "2023-11-15T15:19:44Z",
                  "labels" : {
                    "app.kubernetes.io/component" : "repo-server",
                    "app.kubernetes.io/instance" : "argo-cd",
                    "app.kubernetes.io/managed-by" : "Helm",
                    "app.kubernetes.io/name" : "argocd-repo-server",
                    "app.kubernetes.io/part-of" : "argocd",
                    "app.kubernetes.io/version" : "v3.0.12",
                    "argocd.argoproj.io/instance-edp" : "eks-sandbox-argo-cd",
                    "helm.sh/chart" : "argo-cd-8.2.5"
                  },
                  "managedFields" : [ {
                    "manager" : "argocd-controller",
                    "operation" : "Apply",
                    "apiVersion" : "v1",
                    "time" : "2025-08-01T14:44:31Z",
                    "fieldsType" : "FieldsV1",
                    "fieldsV1" : {
                      "f:metadata" : {
                        "f:labels" : {
                          "f:app.kubernetes.io/component" : { },
                          "f:app.kubernetes.io/instance" : { },
                          "f:app.kubernetes.io/managed-by" : { },
                          "f:app.kubernetes.io/name" : { },
                          "f:app.kubernetes.io/part-of" : { },
                          "f:app.kubernetes.io/version" : { },
                          "f:argocd.argoproj.io/instance-edp" : { },
                          "f:helm.sh/chart" : { }
                        }
                      },
                      "f:spec" : {
                        "f:ports" : {
                          "k:{\"port\":8081,\"protocol\":\"TCP\"}" : {
                            "." : { },
                            "f:name" : { },
                            "f:port" : { },
                            "f:protocol" : { },
                            "f:targetPort" : { }
                          }
                        },
                        "f:selector" : { }
                      }
                    }
                  } ]
                },
                "spec" : {
                  "ports" : [ {
                    "name" : "tcp-repo-server",
                    "protocol" : "TCP",
                    "port" : 8081,
                    "targetPort" : "repo-server"
                  } ],
                  "selector" : {
                    "app.kubernetes.io/instance" : "argo-cd",
                    "app.kubernetes.io/name" : "argocd-repo-server"
                  },
                  "clusterIP" : "10.100.240.197",
                  "clusterIPs" : [ "10.100.240.197" ],
                  "type" : "ClusterIP",
                  "sessionAffinity" : "None",
                  "ipFamilies" : [ "IPv4" ],
                  "ipFamilyPolicy" : "SingleStack",
                  "internalTrafficPolicy" : "Cluster"
                },
                "status" : {
                  "loadBalancer" : { }
                }
              }, {
                "metadata" : {
                  "name" : "argo-cd-argocd-server",
                  "namespace" : "argocd",
                  "uid" : "9d36eaa8-fb31-4073-a36c-3207ed696514",
                  "resourceVersion" : "1915134167",
                  "creationTimestamp" : "2023-11-15T15:19:44Z",
                  "labels" : {
                    "app.kubernetes.io/component" : "server",
                    "app.kubernetes.io/instance" : "argo-cd",
                    "app.kubernetes.io/managed-by" : "Helm",
                    "app.kubernetes.io/name" : "argocd-server",
                    "app.kubernetes.io/part-of" : "argocd",
                    "app.kubernetes.io/version" : "v3.0.12",
                    "argocd.argoproj.io/instance-edp" : "eks-sandbox-argo-cd",
                    "helm.sh/chart" : "argo-cd-8.2.5"
                  },
                  "managedFields" : [ {
                    "manager" : "argocd-controller",
                    "operation" : "Apply",
                    "apiVersion" : "v1",
                    "time" : "2025-08-01T14:44:31Z",
                    "fieldsType" : "FieldsV1",
                    "fieldsV1" : {
                      "f:metadata" : {
                        "f:labels" : {
                          "f:app.kubernetes.io/component" : { },
                          "f:app.kubernetes.io/instance" : { },
                          "f:app.kubernetes.io/managed-by" : { },
                          "f:app.kubernetes.io/name" : { },
                          "f:app.kubernetes.io/part-of" : { },
                          "f:app.kubernetes.io/version" : { },
                          "f:argocd.argoproj.io/instance-edp" : { },
                          "f:helm.sh/chart" : { }
                        }
                      },
                      "f:spec" : {
                        "f:ports" : {
                          "k:{\"port\":80,\"protocol\":\"TCP\"}" : {
                            "." : { },
                            "f:name" : { },
                            "f:port" : { },
                            "f:protocol" : { },
                            "f:targetPort" : { }
                          },
                          "k:{\"port\":443,\"protocol\":\"TCP\"}" : {
                            "." : { },
                            "f:name" : { },
                            "f:port" : { },
                            "f:protocol" : { },
                            "f:targetPort" : { }
                          }
                        },
                        "f:selector" : { },
                        "f:sessionAffinity" : { },
                        "f:type" : { }
                      }
                    }
                  } ]
                },
                "spec" : {
                  "ports" : [ {
                    "name" : "http",
                    "protocol" : "TCP",
                    "port" : 80,
                    "targetPort" : 8080
                  }, {
                    "name" : "https",
                    "protocol" : "TCP",
                    "port" : 443,
                    "targetPort" : 8080
                  } ],
                  "selector" : {
                    "app.kubernetes.io/instance" : "argo-cd",
                    "app.kubernetes.io/name" : "argocd-server"
                  },
                  "clusterIP" : "10.100.240.149",
                  "clusterIPs" : [ "10.100.240.149" ],
                  "type" : "ClusterIP",
                  "sessionAffinity" : "None",
                  "ipFamilies" : [ "IPv4" ],
                  "ipFamilyPolicy" : "SingleStack",
                  "internalTrafficPolicy" : "Cluster"
                },
                "status" : {
                  "loadBalancer" : { }
                }
              }, {
                "metadata" : {
                  "name" : "argo-cd-redis-ha",
                  "namespace" : "argocd",
                  "uid" : "6bc23815-6346-4986-aae6-069aff8d17bf",
                  "resourceVersion" : "1915134169",
                  "creationTimestamp" : "2023-11-15T15:19:44Z",
                  "labels" : {
                    "app" : "redis-ha",
                    "argocd.argoproj.io/instance-edp" : "eks-sandbox-argo-cd",
                    "chart" : "redis-ha-4.33.7",
                    "heritage" : "Helm",
                    "release" : "argo-cd"
                  },
                  "managedFields" : [ {
                    "manager" : "argocd-controller",
                    "operation" : "Apply",
                    "apiVersion" : "v1",
                    "time" : "2025-08-01T14:44:31Z",
                    "fieldsType" : "FieldsV1",
                    "fieldsV1" : {
                      "f:metadata" : {
                        "f:annotations" : { },
                        "f:labels" : {
                          "f:app" : { },
                          "f:argocd.argoproj.io/instance-edp" : { },
                          "f:chart" : { },
                          "f:heritage" : { },
                          "f:release" : { }
                        }
                      },
                      "f:spec" : {
                        "f:clusterIP" : { },
                        "f:ports" : {
                          "k:{\"port\":6379,\"protocol\":\"TCP\"}" : {
                            "." : { },
                            "f:name" : { },
                            "f:port" : { },
                            "f:protocol" : { },
                            "f:targetPort" : { }
                          },
                          "k:{\"port\":26379,\"protocol\":\"TCP\"}" : {
                            "." : { },
                            "f:name" : { },
                            "f:port" : { },
                            "f:protocol" : { },
                            "f:targetPort" : { }
                          }
                        },
                        "f:selector" : { },
                        "f:type" : { }
                      }
                    }
                  } ]
                },
                "spec" : {
                  "ports" : [ {
                    "name" : "tcp-server",
                    "protocol" : "TCP",
                    "port" : 6379,
                    "targetPort" : "redis"
                  }, {
                    "name" : "tcp-sentinel",
                    "protocol" : "TCP",
                    "port" : 26379,
                    "targetPort" : "sentinel"
                  } ],
                  "selector" : {
                    "app" : "redis-ha",
                    "release" : "argo-cd"
                  },
                  "clusterIP" : "None",
                  "clusterIPs" : [ "None" ],
                  "type" : "ClusterIP",
                  "sessionAffinity" : "None",
                  "ipFamilies" : [ "IPv4" ],
                  "ipFamilyPolicy" : "SingleStack",
                  "internalTrafficPolicy" : "Cluster"
                },
                "status" : {
                  "loadBalancer" : { }
                }
              }, {
                "metadata" : {
                  "name" : "argo-cd-redis-ha-announce-0",
                  "namespace" : "argocd",
                  "uid" : "bcdb4ff4-4910-410b-b232-c7eba1d37884",
                  "resourceVersion" : "1915134163",
                  "creationTimestamp" : "2023-11-15T15:19:44Z",
                  "labels" : {
                    "app" : "redis-ha",
                    "argocd.argoproj.io/instance-edp" : "eks-sandbox-argo-cd",
                    "chart" : "redis-ha-4.33.7",
                    "heritage" : "Helm",
                    "release" : "argo-cd"
                  },
                  "managedFields" : [ {
                    "manager" : "argocd-controller",
                    "operation" : "Apply",
                    "apiVersion" : "v1",
                    "time" : "2025-08-01T14:44:31Z",
                    "fieldsType" : "FieldsV1",
                    "fieldsV1" : {
                      "f:metadata" : {
                        "f:annotations" : { },
                        "f:labels" : {
                          "f:app" : { },
                          "f:argocd.argoproj.io/instance-edp" : { },
                          "f:chart" : { },
                          "f:heritage" : { },
                          "f:release" : { }
                        }
                      },
                      "f:spec" : {
                        "f:ports" : {
                          "k:{\"port\":6379,\"protocol\":\"TCP\"}" : {
                            "." : { },
                            "f:name" : { },
                            "f:port" : { },
                            "f:protocol" : { },
                            "f:targetPort" : { }
                          },
                          "k:{\"port\":26379,\"protocol\":\"TCP\"}" : {
                            "." : { },
                            "f:name" : { },
                            "f:port" : { },
                            "f:protocol" : { },
                            "f:targetPort" : { }
                          }
                        },
                        "f:publishNotReadyAddresses" : { },
                        "f:selector" : { },
                        "f:type" : { }
                      }
                    }
                  } ]
                },
                "spec" : {
                  "ports" : [ {
                    "name" : "tcp-server",
                    "protocol" : "TCP",
                    "port" : 6379,
                    "targetPort" : "redis"
                  }, {
                    "name" : "tcp-sentinel",
                    "protocol" : "TCP",
                    "port" : 26379,
                    "targetPort" : "sentinel"
                  } ],
                  "selector" : {
                    "app" : "redis-ha",
                    "release" : "argo-cd",
                    "statefulset.kubernetes.io/pod-name" : "argo-cd-redis-ha-server-0"
                  },
                  "clusterIP" : "10.100.8.41",
                  "clusterIPs" : [ "10.100.8.41" ],
                  "type" : "ClusterIP",
                  "sessionAffinity" : "None",
                  "publishNotReadyAddresses" : true,
                  "ipFamilies" : [ "IPv4" ],
                  "ipFamilyPolicy" : "SingleStack",
                  "internalTrafficPolicy" : "Cluster"
                },
                "status" : {
                  "loadBalancer" : { }
                }
              }, {
                "metadata" : {
                  "name" : "argo-cd-redis-ha-announce-1",
                  "namespace" : "argocd",
                  "uid" : "171a3c5a-19f3-4489-adcc-d64e52e0fe56",
                  "resourceVersion" : "1915134166",
                  "creationTimestamp" : "2023-11-15T15:19:44Z",
                  "labels" : {
                    "app" : "redis-ha",
                    "argocd.argoproj.io/instance-edp" : "eks-sandbox-argo-cd",
                    "chart" : "redis-ha-4.33.7",
                    "heritage" : "Helm",
                    "release" : "argo-cd"
                  },
                  "managedFields" : [ {
                    "manager" : "argocd-controller",
                    "operation" : "Apply",
                    "apiVersion" : "v1",
                    "time" : "2025-08-01T14:44:31Z",
                    "fieldsType" : "FieldsV1",
                    "fieldsV1" : {
                      "f:metadata" : {
                        "f:annotations" : { },
                        "f:labels" : {
                          "f:app" : { },
                          "f:argocd.argoproj.io/instance-edp" : { },
                          "f:chart" : { },
                          "f:heritage" : { },
                          "f:release" : { }
                        }
                      },
                      "f:spec" : {
                        "f:ports" : {
                          "k:{\"port\":6379,\"protocol\":\"TCP\"}" : {
                            "." : { },
                            "f:name" : { },
                            "f:port" : { },
                            "f:protocol" : { },
                            "f:targetPort" : { }
                          },
                          "k:{\"port\":26379,\"protocol\":\"TCP\"}" : {
                            "." : { },
                            "f:name" : { },
                            "f:port" : { },
                            "f:protocol" : { },
                            "f:targetPort" : { }
                          }
                        },
                        "f:publishNotReadyAddresses" : { },
                        "f:selector" : { },
                        "f:type" : { }
                      }
                    }
                  } ]
                },
                "spec" : {
                  "ports" : [ {
                    "name" : "tcp-server",
                    "protocol" : "TCP",
                    "port" : 6379,
                    "targetPort" : "redis"
                  }, {
                    "name" : "tcp-sentinel",
                    "protocol" : "TCP",
                    "port" : 26379,
                    "targetPort" : "sentinel"
                  } ],
                  "selector" : {
                    "app" : "redis-ha",
                    "release" : "argo-cd",
                    "statefulset.kubernetes.io/pod-name" : "argo-cd-redis-ha-server-1"
                  },
                  "clusterIP" : "10.100.74.38",
                  "clusterIPs" : [ "10.100.74.38" ],
                  "type" : "ClusterIP",
                  "sessionAffinity" : "None",
                  "publishNotReadyAddresses" : true,
                  "ipFamilies" : [ "IPv4" ],
                  "ipFamilyPolicy" : "SingleStack",
                  "internalTrafficPolicy" : "Cluster"
                },
                "status" : {
                  "loadBalancer" : { }
                }
              }, {
                "metadata" : {
                  "name" : "argo-cd-redis-ha-announce-2",
                  "namespace" : "argocd",
                  "uid" : "e1a334b5-07f2-47b7-bd66-410684033b78",
                  "resourceVersion" : "1915134168",
                  "creationTimestamp" : "2023-11-15T15:19:44Z",
                  "labels" : {
                    "app" : "redis-ha",
                    "argocd.argoproj.io/instance-edp" : "eks-sandbox-argo-cd",
                    "chart" : "redis-ha-4.33.7",
                    "heritage" : "Helm",
                    "release" : "argo-cd"
                  },
                  "managedFields" : [ {
                    "manager" : "argocd-controller",
                    "operation" : "Apply",
                    "apiVersion" : "v1",
                    "time" : "2025-08-01T14:44:31Z",
                    "fieldsType" : "FieldsV1",
                    "fieldsV1" : {
                      "f:metadata" : {
                        "f:annotations" : { },
                        "f:labels" : {
                          "f:app" : { },
                          "f:argocd.argoproj.io/instance-edp" : { },
                          "f:chart" : { },
                          "f:heritage" : { },
                          "f:release" : { }
                        }
                      },
                      "f:spec" : {
                        "f:ports" : {
                          "k:{\"port\":6379,\"protocol\":\"TCP\"}" : {
                            "." : { },
                            "f:name" : { },
                            "f:port" : { },
                            "f:protocol" : { },
                            "f:targetPort" : { }
                          },
                          "k:{\"port\":26379,\"protocol\":\"TCP\"}" : {
                            "." : { },
                            "f:name" : { },
                            "f:port" : { },
                            "f:protocol" : { },
                            "f:targetPort" : { }
                          }
                        },
                        "f:publishNotReadyAddresses" : { },
                        "f:selector" : { },
                        "f:type" : { }
                      }
                    }
                  } ]
                },
                "spec" : {
                  "ports" : [ {
                    "name" : "tcp-server",
                    "protocol" : "TCP",
                    "port" : 6379,
                    "targetPort" : "redis"
                  }, {
                    "name" : "tcp-sentinel",
                    "protocol" : "TCP",
                    "port" : 26379,
                    "targetPort" : "sentinel"
                  } ],
                  "selector" : {
                    "app" : "redis-ha",
                    "release" : "argo-cd",
                    "statefulset.kubernetes.io/pod-name" : "argo-cd-redis-ha-server-2"
                  },
                  "clusterIP" : "10.100.150.15",
                  "clusterIPs" : [ "10.100.150.15" ],
                  "type" : "ClusterIP",
                  "sessionAffinity" : "None",
                  "publishNotReadyAddresses" : true,
                  "ipFamilies" : [ "IPv4" ],
                  "ipFamilyPolicy" : "SingleStack",
                  "internalTrafficPolicy" : "Cluster"
                },
                "status" : {
                  "loadBalancer" : { }
                }
              }, {
                "metadata" : {
                  "name" : "argo-cd-redis-ha-haproxy",
                  "namespace" : "argocd",
                  "uid" : "1f703dfa-dccd-4431-b8fa-028a32437ba9",
                  "resourceVersion" : "1915134164",
                  "creationTimestamp" : "2023-11-15T15:19:44Z",
                  "labels" : {
                    "app" : "redis-ha",
                    "argocd.argoproj.io/instance-edp" : "eks-sandbox-argo-cd",
                    "chart" : "redis-ha-4.33.7",
                    "component" : "argo-cd-redis-ha-haproxy",
                    "heritage" : "Helm",
                    "release" : "argo-cd"
                  },
                  "managedFields" : [ {
                    "manager" : "argocd-controller",
                    "operation" : "Apply",
                    "apiVersion" : "v1",
                    "time" : "2025-08-01T14:44:31Z",
                    "fieldsType" : "FieldsV1",
                    "fieldsV1" : {
                      "f:metadata" : {
                        "f:annotations" : { },
                        "f:labels" : {
                          "f:app" : { },
                          "f:argocd.argoproj.io/instance-edp" : { },
                          "f:chart" : { },
                          "f:component" : { },
                          "f:heritage" : { },
                          "f:release" : { }
                        }
                      },
                      "f:spec" : {
                        "f:ports" : {
                          "k:{\"port\":6379,\"protocol\":\"TCP\"}" : {
                            "." : { },
                            "f:name" : { },
                            "f:port" : { },
                            "f:protocol" : { },
                            "f:targetPort" : { }
                          },
                          "k:{\"port\":9101,\"protocol\":\"TCP\"}" : {
                            "." : { },
                            "f:name" : { },
                            "f:port" : { },
                            "f:protocol" : { },
                            "f:targetPort" : { }
                          }
                        },
                        "f:selector" : { },
                        "f:type" : { }
                      }
                    }
                  } ]
                },
                "spec" : {
                  "ports" : [ {
                    "name" : "tcp-haproxy",
                    "protocol" : "TCP",
                    "port" : 6379,
                    "targetPort" : "redis"
                  }, {
                    "name" : "http-exporter-port",
                    "protocol" : "TCP",
                    "port" : 9101,
                    "targetPort" : "metrics-port"
                  } ],
                  "selector" : {
                    "app" : "redis-ha-haproxy",
                    "release" : "argo-cd"
                  },
                  "clusterIP" : "10.100.224.21",
                  "clusterIPs" : [ "10.100.224.21" ],
                  "type" : "ClusterIP",
                  "sessionAffinity" : "None",
                  "ipFamilies" : [ "IPv4" ],
                  "ipFamilyPolicy" : "SingleStack",
                  "internalTrafficPolicy" : "Cluster"
                },
                "status" : {
                  "loadBalancer" : { }
                }
              } ]
            }
        """,
    ),
]
