import json

import pytest

from codemie_sdk.models.integration import (
    CredentialTypes,
    IntegrationType,
)
from hamcrest import equal_to, assert_that

from codemie_test_harness.tests import PROJECT
from codemie_test_harness.tests.integrations import integrations
from codemie_test_harness.tests.enums.tools import AzureDevOpsWikiTool
from codemie_test_harness.tests.test_data.direct_tools.ado_wiki_tools_test_data import (
    ado_wiki_get_test_data,
)
from codemie_test_harness.tests.utils.aws_parameters_store import CredentialsUtil
from codemie_test_harness.tests.utils.base_utils import get_random_name
from codemie_test_harness.tests.utils.constants import test_project_name

ado_wiki_prompt = ado_wiki_get_test_data[0][2]
ado_wiki_answer = ado_wiki_get_test_data[0][3]


@pytest.mark.not_for_parallel_run
@pytest.mark.regression
@pytest.mark.tescase("EPMCDME-6708")
@pytest.mark.parametrize(
    "user_integration, is_global, project_integration",
    integrations,
    ids=[
        f"{row[0].value}-{'global' if row[1] else 'None'}-{row[2].value if row[2] else 'None'}"
        for row in integrations
    ],
)
def test_tool_in_workflow_should_use_user_integration_by_default(
    integration_utils,
    similarity_check,
    user_integration,
    is_global,
    project_integration,
    workflow_with_tool,
    workflow_utils,
):
    """
    Test to verify that an assistant should use USER integration by default
    if integration of all types [USER, GLOBAL, PROJECT] are available.
    """

    for integration_type in IntegrationType:
        integration_utils.delete_integrations_by_type(
            integration_type, CredentialTypes.AZURE_DEVOPS
        )

    integration_utils.create_user_integration(
        CredentialTypes.AZURE_DEVOPS,
        CredentialsUtil.azure_devops_credentials(),
        test_project_name,
    )

    if is_global:
        integration_utils.create_global_integration(
            CredentialTypes.AZURE_DEVOPS,
            CredentialsUtil.invalid_ado_credentials(),
            test_project_name,
        )

    if project_integration:
        integration_utils.create_project_integration(
            CredentialTypes.AZURE_DEVOPS,
            CredentialsUtil.invalid_ado_credentials(),
            test_project_name,
        )

    assistant_and_state_name = get_random_name()

    test_workflow = workflow_with_tool(
        assistant_and_state_name,
        AzureDevOpsWikiTool.GET_WIKI_PAGE_BY_ID,
        project_name=test_project_name,
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id,
        assistant_and_state_name,
        user_input=json.dumps(ado_wiki_prompt),
    )
    assert_that(response, equal_to(ado_wiki_answer))


@pytest.mark.not_for_parallel_run
@pytest.mark.regression
@pytest.mark.tescase("EPMCDME-6708")
def test_tool_in_workflow_with_global_and_project_integration(
    integration_utils,
    similarity_check,
    workflow_with_tool,
    workflow_utils,
):
    """
    Test to verify that an assistant should use GLOBAL integration if USER integration is not available,
    and both GLOBAL and PROJECT integrations exist.
    GLOBAL integration has valid credentials, PROJECT has invalid.
    """
    for integration_type in IntegrationType:
        integration_utils.delete_integrations_by_type(
            integration_type, CredentialTypes.AZURE_DEVOPS
        )

    # Create only global (valid) and project (invalid) integrations.
    # Global integration is created in project which is different from the project of the assistant.
    integration_utils.create_global_integration(
        CredentialTypes.AZURE_DEVOPS,
        CredentialsUtil.azure_devops_credentials(),
        PROJECT,
    )
    integration_utils.create_project_integration(
        CredentialTypes.AZURE_DEVOPS,
        CredentialsUtil.invalid_ado_credentials(),
        test_project_name,
    )

    assistant_and_state_name = get_random_name()

    test_workflow = workflow_with_tool(
        assistant_and_state_name,
        AzureDevOpsWikiTool.GET_WIKI_PAGE_BY_ID,
        project_name=test_project_name,
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id,
        assistant_and_state_name,
        user_input=json.dumps(ado_wiki_prompt),
    )
    assert_that(response, equal_to(ado_wiki_answer))


