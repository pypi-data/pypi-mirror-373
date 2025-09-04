import os

import pytest
from hamcrest import assert_that, equal_to

from codemie_test_harness.tests.enums.tools import Toolkit, NotificationTool
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
def test_workflow_with_email_tool(
    assistant,
    similarity_check,
    workflow_utils,
    workflow_with_assistant,
    gmail_message_operator,
    email_integration,
):
    assistant_instance = assistant(
        Toolkit.NOTIFICATION, NotificationTool.EMAIL, settings=email_integration
    )

    workflow_with_assistant_instance = workflow_with_assistant(
        assistant_instance, EMAIL_TOOL_PROMPT
    )
    response = workflow_utils.execute_workflow(
        workflow_with_assistant_instance.id, assistant_instance.name
    )
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
def test_workflow_with_telegram_tool(
    assistant,
    similarity_check,
    workflow_utils,
    workflow_with_assistant,
    telegram_integration,
):
    assistant_instance = assistant(
        Toolkit.NOTIFICATION, NotificationTool.TELEGRAM, settings=telegram_integration
    )
    workflow_with_assistant_instance = workflow_with_assistant(
        assistant_instance, TELEGRAM_TOOL_PROMPT
    )
    response = workflow_utils.execute_workflow(
        workflow_with_assistant_instance.id, assistant_instance.name
    )

    similarity_check.check_similarity(response, TELEGRAM_RESPONSE)
