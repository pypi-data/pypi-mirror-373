import os

import pytest

from codemie_test_harness.tests.test_data.mcp_server_test_data import (
    time_mcp_server_test_data,
    time_expected_response,
    FETCH_MCP_SERVER,
    fetch_expected_response,
    time_server_prompt,
    fetch_server_prompt,
)


@pytest.mark.parametrize(
    "mcp_server",
    time_mcp_server_test_data,
    ids=[
        f"With config: {data.config is not None}" for data in time_mcp_server_test_data
    ],
)
@pytest.mark.regression
@pytest.mark.mcp
@pytest.mark.skipif(
    os.getenv("ENV") == "local", reason="Skipping this test on local environment"
)
def test_creation_mcp_server_with_form_configuration(
    assistant_utils, assistant, similarity_check, mcp_server
):
    assistant = assistant(mcp_server=mcp_server)

    response = assistant_utils.ask_assistant(
        assistant,
        time_server_prompt,
    )

    similarity_check.check_similarity(response, time_expected_response)


@pytest.mark.regression
@pytest.mark.mcp
@pytest.mark.skipif(
    os.getenv("ENV") == "local", reason="Skipping this test on local environment"
)
def test_fetch_mcp_server(assistant_utils, assistant, similarity_check):
    assistant = assistant(mcp_server=FETCH_MCP_SERVER)

    response = assistant_utils.ask_assistant(assistant, fetch_server_prompt)

    similarity_check.check_similarity(response, fetch_expected_response)
