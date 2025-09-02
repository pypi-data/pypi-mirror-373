from enum import Enum


class Toolkit(str, Enum):
    """Enum for toolkits."""

    GIT = "Git"
    VCS = "VCS"
    CODEBASE_TOOLS = "Codebase Tools"
    CLOUD = "Cloud"
    PLUGIN = "Plugin"
    RESEARCH = "Research"
    AZURE_DEVOPS_TEST_PLAN = "Azure DevOps Test Plan"
    AZURE_DEVOPS_WORK_ITEM = "Azure DevOps Work Item"
    AZURE_DEVOPS_WIKI = "Azure DevOps Wiki"
    NOTIFICATION = "Notification"
    PROJECT_MANAGEMENT = "Project Management"
    FILE_MANAGEMENT = "FileSystem"
    OPEN_API = "OpenAPI"
    DATA_MANAGEMENT = "Data Management"
    SERVICENOW = "IT Service Management"


class GitTool(str, Enum):
    """Enum for Git tool names."""

    LIST_BRANCHES_IN_REPO = "list_branches_in_repo"
    CREATE_BRANCH = "create_branch"
    SET_ACTIVE_BRANCH = "set_active_branch"
    CREATE_FILE = "create_file"
    UPDATE_FILE = "update_file"
    UPDATE_FILE_DIFF = "update_file_diff"
    DELETE_FILE = "delete_file"
    CREATE_PULL_REQUEST = "create_pull_request"
    GET_PR_CHANGES = "get_pr_changes"
    CREATE_PR_CHANGES_COMMENT = "create_pr_changes_comment"


class CodeBaseTool(str, Enum):
    """Enum for CodeBase tool names."""

    SONAR = "Sonar"
    SONAR_CLOUD = "Sonar Cloud"
    GET_REPOSITORY_FILE_TREE_V2 = "get_repository_file_tree_v2"
    SEARCH_CODE_REPO_V2 = "search_code_repo_v2"
    READ_FILES_CONTENT = "read_files_content"
    READ_FILES_CONTENT_SUMMARY = "read_files_content_summary"
    SEARCH_CODE_REPO_BY_PATH = "search_code_repo_by_path"


class VcsTool(str, Enum):
    """Enum for VCS tool names."""

    GITLAB = "gitlab"
    GITHUB = "github"


class CloudTool(str, Enum):
    """Enum for Cloud tool names."""

    AWS = "AWS"
    GCP = "GCP"
    AZURE = "Azure"
    KUBERNETES = "Kubernetes"


class PluginTool(str, Enum):
    """Enum for Plugin tool names."""

    # development plugin tools
    LIST_FILES_IN_DIRECTORY = "_list_files_in_directory"
    RUN_COMMAND_LINE_TOOL = "_run_command_line_tool"
    WRITE_FILE_TO_FILE_SYSTEM = "_write_file_to_file_system"
    READ_FILE_FROM_FILE_SYSTEM = "_read_file_from_file_system"
    GENERIC_GIT_TOOL = "_generic_git_tool"

    # cli mcp serv er tools
    RUN_COMMAND = "_run_command"
    SHOW_SECURITY_RULES = "_show_security_rules"

    # filesystem mcp
    LIST_DIRECTORY = "_list_directory"
    WRITE_FILE = "_write_file"
    READ_FILE = "_read_file"


class AzureDevOpsWikiTool(str, Enum):
    """Enum for Azure DevOps Wiki tool names."""

    GET_WIKI = "get_wiki"
    GET_WIKI_PAGE_BY_PATH = "get_wiki_page_by_path"
    GET_WIKI_PAGE_BY_ID = "get_wiki_page_by_id"
    DELETE_WIKI_PAGE_BY_PATH = "delete_page_by_path"
    DELETE_WIKI_PAGE_BY_ID = "delete_page_by_id"
    MODIFY_WIKI_PAGE = "modify_wiki_page"
    RENAME_WIKI_PAGE = "rename_wiki_page"


class AzureDevOpsTestPlanTool(str, Enum):
    """Enum for Azure DevOps Test Plan tool names."""

    CREATE_TEST_PLAN = "create_test_plan"
    DELETE_TEST_PLAN = "delete_test_plan"
    GET_TEST_PLAN = "get_test_plan"
    CREATE_TEST_SUITE = "create_test_suite"
    DELETE_TEST_SUITE = "delete_test_suite"
    GET_TEST_SUITE = "get_test_suite"
    ADD_TEST_CASE = "add_test_case"
    GET_TEST_CASE = "get_test_case"
    GET_TEST_CASES = "get_test_cases"


class AzureDevOpsWorkItemTool(str, Enum):
    """Enum for Azure DevOps Work Item tool names."""

    GET_WORK_ITEM = "get_work_item"
    GET_COMMENTS = "get_comments"
    GET_RELATION_TYPES = "get_relation_types"
    SEARCH_WORK_ITEMS = "search_work_items"
    CREATE_WORK_ITEM = "create_work_item"
    UPDATE_WORK_ITEM = "update_work_item"
    LINK_WORK_ITEMS = "link_work_items"


class ResearchToolName(str, Enum):
    """Enum for Research tool names."""

    GOOGLE_SEARCH = "google_search_tool_json"
    GOOGLE_PLACES = "google_places"
    GOOGLE_PLACES_FIND_NEAR = "google_places_find_near"
    WIKIPEDIA = "wikipedia"
    TAVILY_SEARCH = "tavily_search_results_json"
    WEB_SCRAPPER = "web_scrapper"


class NotificationTool(str, Enum):
    """Enum for Notification tool names."""

    EMAIL = "Email"
    TELEGRAM = "Telegram"


class ProjectManagementTool(str, Enum):
    """Enum for Project Management tool names."""

    JIRA = "generic_jira_tool"
    CONFLUENCE = "generic_confluence_tool"


class FileManagementTool(str, Enum):
    """Enum for File Management tool names."""

    READ_FILE = "read_file_from_file_system"
    WRITE_FILE = "write_file_to_file_system"
    LIST_DIRECTORY = "list_directory_from_file_system"
    RUN_COMMAND_LINE = "run_command_line_tool"
    PYTHON_CODE_INTERPRETER = "python_repl_code_interpreter"
    GENERATE_IMAGE = "generate_image_tool"
    DIFF_UPDATE = "diff_update_file_tool"
    FILESYSTEM_EDITOR = "str_replace_editor"


class OpenApiTool(str, Enum):
    """Enum for Open API tool names."""

    INVOKE_EXTERNAL_API = "open_api"
    GET_OPEN_API_SPEC = "open_api_spec"


class DataManagementTool(str, Enum):
    """Enum for Data Management tool names."""

    ELASTIC = "elastic"
    SQL = "sql"


class ServiceNowTool(str, Enum):
    """Enum for ServiceNow tool names."""

    SERVICE_NOW = "servicenow_table_tool"
