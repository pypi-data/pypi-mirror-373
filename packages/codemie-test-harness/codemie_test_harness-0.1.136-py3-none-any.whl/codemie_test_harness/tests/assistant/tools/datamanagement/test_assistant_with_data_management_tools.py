import os
import uuid

import pytest
from codemie_sdk.models.integration import CredentialTypes

from codemie_test_harness.tests.enums.tools import (
    Toolkit,
    DataManagementTool,
)
from codemie_test_harness.tests.test_data.data_management_tools_test_data import (
    ELASTIC_TOOL_TASK,
    RESPONSE_FOR_ELASTIC,
    sql_tools_test_data,
    SQL_TOOL_CREATE_TABLE_TASK,
    SQL_TOOL_DELETE_TABLE_TASK,
    SQL_TOOL_INSERT_TABLE_TASK,
    SQL_TOOL_QUERY_TABLE_TASK,
    RESPONSE_FOR_SQL,
)
from codemie_test_harness.tests.utils.aws_parameters_store import CredentialsUtil


@pytest.mark.regression
@pytest.mark.testcase("EPMCDME-6132")
@pytest.mark.skip(reason="Credentials for Elastic are not available")
def test_create_assistant_with_elastic_tool(
    integration_utils, assistant, assistant_utils, similarity_check
):
    credential_values = CredentialsUtil.elastic_credentials()
    settings = integration_utils.create_integration(
        CredentialTypes.ELASTIC, credential_values
    )
    assistant = assistant(
        Toolkit.DATA_MANAGEMENT,
        DataManagementTool.ELASTIC,
        settings=settings,
    )

    response = assistant_utils.ask_assistant(assistant, ELASTIC_TOOL_TASK)

    similarity_check.check_similarity(response, RESPONSE_FOR_ELASTIC)


@pytest.mark.regression
@pytest.mark.parametrize(
    "db_dialect",
    sql_tools_test_data,
    ids=[f"{row}" for row in sql_tools_test_data],
)
@pytest.mark.testcase("EPMCDME-6132")
@pytest.mark.skipif(
    os.getenv("ENV") == "local", reason="Skipping this test on local environment"
)
def test_create_assistant_with_sql_tool(
    integration_utils, assistant_utils, assistant, similarity_check, db_dialect
):
    credential_values = CredentialsUtil.sql_credentials(db_dialect)
    settings = integration_utils.create_integration(
        CredentialTypes.SQL, credential_values
    )

    assistant = assistant(
        Toolkit.DATA_MANAGEMENT, DataManagementTool.SQL, settings=settings
    )

    conversation_id = str(uuid.uuid4())

    assistant_utils.ask_assistant(
        assistant, SQL_TOOL_CREATE_TABLE_TASK, conversation_id=conversation_id
    )
    assistant_utils.ask_assistant(
        assistant, SQL_TOOL_INSERT_TABLE_TASK, conversation_id=conversation_id
    )

    response = assistant_utils.ask_assistant(
        assistant, SQL_TOOL_QUERY_TABLE_TASK, conversation_id=conversation_id
    )

    assistant_utils.ask_assistant(
        assistant, SQL_TOOL_DELETE_TABLE_TASK, conversation_id=conversation_id
    )

    similarity_check.check_similarity(response, RESPONSE_FOR_SQL)
