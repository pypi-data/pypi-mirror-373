from enum import Enum
from pathlib import Path

from codemie_test_harness.tests.enums.tools import VcsTool, NotificationTool


class ProjectManagementIntegrationType(Enum):
    JIRA = "jira"
    CONFLUENCE = "confluence"
    JIRA_CLOUD = "jira_cloud"
    CONFLUENCE_CLOUD = "confluence_cloud"


TESTS_PATH = Path(__file__).parent.parent

FILES_PATH = TESTS_PATH / "test_data" / "files"

ID_PATTERN = r'\{\s*"?ID"?\s*:\s*"?(\d+)"?\s*\}'

WORK_ITEM_ID_PATTERN = r"workItems/(\d+)"

vcs_integrations = {
    VcsTool.GITHUB: "github_integration",
    VcsTool.GITLAB: "gitlab_integration",
}

project_management_integrations = {
    ProjectManagementIntegrationType.JIRA: "jira_integration",
    ProjectManagementIntegrationType.CONFLUENCE: "confluence_integration",
    ProjectManagementIntegrationType.JIRA_CLOUD: "jira_cloud_integration",
    ProjectManagementIntegrationType.CONFLUENCE_CLOUD: "confluence_cloud_integration",
}

notification_integrations = {
    NotificationTool.EMAIL: "email_integration",
    NotificationTool.TELEGRAM: "telegram_integration",
}

test_project_name = "automation-tests-project"
