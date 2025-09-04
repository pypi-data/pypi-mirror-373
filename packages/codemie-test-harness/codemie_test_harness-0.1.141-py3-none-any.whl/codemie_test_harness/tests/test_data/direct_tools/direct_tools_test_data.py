from codemie_test_harness.tests.enums.tools import PluginTool
from codemie_test_harness.tests.utils.constants import TESTS_PATH

cli_tools_test_data = [
    (
        PluginTool.SHOW_SECURITY_RULES,
        {},
        f"""
            Security Configuration:
            ==================
            Working Directory: {TESTS_PATH}
            
            Allowed Commands:
            ----------------
            All commands allowed
            
            Allowed Flags:
            -------------
            All flags allowed
            
            Security Limits:
            ---------------
            Max Command Length: 2048 characters
            Command Timeout: 300 seconds
        """,
    ),
    (
        PluginTool.RUN_COMMAND,
        {"command": "ls"},
        """
           '__init__.py
            __pycache__
            assistant
            conftest.py
            direct_test_git.properties
            direct_test_read.properties
            e2e
            enums
            integrations
            llm
            search
            service
            test_data
            ui
            utils
            workflow
            
            
            Command completed with return code: 0'
        """,
    ),
]

dev_plugin_tools_test_data = [
    (
        PluginTool.LIST_FILES_IN_DIRECTORY,
        {"dir_path": str(TESTS_PATH)},
        """
           content='assistant\nui\nconftest.py\nllm\ndirect_test_read.properties\ntest_data\nenums\n__init__.py\n
           utils\n__pycache__\ndirect_test_git.properties\nsearch\nintegrations\nworkflow\nservice\ne2e' 
           name='_list_files_in_directory' tool_call_id='54a3a776-302f-491c-9c5a-ff39401f618d'
        """,
    ),
    (
        PluginTool.RUN_COMMAND_LINE_TOOL,
        {"command": "ls"},
        """
           content='assistant\nui\nconftest.py\nllm\ndirect_test_read.properties\ntest_data\nenums\n__init__.py\n
           utils\n__pycache__\ndirect_test_git.properties\nsearch\nintegrations\nworkflow\nservice\ne2e' 
           name='_list_files_in_directory' tool_call_id='54a3a776-302f-491c-9c5a-ff39401f618d'
        """,
    ),
    (
        PluginTool.RUN_COMMAND_LINE_TOOL,
        {"command": "echo 'Test Message'"},
        "content='Test Message\\n' name='_run_command_line_tool' tool_call_id='02aca1ac-461f-46ee-9e8b-9294bfac6306'",
    ),
    (
        PluginTool.WRITE_FILE_TO_FILE_SYSTEM,
        {"file_path": "direct_test_create.properties", "text": "environment=preview"},
        """
            content='File written successfully to direct_test_create.properties'
            name='_write_file_to_file_system' tool_call_id='c8706489-06c6-493e-ad39-896557149227'
        """,
    ),
    (
        PluginTool.READ_FILE_FROM_FILE_SYSTEM,
        {"file_path": str(TESTS_PATH / "direct_test_read.properties")},
        """
            content='environment=preview' name='_read_file_from_file_system'
            tool_call_id='d6575f60-3843-49bb-94cb-d89b18030749'
        """,
    ),
    (
        PluginTool.GENERIC_GIT_TOOL,
        {"git_command": "add direct_test_git.properties"},
        f"content='{TESTS_PATH}' name='_generic_git_tool' tool_call_id='6924dfa2-2330-4a53-b59a-a65520e533fd'",
    ),
]