@pytest.mark.not_for_parallel_run
@pytest.mark.regression
@pytest.mark.tescase("EPMCDME-6708")
def test_tool_in_workflow_with_project_integration_only(
    integration_utils,
    similarity_check,
    workflow_with_tool,
    workflow_utils,
):
    """
    Test to verify that an assistant should use PROJECT integration if it is the only one available.
    """
    for integration_type in IntegrationType:
        integration_utils.delete_integrations_by_type(
            integration_type, CredentialTypes.AZURE_DEVOPS
        )

    # Create project integration only
    integration_utils.create_project_integration(
        CredentialTypes.AZURE_DEVOPS,
        CredentialsUtil.azure_devops_credentials(),
        test_project_name,
    )

    assistant_and_state_name = get_random_name()

    test_workflow = workflow_with_tool(
        assistant_and_state_name,
        AzureDevOpsWikiTool.GET_WIKI_PAGE_BY_ID,
        project_name=test_project_name,
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id,
        assistant_and_state_name,
        user_input=json.dumps(ado_wiki_prompt),
    )
    assert_that(response, equal_to(ado_wiki_answer))


@pytest.mark.not_for_parallel_run
@pytest.mark.regression
def test_tool_in_workflow_with_global_valid_and_user_invalid_integration(
    integration_utils,
    similarity_check,
    workflow_with_tool,
    workflow_utils,
):
    """
    Test to verify that an assistant should use GLOBAL integration if USER integration is not valid,
    and both GLOBAL and USER integrations exist.
    GLOBAL integration has valid credentials, USER has invalid.
    """
    for integration_type in IntegrationType:
        integration_utils.delete_integrations_by_type(
            integration_type, CredentialTypes.AZURE_DEVOPS
        )

    # Create global valid integration.
    integration_utils.create_global_integration(
        CredentialTypes.AZURE_DEVOPS,
        CredentialsUtil.azure_devops_credentials(),
        PROJECT,
    )

    # Create user invalid integration.
    integration_utils.create_user_integration(
        CredentialTypes.AZURE_DEVOPS,
        CredentialsUtil.invalid_ado_credentials(),
        PROJECT,
    )

    assistant_and_state_name = get_random_name()

    test_workflow = workflow_with_tool(
        assistant_and_state_name,
        AzureDevOpsWikiTool.GET_WIKI_PAGE_BY_ID,
        project_name=test_project_name,
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id,
        assistant_and_state_name,
        user_input=json.dumps(ado_wiki_prompt),
    )
    assert_that(response, equal_to(ado_wiki_answer))


@pytest.mark.not_for_parallel_run
@pytest.mark.regression
def test_tool_in_workflow_with_project_valid_and_user_invalid_integration(
    integration_utils,
    similarity_check,
    workflow_with_tool,
    workflow_utils,
):
    """
    Test to verify that an assistant should use PROJECT integration if USER integration is not valid,
    and both PROJECT and USER integrations exist.
    PROJECT integration has valid credentials, USER has invalid.
    """
    for integration_type in IntegrationType:
        integration_utils.delete_integrations_by_type(
            integration_type, CredentialTypes.AZURE_DEVOPS
        )

    # Create project valid integration.
    integration_utils.create_project_integration(
        CredentialTypes.AZURE_DEVOPS,
        CredentialsUtil.azure_devops_credentials(),
        test_project_name,
    )

    # Create user invalid integration.
    integration_utils.create_user_integration(
        CredentialTypes.AZURE_DEVOPS,
        CredentialsUtil.invalid_ado_credentials(),
        PROJECT,
    )

    assistant_and_state_name = get_random_name()

    test_workflow = workflow_with_tool(
        assistant_and_state_name,
        AzureDevOpsWikiTool.GET_WIKI_PAGE_BY_ID,
        project_name=test_project_name,
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id,
        assistant_and_state_name,
        user_input=json.dumps(ado_wiki_prompt),
    )
    assert_that(response, equal_to(ado_wiki_answer))
