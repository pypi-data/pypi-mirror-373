from codemie_test_harness.tests.enums.tools import ProjectManagementTool
from codemie_test_harness.tests.test_data.pm_tools_test_data import (
    JIRA_TOOL_PROMPT,
    RESPONSE_FOR_JIRA_TOOL,
    CONFLUENCE_TOOL_PROMPT,
    RESPONSE_FOR_CONFLUENCE_TOOL,
    JIRA_CLOUD_TOOL_PROMPT,
    RESPONSE_FOR_JIRA_CLOUD_TOOL,
    CONFLUENCE_CLOUD_TOOL_PROMPT,
    RESPONSE_FOR_CONFLUENCE_CLOUD_TOOL,
)
from codemie_test_harness.tests.utils.constants import ProjectManagementIntegrationType

pm_tools_test_data = [
    (
        ProjectManagementTool.JIRA,
        ProjectManagementIntegrationType.JIRA,
        JIRA_TOOL_PROMPT,
        RESPONSE_FOR_JIRA_TOOL,
    ),
    (
        ProjectManagementTool.CONFLUENCE,
        ProjectManagementIntegrationType.CONFLUENCE,
        CONFLUENCE_TOOL_PROMPT,
        RESPONSE_FOR_CONFLUENCE_TOOL,
    ),
    (
        ProjectManagementTool.JIRA,
        ProjectManagementIntegrationType.JIRA_CLOUD,
        JIRA_CLOUD_TOOL_PROMPT,
        RESPONSE_FOR_JIRA_CLOUD_TOOL,
    ),
    (
        ProjectManagementTool.CONFLUENCE,
        ProjectManagementIntegrationType.CONFLUENCE_CLOUD,
        CONFLUENCE_CLOUD_TOOL_PROMPT,
        RESPONSE_FOR_CONFLUENCE_CLOUD_TOOL,
    ),
]
