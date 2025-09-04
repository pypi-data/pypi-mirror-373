from codemie_test_harness.tests.enums.tools import PluginTool
from codemie_test_harness.tests.utils.constants import TESTS_PATH

list_files_plugin_tools_test_data = [
    (
        f"list files in the {TESTS_PATH} directory",
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
        PluginTool.LIST_FILES_IN_DIRECTORY,
    ),
    (
        "execute 'ls' command",
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
        PluginTool.RUN_COMMAND_LINE_TOOL,
    ),
    (
        "execute command: echo 'Test Message'. In the end return output of the command.",
        "Test Message",
        PluginTool.RUN_COMMAND_LINE_TOOL,
    ),
]

CREATE_READ_DELETE_FILE_TEST_DATA = {
    "create_file_prompt": "create a new {}.properties file with content {}=preview",
    "create_file_response": "I have successfully created the {}.properties file with the content {}=preview.",
    "git_command_prompt": "execute command: git add {}.properties and return if file was added to the staging area.",
    "git_command_response": "The file `{}.properties` has been added to the staging area.",
    "show_file_content_prompt": f"show the content of {TESTS_PATH}/{{}}.properties file",
    "show_file_content_response": "{}=preview",
    "remove_file_prompt": "execute command: git rm -f {}.properties",
    "remove_file_response": "The file `{}.properties` has been removed from the git repository.",
}
