import os

import pytest

from codemie_test_harness.tests.enums.tools import FileManagementTool

CODE_INTERPRETER_TOOL_TASK = """
execute:

print("test_message" + "123")
"""

RESPONSE_FOR_CODE_INTERPRETER = """
    test_message123  
"""

LIST_DIR_TOOL_TASK = "list files in the current directory"

RESPONSE_FOR_LIST_DIR = """
      Here are the files and directories in the current directory:

    - `opt`
    - `var`
    - `dev`
    - `proc`
    - `boot`
    - `usr`
    - `bin`
    - `media`
    - `mnt`
    - `sbin`
    - `home`
    - `sys`
    - `srv`
    - `lib`
    - `root`
    - `etc`
    - `lib64`
    - `tmp`
    - `run`
    - `app`
    - `secrets`
    - `venv`
    - `codemie-ui`

Let me know if you need further details or assistance with any specific directory or file.
"""

WRITE_FILE_TASK = (
    "Under /tmp directory create a new env.properties file with content env=preview"
)

RESPONSE_FOR_WRITE_FILE_TASK = """
   The file env.properties with the content env=preview has been successfully recreated in the /tmp directory.
   If you need any further assistance, feel free to let me know!
"""

COMMAND_LINE_TOOL_TASK = "Execute command: ls /usr"

RESPONSE_FOR_COMMAND_LINE_TASK = """
    The `/usr` directory contains the following subdirectories:

    - `bin`
    - `games`
    - `include`
    - `lib`
    - `lib64`
    - `libexec`
    - `local`
    - `sbin`
    - `share`
    - `src`

    If you need further details about any of these directories or any other assistance, feel free to let me know!
"""

READ_FILE_TOOL_TASK = "Show the content of /tmp/env.properties file"

RESPONSE_FOR_READ_FILE_TASK = """
    The content of the file `/tmp/env.properties` is:

    ```
    env=preview
    ```
"""

GENERATE_IMAGE_TOOL_TASK = """
    Generate an image with mountain view. Something similar to Alps. After image is generated send image url to user
"""

file_management_tools_test_data = [
    (
        FileManagementTool.PYTHON_CODE_INTERPRETER,
        CODE_INTERPRETER_TOOL_TASK,
        RESPONSE_FOR_CODE_INTERPRETER,
    ),
    pytest.param(
        FileManagementTool.LIST_DIRECTORY,
        LIST_DIR_TOOL_TASK,
        RESPONSE_FOR_LIST_DIR,
        marks=pytest.mark.skipif(
            os.getenv("ENV") == "local",
            reason="Skipping this test on local environment",
        ),
    ),
    (
        FileManagementTool.WRITE_FILE,
        WRITE_FILE_TASK,
        RESPONSE_FOR_WRITE_FILE_TASK,
    ),
    (
        FileManagementTool.RUN_COMMAND_LINE,
        COMMAND_LINE_TOOL_TASK,
        RESPONSE_FOR_COMMAND_LINE_TASK,
    ),
]


def create_file_task(file_name: str) -> str:
    return f"Create a new file {file_name} under /tmp and add a method in python to sum two numbers"


def insert_to_file_task(file_name: str) -> str:
    return f"Insert comment 'Calculate the sum' before return statement to the file /tmp/{file_name}"


def show_diff_task(file_name: str) -> str:
    return f"Show the diff in /tmp/{file_name} file"


def show_file_task(file_name: str) -> str:
    return f"Show the content of the file /tmp/{file_name}"


RESPONSE_FOR_DIFF_UPDATE = """
    Here's the diff for the file:

    +    # Calculate the sum

"""

RESPONSE_FOR_FILE_EDITOR = """
    Here is the updated content of the file with the inserted comment:

    ```python
    1    def sum_two_numbers(x, y):
    2        # Calculate the sum of x and y
    3        return x + y
    ```

    If you need any further modifications or have other requests, please let me know!
"""

file_editing_tools_test_data = [
    (
        (FileManagementTool.WRITE_FILE, FileManagementTool.DIFF_UPDATE),
        RESPONSE_FOR_DIFF_UPDATE,
    ),
    (
        FileManagementTool.FILESYSTEM_EDITOR,
        RESPONSE_FOR_FILE_EDITOR,
    ),
]
