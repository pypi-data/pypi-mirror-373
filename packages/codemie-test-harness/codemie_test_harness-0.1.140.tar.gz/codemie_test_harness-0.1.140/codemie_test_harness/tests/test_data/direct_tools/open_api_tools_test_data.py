import os

from codemie_test_harness.tests.enums.tools import Toolkit, OpenApiTool

# OpenAPI tools test data for direct tools calling
open_api_tools_test_data = [
    (
        Toolkit.OPEN_API,
        OpenApiTool.INVOKE_EXTERNAL_API,
        {
            "method": "GET",
            "url": f"{os.getenv('CODEMIE_API_DOMAIN')}/v1/info",
        },
        """
            "{"message":"Codemie","version":"2.0.0-SNAPSHOT.10","description":"Smart AI assistant 'CodeMie'"}"
        """,
    ),
]
