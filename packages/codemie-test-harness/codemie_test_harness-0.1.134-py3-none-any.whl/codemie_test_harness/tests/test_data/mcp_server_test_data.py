from codemie_sdk.models.assistant import MCPServerDetails, MCPServerConfig
from codemie_test_harness.tests.enums.tools import PluginTool

from codemie_test_harness.tests.utils.constants import TESTS_PATH

cli_mcp_server_test_data = [
    (
        "ls",
        """
            Here is the list of directories and files in the current directory:
    
            bin
            games
            include
            lib
            lib64
            libexec
            local
            sbin
            share
            src
        """,
    ),
    (
        "ls /tmp",
        """
            It seems that the command `ls /tmp` cannot be executed because it is outside the allowed directory (`/usr`).
            Only commands within the `/usr` directory are permitted.
        """,
    ),
    (
        "touch long-file-name-for-test.txt",
        """
            It appears that the command exceeds the maximum allowed length of 20 characters.
            Let's try a shorter command.
        """,
    ),
    (
        "cat file.txt",
        """
            The `cat` command is not supported in this environment. If you need to list or display
            the contents of a file, please provide an alternative command that is supported.
            You can use `ls` to list files or `echo` to display text.
        """,
    ),
    (
        "ls -a",
        """
            The `-a` flag is not allowed in this environment. Here are the allowed commands and flags:
    
            - Commands: `ls`, `echo`
            - Flags: `-l`, `--help`
    
            Would you like to run a different command?
        """,
    ),
]

CLI_MCP_SERVER = MCPServerDetails(
    name="CLI MCP server",
    description="CLI MCP server",
    enabled=True,
    config=MCPServerConfig(
        command="uvx",
        args=["cli-mcp-server"],
        env={
            "ALLOWED_DIR": "/usr",
            "ALLOWED_COMMANDS": "ls,echo,touch",
            "ALLOWED_FLAGS": "-l,--help",
            "MAX_COMMAND_LENGTH": "20",
        },
    ),
)

TIME_MCP_SERVER_WITH_CONFIG = MCPServerDetails(
    name="Time MCP server",
    description="Time MCP server",
    enabled=True,
    config=MCPServerConfig(command="uvx", args=["mcp-server-time"]),
)

TIME_MCP_SERVER_WITHOUT_CONFIG = MCPServerDetails(
    name="Time MCP server",
    description="Time MCP server",
    command="uvx",
    arguments="mcp-server-time",
    enabled=True,
)

time_mcp_server_test_data = [
    TIME_MCP_SERVER_WITH_CONFIG,
    TIME_MCP_SERVER_WITHOUT_CONFIG,
]

FETCH_MCP_SERVER = MCPServerDetails(
    name="Fetch MCP server",
    description="Fetch MCP server",
    enabled=True,
    config=MCPServerConfig(command="uvx", args=["mcp-server-fetch"]),
)

fetch_server_prompt = "Fetch https://rubular.com/"

fetch_expected_response = """
    Rubular is a Ruby regular expression editor. It provides a quick reference guide for regex syntax:

    ### Regex Quick Reference
    
    #### Character Classes
    - `[abc]`: A single character of: a, b, or c
    - `[^abc]`: Any single character except: a, b, or c
    - `[a-z]`: Any single character in the range a-z
    - `[a-zA-Z]`: Any single character in the range a-z or A-Z
    
    #### Anchors
    - `^`: Start of line
    - `$`: End of line
    - `\A`: Start of string
    - `\z`: End of string
    
    #### Special Characters
    - `.`: Any single character
    - `\s`: Any whitespace character
    - `\S`: Any non-whitespace character
    - `\d`: Any digit
    - `\D`: Any non-digit
    - `\w`: Any word character (letter, number, underscore)
    - `\W`: Any non-word character
    - `\b`: Any word boundary
    
    #### Grouping and Quantifiers
    - `(...)`: Capture everything enclosed
    - `(a|b)`: a or b
    - `a?`: Zero or one of a
    - `a*`: Zero or more of a
    - `a+`: One or more of a
    - `a{3}`: Exactly 3 of a
    - `a{3,}`: 3 or more of a
    - `a{3,6}`: Between 3 and 6 of a
    
    #### Options
    - `i`: Case insensitive
    - `m`: Make dot match newlines
    - `x`: Ignore whitespace in regex
    - `o`: Perform `#{...}` substitutions only once
    
    This editor can be helpful for testing and experimenting with Ruby regular expressions.
"""

time_server_prompt = (
    'Convert time 23:11 from "Asia/Tokyo" timezone to "America/New_York" timezone'
)

time_expected_response = """
    The time 23:11 (11:11 PM) in the "Asia/Tokyo" timezone converts to 10:11 (10:11 AM) on the same day
     in the "America/New_York" timezone.
"""

cli_mcp_server_with_plugin_test_data = [
    (
        "ls",
        """
            The files and directories in the current directory are as follows:

            - `assistant`
            - `conftest.py`
            - `llm`
            - `similarity_check.py`
            - `test_workflow_service.py`
            - `test_assistant_service.py`
            - `test_data`
            - `enums`
            - `test_user_service.py`
            - `__init__.py`
            - `utils`
            - `__pycache__`
            - `test_task_service.py`
            - `test_integration_service.py`
            - `.env`
            - `workflow`
            - `test_workflow_execution_service.py`
            - `test_datasource_service.py`
            - `test_llm_service.py`
            - `test_e2e.py`
            
            Let me know if you need any further assistance!
        """,
    ),
    (
        "Run ls /tmp. In case of any error do not try to execute the command in other directory or with additional parameters.",
        f"""
            It seems that the command `ls /tmp` cannot be executed because it is outside the allowed directory (`{TESTS_PATH}`).
            Only commands within the `{TESTS_PATH}` directory are permitted.
        """,
    ),
]

filesystem_mcp_server_with_plugin_test_data = [
    (
        f"ls {TESTS_PATH}",
        """
            The files and directories in the current directory are as follows:

            - `assistant`
            - `conftest.py`
            - `llm`
            - `similarity_check.py`
            - `test_workflow_service.py`
            - `test_assistant_service.py`
            - `test_data`
            - `enums`
            - `test_user_service.py`
            - `__init__.py`
            - `ui`
            - `utils`
            - `__pycache__`
            - `test_task_service.py`
            - `test_integration_service.py`
            - `.env`
            - `.env.local`
            - `.env.preview`
            - `.env.prod`
            - `workflow`
            - `test_workflow_execution_service.py`
            - `test_datasource_service.py`
            - `test_llm_service.py`
            - `test_e2e.py`

            Let me know if you need any further assistance!
        """,
        PluginTool.LIST_DIRECTORY,
    ),
    (
        "ls /tmp",
        f"""
            It seems that the command `ls /tmp` cannot be executed because it is outside the allowed directory (`{TESTS_PATH}`).
            Only commands within the `{TESTS_PATH}` directory are permitted.
        """,
        PluginTool.LIST_DIRECTORY,
    ),
    (
        f"Create a new {TESTS_PATH}/sdk_tests.properties file with content sdk_tests=preview",
        f"I have successfully created the {TESTS_PATH}/sdk_tests.properties file with the content sdk_tests=preview.",
        PluginTool.WRITE_FILE,
    ),
    (
        f"Show the content of the {TESTS_PATH}/enums/integrations.py file",
        """
            from enum import Enum


            class DataBaseDialect(str, Enum):
            \"""Enum for DB Dialect names.\"""

            MY_SQL = "mysql"
            POSTGRES = "postgres"
        """,
        PluginTool.READ_FILE,
    ),
]
