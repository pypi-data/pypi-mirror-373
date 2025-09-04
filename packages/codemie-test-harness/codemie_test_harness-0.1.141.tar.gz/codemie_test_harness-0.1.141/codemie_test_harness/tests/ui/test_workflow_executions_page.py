"""Tests for Workflow Executions page showing detailed execution history.

This module contains UI tests for the Workflow Executions page functionality including:
- Page structure and main elements visibility
- Execution history sidebar navigation
- Main content status and metadata display
- Prompt section and interaction
- Execution states display and expansion
- Configuration sidebar functionality
- Navigation and user interactions
"""

import os

import pytest
import pytz
from tzlocal import get_localzone

from codemie_sdk.models.workflow import WorkflowMode
from codemie_test_harness.tests.ui.pageobject.workflows import WorkflowExecutionsPage
from codemie_test_harness.tests.utils.base_utils import get_random_name
from codemie_test_harness.tests.utils.yaml_utils import (
    AssistantModel,
    StateModel,
    WorkflowYamlModel,
    prepare_yaml_content,
)

assistant_and_state_name = "branch_creator"


@pytest.fixture(scope="session")
def test_workflow(workflow_utils, default_llm):
    assistant = AssistantModel(
        id=assistant_and_state_name,
        model=default_llm.base_name,
        system_prompt="You are helpful assistant",
    )

    state = StateModel(
        id=assistant_and_state_name,
        assistant_id=assistant_and_state_name,
    )

    workflow_yaml = WorkflowYamlModel(
        assistants=[assistant],
        states=[state],
    )

    yaml_content = prepare_yaml_content(workflow_yaml.model_dump(exclude_none=True))

    created_workflow = workflow_utils.create_workflow(
        workflow_name=get_random_name(),
        workflow_type=WorkflowMode.SEQUENTIAL,
        shared=True,
        workflow_yaml=yaml_content,
    )
    yield created_workflow
    workflow_utils.delete_workflow(created_workflow)


@pytest.fixture(scope="session")
def executions(test_workflow, workflow_utils):
    for _ in range(3):
        workflow_utils.execute_workflow(
            workflow=test_workflow.id,
            execution_name=assistant_and_state_name,
            user_input="Hello, please provide a greeting",
        )
    return workflow_utils.get_executions(test_workflow)


# ==================== PAGE STRUCTURE & VISIBILITY TESTS ====================


@pytest.mark.ui
def test_workflow_executions_page_structure(page, executions, test_workflow):
    """Test that all main page elements are visible and properly structured."""
    executions_page = WorkflowExecutionsPage(page)
    executions_page.navigate_to(
        test_workflow.id,
        executions[0].execution_id,
    )

    executions_page.should_be_on_workflow_executions_page()

    executions_page.should_have_all_main_sections_visible()

    executions_page.should_have_workflow_title(test_workflow.name)


@pytest.mark.ui
def test_header_elements_visibility(page, executions):
    """Test that all header elements are visible and functional."""
    executions_page = WorkflowExecutionsPage(page)
    executions_page.navigate_to(
        executions[0].workflow_id,
        executions[0].execution_id,
    )

    executions_page.should_have_header_elements_visible()

    executions_page.should_have_action_buttons_visible()


# ==================== EXECUTION HISTORY SIDEBAR TESTS ====================


@pytest.mark.ui
def test_execution_history_sidebar_content(page, executions):
    """Test execution history sidebar content and structure."""
    executions_page = WorkflowExecutionsPage(page)
    executions_page.navigate_to(
        executions[0].workflow_id,
        executions[0].execution_id,
    )

    executions_page.should_have_sidebar_visible()

    executions_page.should_have_execution_history_items()

    executions_page.should_have_active_execution_item()


@pytest.mark.ui
def test_execution_history_item_interactions(page, executions):
    """Test interactions with individual execution history items."""
    executions_page = WorkflowExecutionsPage(page)
    executions_page.navigate_to(
        executions[0].workflow_id,
        executions[0].execution_id,
    )

    first_execution = executions_page.get_first_execution_history_item()
    first_execution.should_be_visible()
    first_execution.should_have_proper_status_styling()

    first_execution.should_have_all_elements_visible()


@pytest.mark.ui
def test_execution_history_status_display(page, executions):
    """Test execution status display and styling in sidebar."""
    executions_page = WorkflowExecutionsPage(page)
    executions_page.navigate_to(
        executions[0].workflow_id,
        executions[0].execution_id,
    )

    execution_items = executions_page.get_all_execution_history_items()
    for item in execution_items[:3]:  # Test first 3 items
        item.should_be_visible()
        item.should_have_proper_status_styling()


# ==================== MAIN CONTENT STATUS & METADATA TESTS ====================


@pytest.mark.ui
def test_execution_status_and_metadata_display(page, executions):
    """Test execution status and metadata display in main content."""
    executions_page = WorkflowExecutionsPage(page)
    executions_page.navigate_to(
        executions[0].workflow_id,
        executions[0].execution_id,
    )

    executions_page.should_have_succeeded_status()

    executions_page.should_have_triggered_by(os.getenv("TEST_USER_FULL_NAME"))

    utc_created = pytz.utc.localize(executions[0].created_date)
    utc_updated = pytz.utc.localize(executions[0].updated_date)

    executions_page.should_have_started_time(
        utc_created.astimezone(get_localzone()).strftime("%m/%d/%Y, %H:%M")
    )
    executions_page.should_have_updated_time(
        utc_updated.astimezone(get_localzone()).strftime("%m/%d/%Y, %H:%M")
    )


