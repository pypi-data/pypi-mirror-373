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
        """
            Run list_buckets tool to print S3 buckets. List names only.
            Query example: {'query': {'service': 's3', 'method_name': 'list_buckets', 'method_arguments': {}}}
        """,
        """
            Okay, here are the names of your S3 buckets:

            *   codemie-bucket
            *   codemie-terraform-states-025066278959
            *   epam-cloud-s3-access-logs-025066278959-eu-central-1
            *   epam-cloud-s3-access-logs-025066278959-us-east-1
            *   terraform-states-025066278959
        """,
    ),
    (
        Toolkit.CLOUD,
        CloudTool.AZURE,
        CredentialTypes.AZURE,
        CredentialsUtil.azure_credentials(),
        "List info about krci-codemie-azure-env-rg resource group. Do not get information about resources in it",
        """
            Here is the information about the resource group krci-codemie-azure-env-rg:

            ID: /subscriptions/08679d2f-8945-4e08-8df8-b8e58626b13a/resourceGroups/krci-codemie-azure-env-rg
            Name: krci-codemie-azure-env-rg
            Type: Microsoft.Resources/resourceGroups
            Location: westeurope
            Tags:
             - environment: codemie-azure
            Provisioning State: Succeeded
        """,
    ),
    pytest.param(
        Toolkit.CLOUD,
        CloudTool.GCP,
        CredentialTypes.GCP,
        CredentialsUtil.gcp_credentials(),
        """
            Get information about bucket with Name 009fb622-4e29-42aa-bafd-584c61f5e1e1

            Data is required: [
              "Kind",
              "Self Link",
              "ID",
              "Name",
              "Project Number",
              "Generation",
              "Metageneration",
              "Location",
              "Storage Class",
              "ETag",
              "Time Created",
              "Updated",
              "Location Type",
              "RPO",
              "Soft Delete Policy Retention Duration Seconds",
              "Soft Delete Policy Effective Time",
              "IAM Configuration Bucket Policy Only",
              "IAM Configuration Uniform Bucket Level Access",
              "IAM Configuration Public Access Prevention"
            ]
        """,
        """
            Here is the information about the bucket with Name `009fb622-4e29-42aa-bafd-584c61f5e1e1`:

            - **Kind**: `storage#bucket`
            - **Self Link**: [Bucket Link](https://www.googleapis.com/storage/v1/b/009fb622-4e29-42aa-bafd-584c61f5e1e1)
            - **ID**: `009fb622-4e29-42aa-bafd-584c61f5e1e1`
            - **Name**: `009fb622-4e29-42aa-bafd-584c61f5e1e1`
            - **Project Number**: `415940185513`
            - **Generation**: `1731334834610581052`
            - **Metageneration**: `1`
            - **Location**: `US`
            - **Storage Class**: `STANDARD`
            - **ETag**: `CAE=`
            - **Time Created**: `2024-11-11T14:20:34.897Z`
            - **Updated**: `2024-11-11T14:20:34.897Z`
            - **Location Type**: `multi-region`
            - **RPO**: `DEFAULT`

            **Soft Delete Policy**:
            - **Retention Duration Seconds**: `604800`
            - **Effective Time**: `2024-11-11T14:20:34.897Z`

            **IAM Configuration**:
            - **Bucket Policy Only**: `False`
            - **Uniform Bucket Level Access**: `False`
            - **Public Access Prevention**: `inherited`
        """,
        marks=pytest.mark.skipif(
            os.getenv("ENV") in ["azure", "gcp"],
            reason="Still have an issue with encoding long strings",
        ),
    ),
    (
        Toolkit.CLOUD,
        CloudTool.KUBERNETES,
        CredentialTypes.KUBERNETES,
        CredentialsUtil.kubernetes_credentials(),
        """
            List service names in the argocd namespace. Return only names, no need to return other data
        """,
        """
            Here are the service names in the `argocd` namespace:
            
            1. argo-cd-argocd-applicationset-controller
            2. argo-cd-argocd-repo-server
            3. argo-cd-argocd-server
            4. argo-cd-redis-ha
            5. argo-cd-redis-ha-announce-0
            6. argo-cd-redis-ha-announce-1
            7. argo-cd-redis-ha-announce-2
            8. argo-cd-redis-ha-haproxy
        """,
    ),
]
