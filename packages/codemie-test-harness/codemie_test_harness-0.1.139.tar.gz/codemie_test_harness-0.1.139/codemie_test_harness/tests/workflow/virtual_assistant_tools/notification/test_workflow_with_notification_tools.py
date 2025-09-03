import os

import pytest
from hamcrest import assert_that, equal_to

from codemie_test_harness.tests.enums.tools import NotificationTool
from codemie_test_harness.tests.test_data.notification_tools_test_data import (
    EMAIL_TOOL_PROMPT,
    EMAIL_RESPONSE,
    EMAIL_SUBJECT,
    EMAIL_BODY,
    TELEGRAM_TOOL_PROMPT,
    TELEGRAM_RESPONSE,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name


@pytest.mark.regression
@pytest.mark.tescase("EPMCDME-6652")
@pytest.mark.skipif(
    os.getenv("ENV") in ["local", "gcp"],
    reason="Skipping this test on local environment",
)
def test_workflow_with_notification_email_tool(
    workflow_with_virtual_assistant,
    similarity_check,
    workflow_utils,
    gmail_message_operator,
    email_integration,
):
    assistant_and_state_name = get_random_name()
    test_workflow = workflow_with_virtual_assistant(
        assistant_and_state_name,
        NotificationTool.EMAIL,
        integration=email_integration,
        task=EMAIL_TOOL_PROMPT,
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id, assistant_and_state_name
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
@pytest.mark.tescase("EPMCDME-6652")
def test_workflow_with_notification_telegram_tool(
    workflow_with_virtual_assistant,
    similarity_check,
    workflow_utils,
    telegram_integration,
):
    assistant_and_state_name = get_random_name()
    test_workflow = workflow_with_virtual_assistant(
        assistant_and_state_name,
        NotificationTool.TELEGRAM,
        integration=telegram_integration,
        task=TELEGRAM_TOOL_PROMPT,
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id, assistant_and_state_name
    )
    similarity_check.check_similarity(response, TELEGRAM_RESPONSE)
