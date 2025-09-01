import os

import pytest
from hamcrest import assert_that, equal_to

from codemie_sdk.models.integration import CredentialTypes
from codemie_test_harness.tests.enums.tools import Toolkit, NotificationTool
from codemie_test_harness.tests.utils.aws_parameters_store import CredentialsUtil
from codemie_test_harness.tests.test_data.notification_tools_test_data import (
    EMAIL_TOOL_PROMPT,
    EMAIL_RESPONSE,
    EMAIL_SUBJECT,
    EMAIL_BODY,
    TELEGRAM_TOOL_PROMPT,
    TELEGRAM_RESPONSE,
)


@pytest.mark.regression
@pytest.mark.skipif(
    os.getenv("ENV") in ["local", "gcp"],
    reason="Skipping this test on local environment",
)
def test_assistant_with_email_tool(
    assistant,
    assistant_utils,
    similarity_check,
    integration_utils,
    gmail_message_operator,
):
    credential_values = CredentialsUtil.gmail_credentials()
    settings = integration_utils.create_integration(
        CredentialTypes.EMAIL, credential_values
    )

    assistant = assistant(
        Toolkit.NOTIFICATION, NotificationTool.EMAIL, settings=settings
    )

    response = assistant_utils.ask_assistant(assistant, EMAIL_TOOL_PROMPT)
    similarity_check.check_similarity(response, EMAIL_RESPONSE)

    message_data = gmail_message_operator.get_messages_list()
    latest_message_id = message_data["messages"][0]["id"]
    message_content = gmail_message_operator.get_specific_message_content(
        latest_message_id
    )

    message_body = message_content["snippet"]
    message_title = next(
        (
            header["value"]
            for header in message_content["payload"]["headers"]
            if header["name"].lower() == "subject"
        )
    )

    assert_that(message_body, equal_to(EMAIL_BODY))
    assert_that(message_title, equal_to(EMAIL_SUBJECT))


@pytest.mark.regression
def test_assistant_with_telegram_tool(
    assistant, assistant_utils, similarity_check, integration_utils
):
    credential_values = CredentialsUtil.telegram_credentials()
    settings = integration_utils.create_integration(
        CredentialTypes.TELEGRAM, credential_values
    )

    assistant = assistant(
        Toolkit.NOTIFICATION, NotificationTool.TELEGRAM, settings=settings
    )

    response = assistant_utils.ask_assistant(assistant, TELEGRAM_TOOL_PROMPT)
    similarity_check.check_similarity(response, TELEGRAM_RESPONSE)
