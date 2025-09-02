import os
import pytest
from codemie_sdk.models.assistant import (
    Context,
    ContextType,
    ToolDetails,
    ToolKitDetails,
)
from codemie_test_harness.tests.enums.tools import (
    Toolkit,
    GitTool,
    VcsTool,
)
from codemie_sdk.models.integration import CredentialTypes
from codemie_test_harness.tests.utils.aws_parameters_store import CredentialsUtil


@pytest.fixture(scope="session")
def git_integration(integration_utils):
    if os.getenv("GIT_ENV", "gitlab") == "gitlab":
        integration = integration_utils.create_integration(
            credential_type=CredentialTypes.GIT,
            credential_values=CredentialsUtil.gitlab_credentials(),
        )
    else:
        integration = integration_utils.create_integration(
            credential_type=CredentialTypes.GIT,
            credential_values=CredentialsUtil.github_credentials(),
        )
    yield integration
    if integration:
        integration_utils.delete_integration(integration)


@pytest.mark.regression
@pytest.mark.code_kb
def test_assistant_with_code_kb(
    assistant_utils, code_datasource, default_llm, similarity_check
):
    assistant = assistant_utils.create_assistant(
        llm_model_type=default_llm.base_name,
        context=[Context(name=code_datasource.name, context_type=ContextType.CODE)],
    )

    response = assistant_utils.ask_assistant(
        assistant,
        "List files in root and confirm that you have an access to the code knowledge base. "
        "Do not return the files to user, just confirm if you have an access or not",
    )

    similarity_check.check_similarity(
        response, "I confirm that I have access to the code knowledge base."
    )


@pytest.mark.skipif(
    os.getenv("GIT_ENV") == "github",
    reason="Test is skipped when GIT_ENV is set to github",
)
@pytest.mark.regression
@pytest.mark.gitlab
def test_assistant_with_vcs_gitlab_tool(
    assistant_utils, gitlab_integration, default_llm, similarity_check
):
    assistant = assistant_utils.create_assistant(
        llm_model_type=default_llm.base_name,
        toolkits=[
            ToolKitDetails(
                toolkit=Toolkit.VCS,
                tools=[ToolDetails(name=VcsTool.GITLAB, settings=gitlab_integration)],
            )
        ],
    )

    response = assistant_utils.ask_assistant(
        assistant,
        f"Run gitlab tool to list branches in the repository for project with ID {os.getenv('GITLAB_PROJECT_ID')}. "
        "Do not ask user confirmation to do this. "
        "Do not return branches to user but just confirm if you have an access to repository or not",
    )

    similarity_check.check_similarity(
        response, "I have confirmed that I have access to the repository."
    )


@pytest.mark.skipif(
    os.getenv("GIT_ENV") == "gitlab",
    reason="Test is skipped when GIT_ENV is set to gitlab",
)
@pytest.mark.regression
@pytest.mark.github
def test_assistant_with_vcs_github_tool(
    assistant_utils, github_integration, default_llm, similarity_check
):
    assistant = assistant_utils.create_assistant(
        llm_model_type=default_llm.base_name,
        toolkits=[
            ToolKitDetails(
                toolkit=Toolkit.VCS,
                tools=[ToolDetails(name=VcsTool.GITHUB, settings=github_integration)],
            )
        ],
    )

    response = assistant_utils.ask_assistant(
        assistant,
        f"Run github tool to list branches in the repository for project {os.getenv('GITHUB_PROJECT')}. "
        "Do not ask user confirmation to do this. "
        "Do not return branches to user but just confirm if you have an access to repository or not",
    )

    similarity_check.check_similarity(
        response, "I have confirmed that I have access to the repository."
    )


@pytest.mark.regression
@pytest.mark.git
def test_assistant_with_list_branches_tool(
    assistant_utils, code_datasource, default_llm, similarity_check
):
    assistant = assistant_utils.create_assistant(
        llm_model_type=default_llm.base_name,
        system_prompt="Do not pass any parameters to tool",
        toolkits=[
            ToolKitDetails(
                toolkit=Toolkit.GIT,
                tools=[ToolDetails(name=GitTool.LIST_BRANCHES_IN_REPO)],
            )
        ],
        context=[Context(name=code_datasource.name, context_type=ContextType.CODE)],
    )

    response = assistant_utils.ask_assistant(
        assistant,
        "List branches in the repository. Run tool without any arguments: {}"
        "No need to pass query at all like {'query': ''}"
        "Do not return branches to user but just confirm if you have an access to repository or not",
    )

    similarity_check.check_similarity(
        response, "I have access to the repository and can list its branches. "
    )


@pytest.mark.regression
@pytest.mark.jira_kb
def test_assistant_with_jira_kb(
    assistant_utils, jira_datasource, default_llm, similarity_check
):
    assistant = assistant_utils.create_assistant(
        llm_model_type=default_llm.base_name,
        context=[
            Context(name=jira_datasource.name, context_type=ContextType.KNOWLEDGE_BASE)
        ],
    )

    response = assistant_utils.ask_assistant(
        assistant,
        "Find any jira ticket. "
        "Do not return it to user but just confirm if you have an access to jira knowledge base or not",
    )

    similarity_check.check_similarity(
        response, "I have access to Jira knowledge base. and can find tickets."
    )


@pytest.mark.regression
@pytest.mark.confluence_kb
def test_assistant_with_confluence_kb(
    assistant_utils, confluence_datasource, default_llm, similarity_check
):
    assistant = assistant_utils.create_assistant(
        llm_model_type=default_llm.base_name,
        context=[
            Context(
                name=confluence_datasource.name, context_type=ContextType.KNOWLEDGE_BASE
            )
        ],
    )

    response = assistant_utils.ask_assistant(
        assistant,
        "Find any confluence page "
        "Do not return it to user but just confirm if you have an access to confluence knowledge base or not",
    )

    similarity_check.check_similarity(
        response, "I have access to the Confluence knowledge base."
    )
