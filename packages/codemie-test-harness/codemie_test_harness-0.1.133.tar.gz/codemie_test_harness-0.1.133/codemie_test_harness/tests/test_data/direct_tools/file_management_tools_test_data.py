import os

import pytest

from codemie_test_harness.tests.enums.tools import FileManagementTool

file_management_tools_test_data = [
    (
        FileManagementTool.PYTHON_CODE_INTERPRETER,
        {"python_script": 'print("test_message" + "123")'},
        """
            {"type":"text","content":"test_message123\n"}
        """,
    ),
    pytest.param(
        FileManagementTool.LIST_DIRECTORY,
        {"dir_path": "."},
        """
        etc
        tmp
        opt
        srv
        sys
        proc
        sbin
        root
        media
        run
        lib
        boot
        lib64
        var
        mnt
        home
        bin
        dev
        usr
        app
        venv
        secrets
        codemie-ui 
        """,
        marks=pytest.mark.skipif(
            os.getenv("ENV") == "local",
            reason="Skipping this test on local environment",
        ),
    ),
    (
        FileManagementTool.WRITE_FILE,
        {"file_path": "/tmp/env.properties", "text": "env=preview"},
        "File written successfully to /tmp/env.properties",
    ),
    (
        FileManagementTool.RUN_COMMAND_LINE,
        {"command": "ls /usr"},
        """
         ('bin
         games
         include
         lib
         lib64
         libexec
         local
         sbin
         share
         src
         ', '', 0, 1753875309836) """,
    ),
]