@pytest.mark.ui
def test_execution_action_buttons(page, executions):
    """Test execution action buttons functionality."""
    executions_page = WorkflowExecutionsPage(page)
    executions_page.navigate_to(
        executions[0].workflow_id,
        executions[0].execution_id,
    )

    executions_page.should_have_action_buttons_visible()


# ==================== PROMPT SECTION TESTS ====================


@pytest.mark.ui
def test_prompt_section_display(page, executions):
    """Test prompt section display and content."""
    executions_page = WorkflowExecutionsPage(page)
    executions_page.navigate_to(
        executions[0].workflow_id,
        executions[0].execution_id,
    )

    executions_page.should_have_prompt_section_visible()

    executions_page.should_have_prompt_buttons_visible()

    executions_page.should_have_prompt_text(executions[0].prompt)


@pytest.mark.ui
def test_prompt_action_buttons(page, executions):
    """Test prompt action buttons (info, copy, download)."""
    executions_page = WorkflowExecutionsPage(page)
    executions_page.navigate_to(
        executions[0].workflow_id,
        executions[0].execution_id,
    )

    executions_page.should_have_prompt_buttons_visible()

    # Test prompt actions (these would typically trigger specific behaviors)
    # executions_page.click_prompt_copy()  # Would trigger clipboard copy
    # executions_page.click_prompt_download()  # Would trigger download


# ==================== EXECUTION STATES TESTS ====================


@pytest.mark.ui
def test_execution_states_display(page, executions):
    """Test execution states section display."""
    executions_page = WorkflowExecutionsPage(page)
    executions_page.navigate_to(
        executions[0].workflow_id,
        executions[0].execution_id,
    )

    executions_page.should_have_states_section_visible()

    executions_page.should_have_execution_states()


@pytest.mark.ui
def test_execution_state_content(page, executions):
    """Test individual execution state content and functionality."""
    executions_page = WorkflowExecutionsPage(page)
    executions_page.navigate_to(
        executions[0].workflow_id,
        executions[0].execution_id,
    )

    first_state = executions_page.get_first_execution_state()
    first_state.should_be_visible()
    first_state.should_have_main_elements_visible()


@pytest.mark.ui
def test_states_expand_collapse_functionality(page, executions):
    """Test expand/collapse functionality for states."""
    executions_page = WorkflowExecutionsPage(page)
    executions_page.navigate_to(
        executions[0].workflow_id,
        executions[0].execution_id,
    )

    executions_page.click_expand_all_states()
    first_state = executions_page.get_first_execution_state()
    first_state.should_be_expanded()

    executions_page.click_collapse_all_states()
    first_state.should_be_collapsed()


@pytest.mark.ui
def test_execution_state_output_interaction(page, executions):
    """Test execution state output interaction."""
    executions_page = WorkflowExecutionsPage(page)
    executions_page.navigate_to(
        executions[0].workflow_id,
        executions[0].execution_id,
    )

    first_state = executions_page.get_first_execution_state()
    first_state.should_be_visible()
    first_state.should_have_output_section()


# ==================== CONFIGURATION SIDEBAR TESTS ====================


@pytest.mark.ui
def test_configuration_sidebar_toggle(page, executions):
    """Test configuration sidebar toggle functionality."""
    executions_page = WorkflowExecutionsPage(page)
    executions_page.navigate_to(
        executions[0].workflow_id,
        executions[0].execution_id,
    )

    executions_page.should_have_configuration_sidebar_closed()

    executions_page.click_configuration()
    executions_page.should_have_configuration_sidebar_open()

    executions_page.click_configuration()
    executions_page.should_have_configuration_sidebar_closed()


@pytest.mark.ui
def test_configuration_sidebar_content(page, executions, test_workflow):
    """Test configuration sidebar content when open."""
    executions_page = WorkflowExecutionsPage(page)
    executions_page.navigate_to(
        executions[0].workflow_id,
        executions[0].execution_id,
    )

    executions_page.click_configuration()
    executions_page.should_have_configuration_sidebar_open()

    executions_page.should_have_workflow_info_in_sidebar(
        executions[0].workflow_id, test_workflow.name
    )


@pytest.mark.ui
def test_yaml_configuration_display(page, executions):
    """Test YAML configuration display in sidebar."""
    executions_page = WorkflowExecutionsPage(page)
    executions_page.navigate_to(
        executions[0].workflow_id,
        executions[0].execution_id,
    )

    executions_page.click_configuration()
    executions_page.should_have_configuration_sidebar_open()

    executions_page.should_have_yaml_configuration_visible()


# ==================== INTEGRATION & NAVIGATION TESTS ====================


@pytest.mark.ui
def test_execution_history_navigation(page, executions):
    """Test navigation between different executions in history."""
    executions_page = WorkflowExecutionsPage(page)
    executions_page.navigate_to(
        executions[0].workflow_id,
        executions[0].execution_id,
    )

    execution_items = executions_page.get_all_execution_history_items()
    if len(execution_items) > 1:
        execution_items[1].click()
        executions_page.should_have_active_execution_item()

        execution_items[0].click()
        executions_page.should_have_active_execution_item()


@pytest.mark.ui
def test_page_state_persistence(page, executions):
    """Test that page state persists during interactions."""
    executions_page = WorkflowExecutionsPage(page)
    executions_page.navigate_to(
        executions[0].workflow_id,
        executions[0].execution_id,
    )

    executions_page.should_preserve_state_after_interactions()
